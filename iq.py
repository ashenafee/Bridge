import os
import subprocess
import sys
import tarfile
import zipfile
from datetime import datetime
from shutil import which
from threading import Thread
from time import sleep

import requests
from Bio import Entrez
from Bio import Phylo
from matplotlib import pyplot as plt
from tqdm import tqdm

EMAIL = os.getenv("EMAIL")
API_KEY = os.getenv("NCBI_API_KEY")


class Tree:
    """
    A phylogenetic tree generated from a multiple sequence alignment.
    """

    def __init__(self, input: str, output: str, rank: str):
        """
        Initialize the Tree object.
        :param input: The input alignment file.
        :param output: The output tree file.
        :param rank: The taxonomic rank to use for the tree.
        """
        self.input = input
        self.output = output
        self.rank = rank

        self.lineages = {}
        self.ranks = {}
        self.accessions = {}

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
        # Check the user's OS
        if sys.platform == 'win32':
            # Windows
            return self._install_windows()

        elif sys.platform == 'darwin':
            # macOS
            return self._install_unix('2.0.6-MacOSX.zip', 'zip')

        elif sys.platform == 'linux':
            # Linux
            return self._install_unix('2.0.6-Linux.tar.gz', 'tar.gz')

        return False

    def _install_windows(self) -> bool:
        """
        Install IQ-TREE on Windows.
        """
        # Check if IQ-TREE is already installed
        if os.path.exists('iqtree.exe'):
            return True

        # Request the data for the Windows executable
        exe = 'https://github.com/Cibiv/IQ-TREE/releases/download/v2.0.6/\
        iqtree-2.0.6-Windows.zip'
        r = requests.get(exe, allow_redirects=True)

        # Check if the request was successful
        if r.status_code == 200:
            # Save the executable
            self._download_archive(r, 'zip')

            # Extract the archive
            self._extract_archive("zip")

            # Move the executable
            self._move_executable()

            # Set the program path
            self.program = os.path.abspath('iqtree.exe')

            return True

        return False

    def _install_unix(self, specific: str, archive: str) -> bool:
        """
        Install IQ-TREE on a UNIX-based system. This includes macOS and Linux.
        Returns True if successful, False otherwise.
        :param specific: The specific OS.
        :param archive: The file archive type (zip, tarball).
        """
        # Check if IQ-TREE is already installed
        if os.path.exists('iqtree'):
            return True

        # Request the data for the archive
        url = f'https://github.com/Cibiv/IQ-TREE/releases/download/v2.0.6/iqtre\
        e-{specific}'
        r = requests.get(url, allow_redirects=True)

        # Check if the request was successful
        if r.status_code == 200:
            # Save the archive
            self._download_archive(r, archive)

            # Extract the archive
            self._extract_archive(archive)

            # Move the executable
            self._move_executable()

            # Set the program path
            self.program = os.path.abspath('iqtree')

            return True

        return False

    def _download_archive(self, r: requests.Response,
                          archive: str) -> None:
        """
        Download the IQ-TREE archive from the GitHub repository.
        :param r: Response made from the GitHub.
        :param archive: The file archive type (zip, tarball).
        """
        total_size = int(r.headers.get('content-length', 0))
        block_size = 1024
        t = tqdm(total=total_size, unit='iB', unit_scale=True)
        with open(f'iqtree.{archive}', 'wb') as f:
            for data in r.iter_content(block_size):
                t.update(len(data))
                f.write(data)
        t.close()

    def _extract_archive(self, archive: str) -> None:
        """
        Extract the IQ-TREE archive.
        :param archive: The file extension of the archive (zip, tarball).
        """
        # Check if archive is .zip
        if archive == "zip":
            # Extract and remove the archive
            with zipfile.ZipFile('iqtree.zip', 'r') as zip_ref:
                zip_ref.extractall()
            os.remove('iqtree.zip')

        # If not, archive is .tar.gz
        else:
            # Extract and remove the archive
            with tarfile.open('iqtree.tar.gz', 'r:gz') as tar:
                tar.extractall()
            os.remove('iqtree.tar.gz')

    def _move_executable(self) -> None:
        """
        Move the IQ-TREE executable up from the bin folder to the project root.
        After moving, delete the originally extracted folder.
        """
        if sys.platform == 'win32':
            # Windows

            # Move the executable and remove the folder
            os.system('move iqtree-2.0.6-Windows\\bin\\iqtree.exe .')
            os.system('rmdir /s /q iqtree-2.0.6-Windows')

        elif sys.platform == 'darwin':
            # Mac

            # Move the executable and remove the folder
            os.system('mv iqtree-2.0.6-MacOSX/bin/iqtree .')
            os.system('rm -r iqtree-2.0.6-MacOSX')

        elif sys.platform == 'linux':
            # Linux

            # Move the executable and remove the folder
            os.system('mv iqtree-2.0.6-Linux/bin/iqtree .')
            os.system('rm -r iqtree-2.0.6-Linux')

    def run(self) -> None:
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

        # Rename the FASTA headers in the alignment file
        self._rename_headers()

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

    def _rename_headers(self) -> None:
        """
        Rename the FASTA headers in the input alignment file.
        """
        # Open the input alignment
        with open(self.input, 'r') as f:
            lines = f.readlines()

        # Remove non-header lines
        headers = [line for line in lines if line[0] == '>']

        # Grab the accessions for each entry
        accessions = [header.split(' ')[0][1:] for header in headers]

        # Create new headers
        headers = []
        for accession in accessions:
            # Grab the species
            species = self.accessions[accession]

            # Create the new header
            header = f'>{species.replace(" ", "_")}_({accession})\n'
            headers.append(header)

        # Replace the headers in the input alignment
        for i in range(len(lines)):
            if lines[i][0] == '>':
                lines[i] = headers.pop(0)

        # Write the new alignment
        with open(self.input, 'w') as f:
            f.writelines(lines)

    def _get_phylogenies(self) -> None:
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
            if not taxonomy_ids:
                continue
            records = self.entrez.efetch(db='taxonomy', id=taxonomy_ids,
                                            retmode='xml')
            records = Entrez.read(records)

            # Find which record is the specified rank
            for record in records:
                if record['Rank'] == self.rank.lower():
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
        self.ranks = dict(sorted(self.ranks.items(), key=lambda item: item[1],
                                 reverse=True))

    def _display_pie_chart(self):
        """
        Display the pie chart of the phylogeny distribution.
        """
        # Create a pie chart of the specified rank distribution
        plt.figure(figsize=(10, 10))
        plt.pie(self.ranks.values(), labels=self.ranks.keys(),
                autopct='%1.1f%%')
        plt.title(f'{self.rank.capitalize()} Distribution')

        # Save the figure
        date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f'{self.rank}-{date}.png'
        plt.savefig(filename)

        # Display the pie chart
        plt.show()

    def _parse_records(self, records: str) -> None:
        """
        Parse the records returned by NCBI.
        :param records: The records returned.
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
            if "other sequences" or "artificial sequences" not in lineage:
                self.lineages[accession] = lineage
            else:
                # Remove the accession from the dictionary
                del self.accessions[accession]

            # Make sure the organism is included in the lineage dictionary if
            # and only if they are natural
            self.lineages[accession] = lineage if "other sequences" or \
                                                  "artificial sequences" \
                                                  not in lineage else []
            # Grab the species name
            species = record['GBSeq_organism']
            # Add the species name to the dictionary
            self.accessions[accession] = species

    def _run_iqtree(self) -> None:
        """
        Helper function to run IQ-TREE on a separate thread.
        """
        # Run IQ-TREE
        subprocess.run([self.program, '-s', self.input, '-redo'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _display_tree(self) -> None:
        """
        Display the IQ-TREE using matplotlib and Biopython
        """
        tree = Phylo.read(f'{self.input}.treefile', 'newick')
        Phylo.draw(tree)
