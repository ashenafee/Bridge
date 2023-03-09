import shutil
import subprocess
from time import sleep

from Bio import SearchIO
from Bio.Blast.Applications import NcbiblastnCommandline
import requests
from bs4 import BeautifulSoup

from genbank import GenBank, GenBankDDL
from threading import Thread
from tqdm import tqdm


def blastn(query, params={}, db='nt', out="blastn.out.txt", ms=100, ev=0.05,
           ws=11, rw=2, pn=-3, go=5, ge=2, tl=18, tt='coding') -> None:
    """
    Run a blastn search on the given query.
    :param params: The parameters to use for the BLAST search.
    :param query: The query file.
    :param db: The database to search.
    :param out: The output file.
    :param ms: The maximum amount of target sequences to return.
    :param ev: The e-value threshold.
    :param ws: The word size.
    :param rw: The reward for a match.
    :param pn: The penalty for a mismatch.
    :param go: The gap opening cost.
    :param ge: The gap extension cost.
    :param tl: The template length.
    :param tt: The template type.
    :return:
    """
    # Setup parameters    
    blastn_cline = NcbiblastnCommandline(query=query,
                                        db=db,
                                        task='dc-megablast',
                                        remote=True,
                                        outfmt='6 std staxid',
                                        out=out,
                                        max_target_seqs=ms,
                                        evalue=ev,
                                        word_size=ws,
                                        reward=rw,
                                        penalty=pn,
                                        gapopen=go,
                                        gapextend=ge,
                                        template_length=tl,
                                        template_type=tt,
                                        )
    blastn_cline = _setup_blast_params(blastn_cline, params)

    # Create a new thread
    t = Thread(target=_blast_thread, args=(blastn_cline,))
    t.start()

    # Show a progress bar
    pbar = tqdm(bar_format='[BLAST] - Time elapsed:\t{elapsed}',)

    # Update the progress bar
    while t.is_alive():
        pbar.update(1)
        sleep(1)
    
    # Close the progress bar
    pbar.close()
    t.join()

    # Download the BLAST results on a separate thread
    t = Thread(target=_download_blast_results, args=(out,))
    t.start()

    # Show a progress bar
    pbar = tqdm(bar_format='[DOWNLOAD] - Time elapsed:\t{elapsed}',)

    # Update the progress bar
    while t.is_alive():
        pbar.update(1)
        sleep(1)
    
    # Close the progress bar
    pbar.close()
    t.join()


def _download_blast_results(out):
    """
    Download the BLAST results.
    """
    # Open the BLAST results
    with open(out, 'r') as f:
        lines = f.readlines()
    
    # Get the accessions of the results
    accessions = [line.split(' ')[1] for line in lines]

    # Use Biopython's Entrez module to download the sequences
    gb = GenBankDDL(records=accessions)
    gb.download(f'{out}.fasta')
    


def _blast_thread(blastn: NcbiblastnCommandline):
    """
    Thread to run the BLAST search.
    :return:
    """
    subprocess.call(str(blastn), shell=True)


def _setup_blast_params(executable, params: dict) -> NcbiblastnCommandline:
    """
    Setup the BLAST parameters.
    :param params:
    :return:
    """

    # Try to turn numbers into integers
    for x in params:
        try:
            params[x] = int(params[x])
        except ValueError:
            pass

    for x, y in params.items():
        setattr(executable, x, y)
    
    return executable


def read_blast(blast_file) -> dict:
    """
    Read the blast file.
    :param blast_file:
    :return:
    """
    results = SearchIO.read(blast_file, 'blast-tab', fields=['std', 'staxid'])
    results_raw = open(blast_file, 'r').readlines()

    # Parse the taxids into a dictionary
    parsed = {}
    for i in range(len(results)):
        result = results[i]
        parsed[result.id] = {
            'fragments': result.fragments,
            'hsps': result.hsps,
            'taxid': results_raw[i].split('\t')[-1].strip()
        }

    return parsed


def filter_blast(results: dict, filter: str) -> list:
    """
    Filter the results of a BLAST search based off the taxonomic filter
    supplied by the user.
    :param results:
    :param filter:
    :return:
    """
    # TODO: Filter multiple FASTA file entry
    # Get the IDs from the BLAST results
    ids = [results[x]['taxid'] for x in results]

    # Make sure it's only unique IDs
    ids = list(set(ids))

    # Send the request
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" \
          "db=taxonomy&id={IDS}"
    r = requests.get(url.format(IDS=",".join(ids)))

    tax_map = _map_id_to_lineage(r)

    # Filter the results
    filtered = []
    for result in results:
        taxid = results[result]['taxid']
        lineage = tax_map[taxid]
        if filter in lineage:
            filtered.append(result)

    return filtered


def _map_id_to_lineage(r: requests.Response) -> dict:
    """
    Given the response from the NCBI taxonomy database, map the IDs to their
    respective lineages.
    :param r:
    :return:
    """
    # Parse the XML results using BeautifulSoup
    soup = BeautifulSoup(r.text, features='xml')
    # Remove all of 'LineageEx'
    for x in soup.find_all('LineageEx'):
        x.decompose()
    # Get taxids and lineages
    taxa = soup.findAll('Taxon')
    # Build the map of tax ID to lineage
    tax_map = {}
    for taxon in taxa:
        tax_map[taxon.TaxId.text] = taxon.Lineage.text.split('; ')

    return tax_map


def blast_by_species_and_symbol(species: list, symbol: list, 
                                output: str) -> None:
    """
    Run a BLAST search by downloading the sequence for the given symbol and
    species.
    :param species:
    :param symbol:
    :return:
    """
    # TODO: Complete this function.

    # Search for the symbol in the GenBank database
    gb = GenBank(symbol, species)
    data = gb.search()

    # Download the sequence
    gb.download(filename="btemp", records=data)

    # Run the BLAST search
    blastn('./btemp/btemp-rna.fasta', out=output)

    # Delete the temporary folder
    shutil.rmtree('./btemp')

    # TODO: Download BLAST results

if __name__ == "__main__":
    # Run the BLAST search
    blastn('homo_rho.fasta')

    # Read the results
    blast_records = read_blast("blastn.out.txt")
    ids = [blast_records[x]['taxid'] for x in blast_records]
    filtered = filter_blast(blast_records, "Phocidae")

    # Download the filtered sequences
    gb = GenBankDDL(records=filtered)
    gb.download(filename="test")

    # TODO: Dirty taxonomy and output taxonomy on the tree (like a snapshot)
    # TODO: Checkbox for excluding certain data points
    # Accession, gene name, species, family, class
    # TODO: Figure out tree program from BLAST
    # Figtree
    # https://biopython.org/docs/1.76/api/Bio.Align.Applications.html#module-Bio.Align.Applications