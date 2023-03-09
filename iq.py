import sys
from time import sleep
import zipfile
from matplotlib import pyplot as plt
import requests
import os
from tqdm import tqdm
from shutil import which
from threading import Thread
import subprocess
from Bio import Phylo
from Bio import Entrez
from datetime import datetime


EMAIL = os.getenv("EMAIL")
API_KEY = os.getenv("NCBI_API_KEY")


class Tree:
    """
    A phylogenetic tree generated from a multiple sequence alignment.
    """

    def __init__(self, input: str, output: str, filter: str):
        self.input = input
        self.output = output
        self.filter = filter

        self.lineages = {}
        self.ranks = {}

        self.program = ""

        self.entrez = Entrez
        self.entrez.email = EMAIL
        self.entrez.api_key = API_KEY
    
    def check_installed(self) -> bool:
        """
        Check if IQ-TREE is available in the user's PATH.
        """
        if which('iqtree'):
            self.program = which('iqtree')
            return True
        
        if os.path.exists('iqtree'):
            self.program = os.path.abspath('iqtree')
            return True
        
        return False

    def install(self) -> bool:
        """
        Install IQ-TREE to the local directory.
        """

        link = ''

        # Check the user's OS
        if sys.platform == 'win32':
            # Download the Windows executable
            link = 'https://github.com/Cibiv/IQ-TREE/releases/download/v2.0.6/iqtree-2.0.6-Windows.zip'
        elif sys.platform == 'linux':
            # Download the Linux executable
            link = 'https://github.com/Cibiv/IQ-TREE/releases/download/v2.0.6/iqtree-2.0.6-Linux.tar.gz'
        elif sys.platform == 'darwin':
            # Download the Mac executable
            link = 'https://github.com/Cibiv/IQ-TREE/releases/download/v2.0.6/iqtree-2.0.6-MacOSX.zip'
        else:
            # Unsupported OS
            return False
        
        # Download the executable using tqdm
        self._download(link)

        # Unzip the file
        self._unzip_download()
        
        # Move the executable from bin to the current directory
        self._move_executable()
        
        # Remove the zip file and the extracted directory
        self._clean_up_download()

        # Set the program path
        self.program = os.path.abspath('iqtree')

        return True

    def _download(self, link):
        r = requests.get(link, stream=True)
        total_size = int(r.headers.get('content-length', 0))
        block_size = 1024
        t=tqdm(total=total_size, unit='iB', unit_scale=True)
        with open('iqtree.zip', 'wb') as f:
            for data in r.iter_content(block_size):
                t.update(len(data))
                f.write(data)
        t.close()

    def _clean_up_download(self):
        os.remove('iqtree.zip')
        if sys.platform == 'win32':
            # Windows
            os.system('rmdir /s /q iqtree-2.0.6-Windows')
        elif sys.platform == 'linux':
            # Linux
            os.system('rm -r iqtree-2.0.6-Linux')
        elif sys.platform == 'darwin':
            # Mac
            os.system('rm -r iqtree-2.0.6-MacOSX')

    def _move_executable(self):
        if sys.platform == 'win32':
            # Windows
            os.system('move iqtree-2.0.6-Windows\\bin\\iqtree.exe .')
        elif sys.platform == 'linux':
            # Linux
            os.system('mv iqtree-2.0.6-Linux/bin/iqtree .')
        elif sys.platform == 'darwin':
            # Mac
            os.system('mv iqtree-2.0.6-MacOSX/bin/iqtree .')

    def _unzip_download(self):
        if sys.platform == 'win32':
            # Windows
            with zipfile.ZipFile('iqtree.zip', 'r') as zip_ref:
                zip_ref.extractall()
        elif sys.platform == 'linux':
            # Linux
            os.system('tar -xvzf iqtree.zip')
        elif sys.platform == 'darwin':
            # Mac
            with zipfile.ZipFile('iqtree.zip', 'r') as zip_ref:
                zip_ref.extractall()

    def run(self):
        """
        Run IQ-TREE on the input alignment.
        """

        # Create a thread to grab the phylogenies of each sequence
        t = Thread(target=self._get_phylogenies)
        t.start()

        # Show a progress bar
        pbar = tqdm(bar_format='[PHYLOGENIES] - Time elapsed:\t{elapsed}',)

        # Update the progress bar
        while t.is_alive():
            pbar.update(1)
            sleep(1)
        
        # Close the progress bar
        pbar.close()
        t.join()

        # Display the pie chart
        self._display_pie_chart()

        # Create a thread to run IQ-TREE
        t = Thread(target=self._run_iqtree)
        t.start()

        # Show a progress bar
        pbar = tqdm(bar_format='[TREE] - Time elapsed:\t{elapsed}',)

        # Update the progress bar
        while t.is_alive():
            pbar.update(1)
            sleep(1)

        # Close the progress bar
        pbar.close()

        t.join()

        # Remove non-tree files
        os.remove(f'{self.input}.bionj')
        os.remove(f'{self.input}.ckp.gz')
        os.remove(f'{self.input}.iqtree')
        os.remove(f'{self.input}.log')
        os.remove(f'{self.input}.mldist')
        os.remove(f'{self.input}.model.gz')

        # Display the tree
        self._display_tree()

    def _get_phylogenies(self) -> dict:
        """
        Get the phylogenies of the sequences in the input alignment.
        """

        # Open the input alignment
        with open(self.input, 'r') as f:
            lines = f.readlines()
        
        # Remove non-header lines
        headers = [line for line in lines if line[0] == '>']

        # Grab the accessions for each entry
        accessions = [header.split(' ')[0][1:] for header in headers]

        # Request NCBI for the records
        records = self.entrez.efetch(db='nucleotide', id=accessions, 
                                     retmode='xml')
        self._parse_records(records)

        # Count the number of species that fall under each specified rank
        for accession in self.lineages:
            # Grab the lineage
            taxonomies = self.lineages[accession]

            # Request NCBI for the taxonomy record
            taxonomy_ids = []
            for taxonomy in taxonomies[4:]:
                record = self.entrez.esearch(db='taxonomy', term=taxonomy)
                record = Entrez.read(record)
                # Grab the taxonomy ID
                taxonomy_id = record['IdList'][0]
                taxonomy_ids.append(taxonomy_id)
            
            # Grab the taxonomy records
            records = self.entrez.efetch(db='taxonomy', id=taxonomy_ids,
                                            retmode='xml')
            records = Entrez.read(records)

            # Find which record is the specified rank
            for record in records:
                if record['Rank'] == self.filter.lower():
                    # Grab the rank
                    rank = record['ScientificName']
                    # Add the Order to the dictionary
                    if rank in self.ranks:
                        self.ranks[rank] += 1
                    else:
                        self.ranks[rank] = 1
                    break

            sleep(0.25)

        # Sort the dictionary by the number of species
        self.ranks = dict(sorted(self.ranks.items(), key=lambda item: item[1], reverse=True))
    
    def _display_pie_chart(self):
        """
        Display the pie chart of the phylogeny distribution.
        """
        # Create a pie chart of the specified rank distribution
        plt.figure(figsize=(10, 10))
        plt.pie(self.ranks.values(), labels=self.ranks.keys(), autopct='%1.1f%%')
        plt.title(f'{self.rank.capitalize()} Distribution')

        filename = f'{self.rank}-\
            {datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.png'

        plt.savefig(filename)

        # Display the pie chart
        plt.show()

    def _parse_records(self, records: str) -> None:
        """
        Parse the records returned by NCBI.
        """
        # Parse the records
        records = Entrez.read(records)

        # Grab the lineages for each record
        for record in records:
            # Grab the accession
            accession = record['GBSeq_accession-version']
            # Grab the lineage
            lineage = record['GBSeq_taxonomy'].split('; ')
            # Add the lineage to the dictionary
            self.lineages[accession] = lineage

    def _run_iqtree(self):
        """
        Helper function to run IQ-TREE on a separate thread.
        """
        # Run IQ-TREE
        subprocess.run([self.program, '-s', self.input, '-redo'], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _display_tree(self):
        """
        Display the IQ-TREE using matplotlib and Biopython
        """
        tree = Phylo.read(f'{self.input}.treefile', 'newick')
        Phylo.draw(tree)



if __name__ == '__main__':
    entrez = Entrez
    entrez.email = EMAIL
    entrez.api_key = API_KEY

    records = entrez.efetch(db='taxonomy', id='2', retmode='xml')
    records = Entrez.read(records)

    tree = Tree()
