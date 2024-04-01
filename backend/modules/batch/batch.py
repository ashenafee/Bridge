import os
import re
import sys
import time
from typing import Dict, List
import zipfile

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tqdm import tqdm

from models import Identifier

load_dotenv()

NCBI_API_KEY = os.getenv("NCBI_API_KEY")


ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi{QUERY}"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi{QUERY}"


def taxon_name_to_id(taxon_name: str) -> int:
    """
    Convert a taxon name to a taxon ID using the NCBI Taxonomy Browser API.
    """
    url = ESEARCH.format(QUERY=f"?db=taxonomy&term={taxon_name}&api_key={NCBI_API_KEY}")
    print(url)
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("Error fetching taxon ID from NCBI Taxonomy Browser.")
    return int(re.findall(r"<Id>(\d+)</Id>", r.text)[0])


def fetch_species(gene_id: List[int]) -> Dict[str, List[int]]:
    """
    Fetch species information given a gene ID using the NCBI Gene API.
    """

    species_dict = {}

    with tqdm(total=len(gene_id), desc="Fetching species", unit="Species") as pbar:
        for i, gid in enumerate(gene_id):
            url = EFETCH.format(QUERY=f"?db=gene&id={gid}&retmode=xml&api_key={NCBI_API_KEY}")
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                print(f"Error fetching species for gene {gid}.")
                print(r.text)
                raise Exception("Error fetching species from NCBI Gene.")
            
            # Convert the XML response to a BeautifulSoup object.
            soup = BeautifulSoup(r.text, "xml")

            # Get the scientific name of the species.
            species = soup.find("Org-ref_taxname").text

            # Get the taxonomy ID of the species.
            txid = soup.find("BioSource_org").find("Org-ref_db").find("Object-id_id").text

            if txid == "":
                print(f"Could not find taxonomy ID for gene {gid}.")

            # Get all gene commentary products            
            accessions = []

            # Find all "Gene-commentary_type" tags with a value of "mRNA"
            for gc in soup.find_all("Gene-commentary_type", attrs={"value": "mRNA"}):
                # Get the sibling "Gene-commentary_accession" tag
                gc_accession = gc.find_next("Gene-commentary_accession")
                if gc_accession:
                    accessions.append(gc_accession.text)
            
            # Make sure the gene_commentary_products list is unique
            accessions = list(set(accessions))
            
            if len(accessions) == 0:
                print(f"Could not find mRNA for gene {gid}.")
                continue

            # Add each gene ID and nucleotide sequence ID to the species dictionary.
            for nuc_id in accessions:
                gene_nuc_dict = {
                    "txid": txid,
                    "gene_id": gid,
                    "nuc_id": nuc_id
                }

                # Add the species to the dictionary.
                if species in species_dict:
                    species_dict[species].append(gene_nuc_dict)
                else:
                    species_dict[species] = [gene_nuc_dict]
            
            if (i + 1) % 10 == 0:
                time.sleep(1.5)
            
            pbar.update(1)
    
    return species_dict


def fetch_gene_ids(txid: int, gene_name: str) -> list:
    """
    Fetch all gene IDs for a given taxonomy and gene name using the NCBI Gene API.
    """
    url = ESEARCH.format(QUERY=f"?db=gene&term={gene_name}[Gene Name]+AND+txid{txid}[Organism:exp]&retmax=100000&api_key={NCBI_API_KEY}")
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("Error fetching gene IDs from NCBI Gene.")
        
    # The gene IDs are under eSearchResult -> IdList -> Id.
    return re.findall(r"<Id>(\d+)</Id>", r.text)


def fetch_fasta(nuc_id: str) -> str:
    """
    Fetch the FASTA sequence for a given gene ID and nucleotide ID using the NCBI Nucleotide API.
    """
    url = EFETCH.format(QUERY=f"?db=nuccore&id={nuc_id}&rettype=fasta_cds_na&retmode=text&api_key={NCBI_API_KEY}")
    r = requests.get(url)
    if r.status_code != 200:
        print("Error fetching FASTA from NCBI Nucleotide.")
        return "EMPTY"
        # raise Exception("Error fetching FASTA from NCBI Nucleotide.")
    return r.text


