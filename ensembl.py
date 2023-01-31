import json
import time
import re

import requests
from bs4 import BeautifulSoup


class EMBLFile:
    """
    Fetch information on an accession file containing values from Ensembl.
    """

    def __init__(self, filename: str) -> None:
        """
        Initialize a new EMBLFile class.
        :param filename:
        """
        self.filename = filename

        self._species_table = None
        self._fetch_species_table()

    def _fetch_species_table(self) -> None:
        """
        Fetch the latest version of the Ensembl species table from the database.
        """
        # https://www.ensembl.org/info/genome/stable_ids/prefixes.html
        url = 'https://www.ensembl.org/info/genome/stable_ids/prefixes.html'
        r = requests.get(url)

        # Parse the HTML table.
        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find('table', {'class': 'ss'})

        # Extract the table rows.
        species_table = {}
        for row in table.find_all('tr'):
            temp = [x.text for x in row.find_all('td')]
            if len(temp) != 0:
                species_table[temp[0]] = temp[1]

        self._species_table = species_table

    def get_information(self) -> dict:
        """
        Return information on each accession provided in self.filename.
        :return:
        """
        with open(self.filename, 'r') as f:
            accessions = f.read().splitlines()

        # Filter out the dividers and the initial header character.
        accessions = [x[1:] for x in accessions if x[0] == '>']

        # Compare each accession to the species table.
        results = {}
        for accession in accessions:
            # Get the prefix before the numbers
            prefix = re.search(r'^[A-Z]+', accession).group(0)

            # Check if the prefix minus the last character is in the table.
            if prefix[:-1] in self._species_table:
                species = self._species_table[prefix[:-1]]
            elif prefix[:-2] in self._species_table:
                species = self._species_table[prefix[:-2]]
            # If the species is not in the table, it is not a valid accession.
            else:
                species = 'Unknown'

            # Add the species to the results.
            results[accession] = species

        return results


