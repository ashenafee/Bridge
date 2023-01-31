import subprocess

from Bio import SearchIO
from Bio.Blast.Applications import NcbiblastnCommandline
import requests
from bs4 import BeautifulSoup

from genbank import GenBank


def blastn(query, db='nt', out="blastn.out.txt", ms=100, ev=0.05, ws=11, rw=2,
           pn=-3, go=5, ge=2, tl=18, tt='coding') -> None:
    """
    Run a blastn search on the given query.
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
    # TODO: Add permissible values for the parameters given above.

    # if not out.endswith(".xml"):
    #     out = out + ".xml"
    blastn_cline = NcbiblastnCommandline(query=query,
                                         db=db,
                                         task='dc-megablast',
                                         remote=True,
                                         outfmt='6 std staxid',
                                         out=out,   # Output file
                                         max_target_seqs=ms,    # Num of results
                                         evalue=ev,  # E-value threshold
                                         word_size=ws,  # Word size
                                         reward=rw,  # Reward
                                         penalty=pn,  # Penalty
                                         gapopen=go,  # Gap open
                                         gapextend=ge,  # Gap extend
                                         template_length=tl,    # Template len
                                         template_type=tt,  # Template type
                                         )
    subprocess.call(str(blastn_cline), shell=True)


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


def blast_by_species_and_symbol(species: str, symbol: str) -> None:
    """
    Run a BLAST search by downloading the sequence for the given symbol and
    species.
    :param species:
    :param symbol:
    :return:
    """
    # TODO: Complete this function.

    # Search for the symbol in the GenBank database
    gb = GenBank([species], [symbol])
    data = gb.search()
    gb.download(filename="", records=data)
    print("Done!")

if __name__ == "__main__":
    # TODO: Filter for only the results that are in the lineage of interest.
    blastn("test-anolis_carolinensis.fasta")
    import json
    blast_records = read_blast("blastn.out.txt")
    # TODO: Allow user to specify returned sequences amount
    ids = [blast_records[x]['taxid'] for x in blast_records]

    filter_blast(blast_records, "Anolis")
    #blast_by_species_and_symbol("Anolis carolinensis", "RHO")

    # TODO: Dirty taxonomy and output taxonomy on the tree (like a snapshot)
    # TODO: Checkbox for excluding certain data points
    # Accession, gene name, species, family, class
    # TODO: Figure out tree program from BLAST
    # Figtree
    # https://biopython.org/docs/1.76/api/Bio.Align.Applications.html#module-Bio.Align.Applications