def modify_fasta_header(fasta: str, species: str) -> tuple:
    """
    Modify the header of a FASTA sequence to consist of the species name and
    the gene symbol.
    """
    gene_symbol = ""

    # List of failed FASTA headers.
    failed = "Failed to extract gene symbol for:\n"
    # Extract the gene symbol from the header.
    try:
        gene_symbol = re.findall(r"\[gene=(\w+)\]", fasta)[0]
    except IndexError:
        failure = f"\t {species}"
        failed += failure

    # Replace the original header with the new header.
    return f">{species} {gene_symbol}\n" + fasta.split("\n", 1)[1], failed


def write_fasta(fasta: str, filename: str, base_dir: str = "data") -> None:
    """
    Write a FASTA string to a file.
    """
    # Create the data directory if it doesn't exist.
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    with open(os.path.join(base_dir, filename), "w") as f:
        f.write(fasta)


def clear_directory(directory: str) -> None:
    """
    Clear the contents of a directory.
    """
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


def download_fasta(species_dict: Dict[str, List[Identifier]]) -> str:
    """
    Download FASTA files for each gene in a species dictionary.
    """
    # Create a directory for storing the FASTA files
    fasta_dir = os.path.join(os.getcwd(), 'fasta_files')
    os.makedirs(fasta_dir, exist_ok=True)

    # Clear the directory of any existing files
    clear_directory(fasta_dir)

    with tqdm(total=len(species_dict), desc="Downloading FASTA", unit="Species") as pbar:
        for species, gene_list in species_dict.items():
            fasta_list = []
            for gene in gene_list:
                fasta = fetch_fasta(gene.nuc_id)
                if fasta != "EMPTY" and fasta != "\n" and fasta != "" and fasta != " ":
                    # fasta, failed = modify_fasta_header(fasta, species)
                    fasta_list.append(fasta)
                    # print(failed)
            all_fasta = "\n".join(fasta_list)
            fasta_file_path = os.path.join(fasta_dir, f"{species}.fasta")
            write_fasta(all_fasta, fasta_file_path)
            pbar.update(1)

    # Create a zip file
    zip_file_path = os.path.join(fasta_dir, "fasta_files.zip")
    with zipfile.ZipFile(zip_file_path, 'w') as zip_f:
        for root, dirs, files in os.walk(fasta_dir):
            for file in files:
                if file.endswith('.fasta'):
                    zip_f.write(os.path.join(root, file), arcname=file)

    return zip_file_path


def concatenate_fasta() -> None:
    """
    Concatenate all FASTA files in the data directory into one FASTA file.
    """
    with open("data/concatenated.fasta", "w") as outfile:
        for filename in os.listdir("data"):
            if filename.endswith(".fasta"):
                with open(f"data/{filename}", "r") as f:
                    outfile.write(f.read())
    
    # Delete the files minus the concatenated file.
    for filename in os.listdir("data"):
        if filename.endswith(".fasta") and filename != "concatenated.fasta":
            os.remove(f"data/{filename}")


if __name__ == '__main__':
    # Get the taxonomy query.
    taxonomy_query = sys.argv[1]

    # Convert the taxonomy query to a taxonomy ID.
    taxonomy_id = taxon_name_to_id(taxonomy_query)
    print(f"Converted '{taxonomy_query}' to taxonomy ID {taxonomy_id}.")

    # Fetch the genes that fall under the given taxonomy ID.
    gene_name = sys.argv[2]
    gene_ids = fetch_gene_ids(taxonomy_id, 'RHO')

    # Fetch the species that each gene belongs to.
    species_ids = fetch_species(gene_ids)

    # Download the FASTA files for each gene.
    download_fasta(species_ids)
