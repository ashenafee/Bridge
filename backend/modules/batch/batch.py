# 1. Get the ID of the taxonomy query input.
# 2. Fetch a list of all species in the taxonomy.
# 3. Create a list of gene identifiers for each species' copy of the given gene.


import sys
import os
import re
import time
import json
from typing import Dict, List
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv


load_dotenv()

NCBI_API_KEY = os.getenv("NCBI_API_KEY")


ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi{QUERY}"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi{QUERY}"


def taxon_name_to_id(taxon_name: str) -> int:
    """
    Convert a taxon name to a taxon ID using the NCBI Taxonomy Browser API.
    """
    url = ESEARCH.format(QUERY=f"?db=taxonomy&term={taxon_name}")
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
            r = requests.get(url)
            if r.status_code != 200:
                raise Exception("Error fetching species from NCBI Gene.")
            
            # Convert the XML response to a BeautifulSoup object.
            soup = BeautifulSoup(r.text, "xml")

            # Get the scientific name of the species.
            species = soup.find("Org-ref_taxname").text

            # Get the nucleotide sequence ID.
            nuc_id = soup.find("Gene-commentary_products").find("Gene-commentary_accession").text

            # Create a dictionary of the gene ID and the nucleotide sequence ID.
            gene_nuc_dict = {
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


def write_fasta(fasta: str, filename: str, base_dir: str = "data") -> None:
    """
    Write a FASTA string to a file.
    """

    # Create the data directory if it doesn't exist.
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    with open(os.path.join(base_dir, filename), "w") as f:
        f.write(fasta)


def download_fasta(species_dict: Dict[str, List[int]]) -> None:
    """
    Download FASTA files for each gene in a species dictionary.
    """
    for species, gene_list in species_dict.items():
        for gene in gene_list:
            fasta = fetch_fasta(gene["nuc_id"])
            write_fasta(fasta, f"{species}_{gene['gene_id']}.fasta")


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
