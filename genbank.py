import os
import time

from Bio import Entrez
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

EMAIL = os.getenv("EMAIL")
API_KEY = os.getenv("NCBI_API_KEY")


class GenBank:
    """
    A class containing methods to interact with and download GenBank records.
    """

    DOWNLOAD = "https://api.ncbi.nlm.nih.gov/datasets/v1/gene/" \
               "download?filename={FILE}"

    def __init__(self, genes: list, species: list):
        """
        Initialize a new GenBank object.
        :param genes: A list of genes to search for.
        :param species: A list of species to search for.
        """
        self.genes = genes
        self.species = species

        self.entrez = Entrez
        self.entrez.email = EMAIL
        self.entrez.api_key = API_KEY

    def search(self) -> list:
        """
        Search for the given genes in the given species.
        """
        raw_results = self._search()
        results = self._fetch(raw_results)
        return results

    def download(self, filename: str, records=None) -> None:
        """
        Download the fasta files.
        :param filename: The name of the file to save the results to.
        :param records: A list of records to download.
        """
        if filename is None:
            # Create a filename based on the genes and species.
            filename = f"{len(self.genes)}-genes-{len(self.species)}-species"

        if records is not None:
            gene_ids = self._download_from_records(records)
        else:
            gene_ids = self._download_from_summary(filename)

        # Use Biopython EFetch to download the fasta files for the genes.
        with self.entrez.efetch(db="gene", id=gene_ids, rettype="xml",
                                retmode="xml") as handle:
            # Grab the mRNA products
            mrnas = []
            records = self.entrez.parse(handle)
            for record in records:

                egene = record["Entrezgene_locus"]

                for accession in egene:
                    for entry in accession["Gene-commentary_products"]:

                        val = entry["Gene-commentary_type"].attributes["value"]
                        if val == "mRNA":
                            mrnas.append(entry["Gene-commentary_accession"])

        accessions = list(set(mrnas))

        handle.close()

        # Download the sequences
        with self.entrez.efetch(db="nuccore", id=accessions, rettype="fasta",
                                retmode="text") as handle:

            # Write the sequences to a file.
            with open(f"{filename}.fasta", "w") as f:
                f.write(handle.read())

    def _download_from_summary(self, filename) -> list:
        """
        Parse the gene IDs from the summary file.
        :param filename: The name of the file containing results to download.
        """
        # Open the summary file.
        with open(f"{filename}-summary.txt", "r") as f:
            lines = f.readlines()

        # Parse the gene IDs from the summary.
        gene_ids = [line.split()[0].strip("()") for line in lines
                    if line[1] == "("]

        # Move the summary file to the data directory.
        os.mkdir(f"./{filename}")
        os.rename(f"{filename}-summary.txt",
                  f"./{filename}/{filename}-summary.txt")

        return gene_ids

    def _download_from_records(self, records) -> list:
        """
        Parse the gene IDs from the records and return them.
        :param records: A list of records to parse.
        """
        gene_ids = []
        for record in records:
            gene_ids.append(str(record['uid']))

        return gene_ids

    def summarize(self, filename: str, records: list) -> None:
        """
        Output a summary of the given GenBank records.
        :param filename: The name of the file to save the results to.
        :param records: A list of records to summarize.
        """
        if filename is None:
            # Create a filename based on the genes and species.
            filename = f"{len(self.genes)}-genes-{len(self.species)}-species"

        summary = ""
        by_organisms = {}
        failed = []
        for i in range(len(records)):

            if records[i]['uid'] is not None:
                try:
                    by_organisms[records[i]['organism']].append(records[i])
                except KeyError:
                    by_organisms[records[i]['organism']] = [records[i]]
            else:
                failed.append(records[i])

        # Summarize the successful records.
        summary = self._summarize_success(by_organisms, summary)

        # Summarize the failed records.
        summary = self._summarize_failed(failed, summary)

        with open(f"{filename}-summary.txt", "w") as f:
            f.write(summary)

    def _summarize_success(self, by_organisms: dict, summary: str) -> str:
        """
        Summarize the successful GenBank records.
        :param by_organisms: A dictionary of records by organism.
        :param summary: The summary string to append to.
        """
        for organism in by_organisms:
            summary += f"{organism}\n"
            summary += f"Lineage: {by_organisms[organism][0]['lineage']}\n"
            summary += "-" * 80 + "\n"
            for record in by_organisms[organism]:
                summary += f"\t({record['uid']}) {record['symbol']}\n"
                summary += f"\t{record['description']}\n"
                summary += "-" * 80 + "\n"
        return summary

    def _summarize_failed(self, failed: list, summary: str) -> str:
        """
        Summarize the failed GenBank records.
        :param failed: A list of failed records.
        :param summary: The summary string to append to.
        """
        if len(failed) > 0:
            summary += "Failed to find the following genes:\n"
            for record in failed:
                summary += f"\t{record['gene_input']} " \
                           f"{record['organism_input']}\n"
        return summary

    def _search(self) -> list:
        """
        Use Biopython's ESearch module to query GenBank.
        """
        results = []
        for species in tqdm(self.species,
                            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} '
                                       'species have been examined.'):
            for gene in self.genes:
                handle = self.entrez.esearch(db="gene",
                                             term=f"{gene}[GENE] AND "
                                                  f"{species}[ORGN]")
                record = self.entrez.read(handle)

                # If the gene was not found, add a default value to the results.
                if record['Count'] == '0':
                    results.append({
                        'uid': None,
                        'gene_input': gene,
                        'organism_input': species
                    })
                else:
                    results.append({
                        'uid': record['IdList'][0],
                        'gene_input': gene,
                        'organism_input': species
                    })
                handle.close()
        return results

    def _fetch(self, raw: list) -> list:
        """
        Use Biopython's EFetch module to fetch the GenBank records.
        :param raw: The raw results from the ESearch module.
        """
        results = []

        # Set a cooldown to prevent being rate-limited.
        if len(raw) > 500:
            cooldown = 2
        else:
            cooldown = 1

        for result in tqdm(raw, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'
                                           ' records have been fetched.'):
            if result['uid'] is None:
                results.append(result)
            else:
                handle = self.entrez.efetch(db="gene", id=result['uid'],
                                            retmode="xml")
                self._parse_record(self.entrez.read(handle)[0])
                results.append(self.record)
                handle.close()
            time.sleep(cooldown)
        return results

    def _parse_record(self, record) -> None:
        """
        Parse the GenBank record for the desired information.
        """
        # Try to get the description, if it exists.
        try:
            desc = record['Entrezgene_summary']
        except KeyError:
            desc = None

        lineage_info = record['Entrezgene_source']['BioSource'] \
            ['BioSource_org']
        organism = lineage_info['Org-ref']['Org-ref_taxname']
        lineage = lineage_info['Org-ref']['Org-ref_orgname']['OrgName'] \
            ['OrgName_lineage']

        gene_info = record['Entrezgene_gene']['Gene-ref']
        gene = gene_info['Gene-ref_locus']

        # Try to get the name, synonyms, and gene ID, if they exist.
        try:
            name = gene_info['Gene-ref_desc']
        except KeyError:
            name = None
        try:
            synonyms = gene_info['Gene-ref_syn']
        except KeyError:
            synonyms = None
        try:
            gid = record['Entrezgene_locus'][0]['Gene-commentary_products'] \
                [0]['Gene-commentary_accession']
        except KeyError:
            gid = None

        self.record = {
            'uid': record['Entrezgene_track-info']['Gene-track']
            ['Gene-track_geneid'],
            'gid': gid,
            'name': name,
            'symbol': gene,
            'synonyms': synonyms,
            'description': desc,
            'organism': organism,
            'lineage': lineage
        }


class GenBankDDL:
    """
    A class for downloading sequence data, given a list of GenBank records.
    """

    def __init__(self, records: list):
        """
        Initialize the direct-download class.
        :param records: A list of GenBank records.
        """
        self.records = records
        self.entrez = Entrez
        self.entrez.email = EMAIL
        self.entrez.api_key = API_KEY

    def download(self, filename: str) -> None:
        """
        Download the GenBank records using Biopython's EFetch module.
        :param filename: The name of the file to save the records to.
        """
        for record in tqdm(self.records, bar_format='{l_bar}{bar}| {n_fmt}/'
                                                    '{total_fmt} records have '
                                                    'been downloaded.'):
            handle = self.entrez.efetch(db="nucleotide", id=record,
                                        rettype="fasta", retmode="text")

            with open(f"{filename}.fasta", "a") as f:
                f.write(handle.read())

            handle.close()

            time.sleep(0.20)

        print(f"Downloaded {len(self.records)} records to {filename}.fasta.")