class Ensembl:
    """
    A class containing methods to interact with and download Ensembl records.
    """

    LOOKUP = "http://rest.ensembl.org/lookup/symbol/{SPECIES}/{GENE}" \
             "?content-type=application/json;expand=1"
    LOOKUP_ACC = "http://rest.ensembl.org/lookup/id"
    SEQUENCE2 = "http://rest.ensembl.org/sequence/region/{SPECIES}"
    SEQUENCE = "http://rest.ensembl.org/sequence/id"

    def __init__(self, genes=None, species=None) -> None:
        """
        Initialize a new Ensembl object.
        :param genes:
        :param species:
        """
        if genes is not None and species is not None:
            self.genes = genes
            self.species = species
        else:
            self.genes = []
            self.species = []
            self.accessions = None

        self._acc_seq = False

    def search(self) -> list:
        """
        Search for the given genes in the given species.
        :return:
        """
        raw_results = self._search()
        results = self._fetch(raw_results)
        return results

    def search_by_alignment(self, alignment: str, seq: bool) -> list:
        """
        Search for the sequences given by the alignment file in the Ensembl
        database. If seq is True, return the sequences. Otherwise, return the
        descriptions and metadata of these accessions.
        :param alignment:
        :param seq:
        :return:
        """
        if seq:
            self._acc_seq = True

        # Parse the file
        with open(alignment, "r") as f:
            lines = f.readlines()
        self.accessions = [line.strip()[1:] for line in lines if
                           line.startswith(">")]
        results = self._search()

        # Re-annotate the alignment file
        re_ann = ""
        for result in results[0]:
            re_ann += f">{result} ({results[0][result]['species']})\n"
            # Split the sequence into 80 character lines.
            seq = results[0][result]["sequence"]
            seq = [seq[i:i + 80] for i in range(0, len(seq), 80)]
            re_ann += "\n".join(seq) + "\n"
        with open(f"{alignment.split('.')[0]}-searched.fasta", "w") as f:
            f.write(re_ann)

        return results

    def _search(self) -> list:
        """
        Search for the given genes in the given species.
        :return:
        """
        results = []

        if self.species:
            for species in self.species:
                for gene in self.genes:
                    # Fetch the record from Ensembl.
                    record = self.LOOKUP.format(SPECIES=species.replace(" ", "_"),
                                                GENE=gene)
                    r = requests.get(record)
                    if r.status_code == 200:
                        results.append(r.json())
                    else:
                        print("Error finding the gene.")
        else:

            accessions = [self.accessions[i:i + 100]
                          for i in range(0, len(self.accessions), 100)]

            for accession in accessions:
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                data = {"ids": accession}
                start_time = time.time()
                r = requests.post(self.LOOKUP_ACC,
                                  headers=headers,
                                  data=json.dumps(data))
                print(f"Time taken: {time.time() - start_time}")

                if r.status_code == 200:
                    results.append(r.json())
                    # TODO: Message where if certain features aren't found,
                    # display that to the user.
                else:
                    print("Error finding the gene(s).")
                time.sleep(1)

            if self._acc_seq:
                self._get_acc_seqs(results)

        return results

    def _get_acc_seqs(self, results) -> None:
        """
        Get the sequences for the accessions.
        :param results:
        :return:
        """
        accessions_seq = [self.accessions[i:i + 50]
                          for i in range(0, len(self.accessions), 50)]
        for accession in accessions_seq:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            data = {"ids": accession}
            r = requests.post(self.SEQUENCE,
                              headers=headers,
                              data=json.dumps(data))

            if r.status_code == 200:
                # Go through the results and add them to the
                # respective entry.
                for result in r.json():
                    results[0][result["id"]]["sequence"] = result["seq"]

    def _fetch(self, raw: list) -> list:
        """
        Fetch the records for the raw results.
        :param raw:
        :return:
        """
        results = []
        for record in raw:
            parsed = self._parse(record)
            results.append(parsed)
        return results

    def _parse(self, record: dict) -> dict:
        """
        Parse the record.
        :param record:
        :return:
        """
        result = {
            "id": record["canonical_transcript"],
            "species": record["species"],
            "description": record["description"],
            "type": record["biotype"]
        }
        return result

    def download(self, filename: str, records=None) -> None:
        """
        Download the fasta files.
        :return:
        """
        if records is not None:
            # Create a dictionary of species to genes.
            species = self._species_to_genes(records)
        else:
            with open(f"{filename}-summary.txt", "r") as f:
                lines = f.readlines()
            species = self._species_to_genes_file(lines)

        # Get attributes for the POST request
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        fasta_headers = self._get_headers(species)

        for organism in species:
            # Make the POST request.
            data = {
                "ids": [f"{gene[0].split('.')[0]}"
                        for gene in species[organism]],
                "format": "fasta",
                "type": "cds"
            }
            r = requests.post(self.SEQUENCE,
                              headers=headers,
                              data=json.dumps(data))
            if r.status_code == 200:
                # Parse the results.
                results = self._parse_fasta(r.json(), headers=fasta_headers)
                with open(f"{filename}-{organism}.fasta", "w") as f:
                    f.write(results)
            else:
                # TODO: Error message
                print("Could not download the sequences. Make sure the values "
                      "are valid Ensembl sequence IDs.")

    def _species_to_genes(self, records: list) -> dict:
        """
        Return a dictionary of species mapped to their genes-of-interest.
        :param records:
        :return:
        """
        species = {}
        for record in records:
            if record["species"] not in species:
                species[record["species"]] = [(record["id"], record["description"])]
            else:
                species[record["species"]].append((record["id"], record["description"]))
        return species

    def _species_to_genes_file(self, lines: list) -> dict:
        """
        Return a dictionary of species mapped to their genes-of-interest from
        a summary file.
        :param lines:
        :return:
        """
        species = {}
        divider = "-" * 80
        curr_species = None
        for line in lines:
            if (divider not in line) and (not line.startswith("\t")) and \
                    (line != "\n"):
                species[line.strip()] = []
                curr_species = line.strip()
            elif line.startswith("\t("):
                info = (line[2:line.index(")")], line[line.index(")") + 1:].strip())
                species[curr_species].append(info)
        return species

    def _get_headers(self, organisms: dict) -> dict:
        """
        Get the FASTA headers for the POST request.
        :param records:
        :return:
        """
        headers = {}
        for organism in organisms:
            for gene in organisms[organism]:
                headers[gene[0].split('.')[0]] = \
                    f"> {organism}: {gene[0]} - {gene[1]}"
        return headers

    def _parse_fasta(self, results: list, headers=None) -> str:
        """
        Parse the results into a single FASTA file.
        :param results:
        :param headers:
        :return:
        """
        fasta = ""
        if headers is not None:
            for result in results:
                # Split the sequence into 80 character chunks.
                sequence = result["seq"]
                chunks = [sequence[i:i + 80] for i in range(0, len(sequence), 80)]
                sequence = "\n".join(chunks)
                fasta += f"{headers[result['id']]}\n{sequence}\n\n"
        else:
            for result in results:
                # Split the sequence into 80 character chunks.
                sequence = result["seq"]
                chunks = [sequence[i:i + 80] for i in range(0, len(sequence), 80)]
                sequence = "\n".join(chunks)
                fasta += f">{result['id']}\n{sequence}\n\n"
        return fasta

    def summarize(self, results: list, filename: str) -> None:
        """
        Summarize the downloaded files.
        :return:
        """
        # Create a dictionary of species to genes.
        species = {}
        for result in results:
            if result["species"] not in species:
                species[result["species"]] = [(result["id"], result["description"])]
            else:
                species[result["species"]].append((result["id"], result["description"]))

        # Create the summary string.
        summary = ""
        for specie in species:
            summary += f"{specie}\n"
            summary += "-" * 80 + "\n"
            for gene in species[specie]:
                summary += f"\t({gene[0]}) {gene[1]}\n"
            summary += "\n"

        with open(f"{filename}-summary.txt", 'w') as f:
            f.write(summary)


if __name__ == '__main__':
    #ensembl = Ensembl(species=["anolis carolinensis"], genes=["TRPA1"])
    #results = ensembl.search()
    #ensembl.summarize(results, "test")
    #ensembl.download('test')
    #ensembl = Ensembl()
    #res = ensembl.search_by_alignment('6_documents_align.fasta', True)

    #with open('test.json', 'w') as f:
    #    f.write(json.dumps(res, indent=4))

    embl = EMBLFile('6_documents_align.fasta')
    print(json.dumps(embl.get_information(), indent=4))
