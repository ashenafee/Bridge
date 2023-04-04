# Module containing all alignment functions
# TODO: When writing documentation, ensure the user knows to add the executables
#       to their PATH before using Bridge.

# TODO: Let the user choose if they prefer Bridge to download the executable for
#       the alignment algorithm if it's not found in their PATH.

# TODO: Muscle works with Homebrew, not normal download!

import os
import platform
import subprocess
import sys
import tarfile
from time import sleep
from Bio.Align.Applications import MuscleCommandline
from shutil import which

import requests
from tqdm import tqdm
from threading import Thread



class Muscle:
    """
    A wrapper class for interacting with the MUSCLE MSA through Biopython.
    """

    def __init__(self, input: str, output: str):
        self.input = input

        if "." not in output:
            output += ".aln"

        self.output = output

        self.program = ""

    def check_installed(self) -> bool:
        """
        Check if MUSCLE is available in the user's PATH.
        """

        if which('muscle'):
            self.program = which('muscle')
            return True
        
        if os.path.exists('muscle'):
            self.program = os.path.abspath('muscle')
            return True
        
        return False
    
    def install_muscle(self) -> bool:
        """
        Download and install MUSCLE on the user's system.
        """
        # TODO: Refactor installation

        # Check the user's OS
        if sys.platform == 'win32':
            return self._install_windows()

        elif sys.platform == 'darwin':

            return self._install_macos()
        
        elif sys.platform == 'linux':

            return self._install_linux()
        
        return False

    def _install_windows(self):
        """
        Install MUSCLE on Windows. Returns True if successful, False otherwise.
        """
        # Check if MUSCLE is already installed
        if os.path.exists('muscle.exe'):
            return True

        # Download the Windows executable
        exe = 'https://drive5.com/muscle/downloads3.8.31/muscle3.8.31_i86win32.exe'

        r = requests.get(exe, allow_redirects=True)

        # Check if the download was successful
        if r.status_code == 200:
            with open('muscle.exe', 'wb') as f:
                for chunk in tqdm(r.iter_content(chunk_size=1024), 
                                  total=len(r.content)/1024, unit='KB', 
                                  unit_scale=True, desc='Downloading MUSCLE'):
                    if chunk:
                        f.write(chunk)
            
            self.program = os.path.abspath('muscle.exe')

            return True

        return False

    def _install_macos(self):
        """
        Install MUSCLE on macOS. Returns True if successful, False otherwise.
        The executable installed is for Intel processors as MUSCLE v3.8.31
        does not have an ARM executable.
        """

        if os.path.exists('muscle'):
            return True
        
        exe = 'https://drive5.com/muscle/downloads3.8.31/muscle3.8.31_i86darwin64.tar.gz'

        # Download the macOS (Intel) executable
        r = requests.get(exe, allow_redirects=True)

        # Check if the download was successful
        if r.status_code == 200:
            # Download the file using tqdm
            with open('muscle.tar.gz', 'wb') as f:
                for chunk in tqdm(r.iter_content(chunk_size=1024), 
                                total=len(r.content)/1024, unit='KB', 
                                unit_scale=True, desc='Downloading MUSCLE'):
                    if chunk:
                        f.write(chunk)
            
            # Extract the tarball
            with tarfile.open('muscle.tar.gz', 'r:gz') as tar:
                tar.extractall()
            
            # Remove the tarball
            os.remove('muscle.tar.gz')

            self.program = os.path.abspath('muscle')

            return True
        
        return False

    def _install_linux(self):
        """
        Install MUSCLE on Linux. Returns True if successful, False otherwise.
        """

        if os.path.exists('muscle'):
            return True

        # Download the Linux executable
        exe = 'https://drive5.com/muscle/downloads3.8.31/muscle3.8.31_i86linux64.tar.gz'

        # Download the executable
        r = requests.get(exe, allow_redirects=True)

        # Check if the download was successful
        if r.status_code == 200:
            # Download the file using tqdm
            with open('muscle.tar.gz', 'wb') as f:
                for chunk in tqdm(r.iter_content(chunk_size=1024), 
                                  total=len(r.content)/1024, unit='KB', 
                                  unit_scale=True, desc='Downloading MUSCLE'):
                    if chunk:
                        f.write(chunk)
            
            # Extract the tarball
            with tarfile.open('muscle.tar.gz', 'r:gz') as tar:
                tar.extractall()
            
            # Remove the tarball
            os.remove('muscle.tar.gz')

            self.program = os.path.abspath('muscle')

            return True

        return False

    def align(self):
        """
        Run MUSCLE on a given FASTA file input.
        """
        muscle = MuscleCommandline(self.program, input=self.input, 
                                   out=self.output)

        # Run MUSCLE on a separate thread
        t = Thread(target=self._run_muscle, args=(muscle,))
        t.start()

        # Show a progress bar
        pbar = tqdm(bar_format='[ALIGN] - Time elapsed:\t{elapsed}',)

        # Update the progress bar
        while t.is_alive():
            pbar.update(1)
            sleep(1)

        # Close the progress bar
        pbar.close()

        t.join()
   
    def _run_muscle(self, muscle):
        """
        Helper function to run MUSCLE on a separate thread.
        """
        muscle()

# class Mafft:
#     """
#     A wrapper class for interacting with the MAFFT MSA through Biopython.
#     """

#     def __init__(self, input: str, output: str):
#         self.input = input
#         self.output = output

#         self.program = ""

#     def check_installed(self) -> bool:
#         """
#         Check if MAFFT is available in the user's PATH.
#         """

#         if which('mafft'):
#             self.program = which('mafft')
#             return True
        
#         if os.path.exists('mafft'):
#             self.program = os.path.abspath('mafft')
#             return True
        
#         return False
    
#     def install_mafft(self) -> bool:
#         """
#         Download and install MAFFT on the user's system.
#         """
#         # Check the user's OS
#         if sys.platform == 'win32':
#             # Download the Windows executable
#             exe = '


if __name__ == '__main__':
    # Test the MUSCLE wrapper
    muscle = Muscle('BLAST-name-symbol-test-filtered.out.fasta', 'test.aln')
    if not muscle.check_installed():
        if not muscle.install_muscle():
            print('Failed to install MUSCLE.')
            sys.exit(1)
    
    muscle.align()






# TODO: Implement the following alignment algorithms
# Clustal Omega
# ClustalW
# Dialign
# MSAProbs
# MAFFT
# PRANK
# Probcons
# TCoffee
