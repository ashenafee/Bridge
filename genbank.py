import os

import requests
from Bio import Entrez
from dotenv import load_dotenv
from tqdm import tqdm
import time
import zipfile
import shutil

load_dotenv()

EMAIL = os.getenv("EMAIL")
API_KEY = os.getenv("NCBI_API_KEY")


class GenBank:
    """
    A class containing methods to interact with and download GenBank records.
    """

    DOWNLOAD = "https://api.ncbi.nlm.nih.gov/datasets/v1/gene/" \
               "download?filename={FILE}"

    def __init__(self, genes: list, species: list) -> None:
        """
        Initialize a new GenBank object.
        """
        self.genes = genes
        self.species = species

        self.entrez = Entrez
        self.entrez.email = EMAIL
        self.entrez.api_key = API_KEY

    def search(self) -> list:
        """
        Search for the given genes in the given species.
        :return:
        """
        raw_results = self._search()
        results = self._fetch(raw_results)
        return results

    def download(self, filename: str, records=None) -> None:
        """
        Download the fasta files.
        :return:
        """

        if records is not None:
            gene_ids = self._download_from_records(records)
        else:
            gene_ids = self._download_from_summary(filename)

        data = {
            "gene_ids": gene_ids,
            "include_annotation_type": ["FASTA_GENE",
                                        "FASTA_RNA",
                                        "FASTA_PROTEIN"]
        }
        r = requests.post(self.DOWNLOAD.format(FILE=filename), json=data)
        if r.status_code == 200:
            with open(f"{filename}.zip", 'wb') as f:
                f.write(r.content)
            
            # Get absolute path to the file.
            path = os.path.abspath(f"{filename}.zip")

            # Create temporary directory.
            os.mkdir("./temp")

            # Unzip the file.
            with zipfile.ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall("./temp")

            # Delete the zip file.
            os.remove(path)

            # Get current working directory.
            cwd = os.getcwd()
            dl_data = cwd + "/temp/ncbi_dataset/data"

            # Create the data directory if it doesn't exist.
            if os.path.exists(f"{cwd}/{filename}") is False:
                os.mkdir(f"./{filename}")

            # Move the files to the data directory.
            save = cwd + f"/{filename}/{filename}"
            os.rename(f"{dl_data}/gene.fna", f"{save}-gene.fasta")
            os.rename(f"{dl_data}/rna.fna", f"{save}-rna.fasta")
            os.rename(f"{dl_data}/protein.faa", f"{save}-protein.fasta")

            # Remove any non "NM" entries from rna.fasta
            with open(f"{save}-rna.fasta", "r") as f:
                lines = f.readlines()
            
            transcript = ""
            begin = False
            for line in lines:
                if line[1] == 'N' and line[2] == 'M':
                    begin = True
                else:
                    if line[0] == ">":
                        begin = False
                
                if begin:
                    transcript += line
            
            with open(f"{save}-rna.fasta", "w") as f:
                f.write(transcript)


            # Delete the directory.
            shutil.rmtree("./temp")

        else:
            print(r.status_code)

    def _download_from_summary(self, filename) -> list:
        """
        Parse the gene IDs from the summary file.
        :param filename:
        :return:
        """
        # Open the summary file.
        with open(f"{filename}-summary.txt", "r") as f:
            lines = f.readlines()

        # Parse the gene IDs from the summary.
        gene_ids = [line.split()[0].strip("()") for line in lines
                    if line[1] == "("]
        
        # Move the summary file to the data directory.
        os.mkdir(f"./{filename}")
        os.rename(f"{filename}-summary.txt", f"./{filename}/{filename}-summary.txt")

        return gene_ids

    def _download_from_records(self, records) -> list:
        """
        Parse the gene IDs from the records and return them.
        :param records:
        :return:
        """
        gene_ids = []
        for record in records:
            gene_ids.append(str(record['uid']))

        return gene_ids

    def summarize(self, filename: str, records: list) -> None:
        """
        Output a summary of the given GenBank records.
        :return:
        """
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

        summary = self._summarize_success(by_organisms, summary)
        summary = self._summarize_failed(failed, summary)

        with open(f"{filename}-summary.txt", "w") as f:
            f.write(summary)

    def _summarize_success(self, by_organisms, summary) -> str:
        """
        Summarize the successful GenBank records.
        :param by_organisms:
        :param summary:
        :return:
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

    def _summarize_failed(self, failed, summary) -> str:
        """
        Summarize the failed GenBank records.
        :param failed:
        :param summary:
        :return:
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
        :return:
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
        :return:
        """
        results = []

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
        :return:
        """
        try:
            desc = record['Entrezgene_summary']
        except KeyError:
            desc = None
        lineage_info = record['Entrezgene_source']['BioSource']\
        ['BioSource_org']
        organism = lineage_info['Org-ref']['Org-ref_taxname']
        lineage = lineage_info['Org-ref']['Org-ref_orgname']['OrgName']\
        ['OrgName_lineage']

        gene_info = record['Entrezgene_gene']['Gene-ref']
        gene = gene_info['Gene-ref_locus']
        try:
            name = gene_info['Gene-ref_desc']
        except KeyError:
            name = None
        try:
            synonyms = gene_info['Gene-ref_syn']
        except KeyError:
            synonyms = None
        try:
            gid = record['Entrezgene_locus'][0]['Gene-commentary_products']\
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
        self.records = records
        self.entrez = Entrez
        self.entrez.email = EMAIL
        self.entrez.api_key = API_KEY

    def download(self, filename: str) -> None:
        """
        Download the GenBank records.
        :param filename:
        :return:
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


if __name__ == '__main__':
    from argparse import ArgumentParser

    title = ""
    with open('title.txt') as f:
        title = '\n'.join([line.strip() for line in f.readlines()])

    print()
    print(title)
    print()

    def set_emily():
        return True

    def set_short():
        return True

    parser = ArgumentParser(description="Bridge: GenBank Module")
    parser.add_argument('-EMILY',
                        dest='emily',
                        action="store_const",
                        const=True,
                        default=False,
                        help='Use Emily\'s dataset for debugging.')
    parser.add_argument('-SHORT',
                        dest='short',
                        action="store_const",
                        const=True,
                        default=False,
                        help='Use a short dataset for debugging.')

    species = ["Homo sapiens"]
    genes = ["RHO"]

    args = parser.parse_args()

    if args.emily:
        with open("emily-species.txt", "r") as f:
            species = [line.strip() for line in f.readlines()]
            f.close()

        with open("emily-genes.txt", "r") as f:
            genes = [line.strip() for line in f.readlines()]
            f.close()

        gb = GenBank(genes, species)
        data = gb.search()
        gb.summarize("emily-test-2", data)
        gb.download("emily-test-2")

    if args.short:
        with open("testfiles/short-species.txt", "r") as f:
            species = [line.strip() for line in f.readlines()]
            f.close()

        with open("testfiles/short-genes.txt", "r") as f:
            genes = [line.strip() for line in f.readlines()]
            f.close()

        gb = GenBank(genes, species)
        data = gb.search()
        gb.summarize("short-test-1", data)
        gb.download("short-test-1")


    # gb = GenBank(genes, species)
    # data = gb.search()
    # gb.summarize("homo_rho", data)
    # gb.download("homo_rho")

# TODO: A docker image, singularity package, something like pip, but these options work across platforms
# MACSE large dataset pipeline uses singularity; good for upscaling and packaging!
# Being able to have a tree as part of sequence selection (easier to view ANNOTATED tree instead of numbers)
# Think of the end-goal; make it very clear! The fact that it's not implemented in anything else very well; selling point!
