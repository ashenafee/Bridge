import requests
from bs4 import BeautifulSoup

from blast import read_blast


def filter_summary(results: list, filter: str) -> list:
    """
    Filter the results of a summary file based on a taxonomic filter. Any
    species that belongs to that filter will be included in the returned list.
    The original results list is not modified.
    :param results: A list of strings containing the results of a BLAST search.
    :param filter: The name of the taxon to filter by.
    """
    # Loop through each line in the results and check the species lineage.
    removed = 0
    filter_upper = filter.upper()

    # Get tuples of where each entry starts and ends
    entries = []
    start = False
    lineage = None
    i1 = -1
    for i in range(len(results)):
        if start:
            if (not (results[i].startswith('\t') or
                     results[i][0] == '-' or
                     results[i].startswith('Lineage: '))) or (i == len(results) - 1):
                i2 = i
                entries.append((i1, i2, filter_upper in lineage))
                start = False

        if not (results[i].startswith('\t') or results[i][0] == '-' or
                results[i].startswith('Lineage: ')):
            start = True
            i1 = i

        if results[i].startswith('Lineage: '):
            lineage = results[i].split('Lineage: ')[1]
            lineage = lineage.split(';')
            lineage = [x.strip().upper() for x in lineage]

    # Remove entries that are not in the filter lineage
    res = []
    for entry in entries:
        if not entry[2]:
            removed += 1
        else:
            res += results[entry[0]:entry[1]]

    res.insert(0, f'Removed {removed} results not in lineage {filter}\n\n')

    return res


def filter_blast(blast_file: str, filter: str) -> list:
    """
    Filter the blast output based on a taxonomic filter.
    :param blast_file: The path to the BLAST file.
    :param filter: The name of the taxon to filter by.
    """
    # Read the results
    results = read_blast(blast_file)

    # Get the taxids
    ids = [results[x]['taxid'] for x in results]

    # Make sure the ids are unique
    ids = list(set(ids))

    # Send the request
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" \
          "db=taxonomy&id={IDS}"
    r = requests.get(url.format(IDS=",".join(ids)))

    # Map the IDs to their respective lineages
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
    :param r: The response from the NCBI taxonomy database.
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
