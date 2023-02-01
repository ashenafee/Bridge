from blast import read_blast
import requests


#def filter_blast(blast_file, taxid_file, out_file):


# The genbank.py summarize script uses lineage information for each species.
# This information (likely) comes from a dictionary fetched when getting info
# on each gene.
#
# To create a filter function, one can simply loop through the results and their
# respective lineages, and if a name in the lineage matches the filter, that
# entire result can be added to the filtered list.
#
# Example: If we have results from Species A, Species B, Species C, and Species
#          D, consider we filter for Taxonomy X. Let's say that Species A and
#          Species D fall within Taxonomy X. Then, running the filter function
#          would return a list with Species A and Species D. Species B and
#          Species C would be excluded.

def filter(results: list, filter: str) -> list:
    """
    Filter the results based off a taxonomic filter. Results for which the
    species falls under the filter (i.e., that species is a member of that
    taxon) will be included in the returned list. No information is modified
    in the original results list.
    :param results:
    :param filter:
    :return:
    """
    filtered = []
    for result in results:
        if filter in result['lineage']:
            filtered.append(result)
    return filtered


# def filter_summary(results: list, filter: str) -> list:
#     """
#     Filter the results found in a summary file.
#     :param results:
#     :param filter:
#     :return:
#     """
#     # Loop through each line in the results and check the species lineage.
#     lines = results[:]
#     removed = 0
#     filter_upper = filter.upper()
#
#     lineage = []
#     i = 0
#
#     while i < len(results):
#         line = lines[i]
#         if line.startswith('Lineage: '):
#             lineage = line.split('Lineage: ')[1]
#             lineage = lineage.split(';')
#             lineage = [x.strip().upper() for x in lineage]
#
#         if line.startswith('\t'):
#             # This is a result line
#             if filter_upper not in lineage:
#                 # This result is not in the filter lineage
#                 lines.pop(i - 1)
#                 lines.pop(i - 1)
#                 lines.pop(i - 1)
#
#                 removed += 3
#                 i -= 3
#
#         if line.startswith('Failed'):
#             break
#
#         i += 1
#
#     # Remove empty lines
#     lines = [x for x in lines if x != '']
#
#     # Add the number of removed results to the top of the file
#     lines.insert(0, f'Removed {removed} results not in lineage {filter}\n')
#
#     return lines

def filter_summary(results: list, filter: str) -> list:
    """

    :param results:
    :param filter:
    :return:
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

        if not (results[i].startswith('\t') or results[i][0] == '-' or results[i].startswith('Lineage: ')):
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


def filter_blast(blast_output: str, filter: str) -> list:
    """
    Filter the blast output based on a taxonomic filter.
    :param blast_output:
    :return:
    """
    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=taxonomy&id=38937,28377
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" \
          "db=taxonomy&id={IDS}"

    # Send the request
    r = requests.get(url)

    # Get the results from the blast output
    results = read_blast(blast_output)


if __name__ == '__main__':
    # # Read in emily's summary
    # with open('emily-summary.txt', 'r') as f:
    #     emily = f.readlines()
    #
    # l = filter_summary(emily, 'Bovidae')
    # with open('emily-filtered.txt', 'w') as f:
    #     f.writelines(l)

    # Read in the BLAST results
    with open('blastn.out.txt', 'r') as f:
        blast = f.readlines()

