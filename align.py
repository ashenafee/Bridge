# Module containing all alignment functions
# TODO: When writing documentation, ensure the user knows to add the executables
#       to their PATH before using Bridge.

# TODO: Let the user choose if they prefer Bridge to download the executable for
#       the alignment algorithm if it's not found in their PATH.

# TODO: Muscle works with Homebrew, not normal download!

import os
import platform
import sys
from Bio.Align.Applications import MuscleCommandline
from shutil import which

import requests
from tqdm import tqdm



class Muscle:
    """
    A wrapper class for interacting with the MUSCLE MSA through Biopython.
    """

    def __init__(self, input: str, output: str):
        self.input = input
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
        # Check the user's OS
        if sys.platform == 'win32':
            # Download the Windows executable
            exe = 'https://github.com/rcedgar/muscle/releases/download/5.1.0/muscle5.1.win64.exe'
        elif sys.platform == 'darwin':
            # Download the Mac executable
            # Check if the Mac is Apple Silicon or Intel
            if platform.machine() == 'arm64':
                exe = 'https://github.com/rcedgar/muscle/releases/download/5.1.0/muscle5.1.macos_arm64'
            elif platform.machine() == 'x86_64':
                exe = 'https://github.com/rcedgar/muscle/releases/download/5.1.0/muscle5.1.macos_intel64'
        elif sys.platform == 'linux':
            # Download the Linux executable
            exe = 'https://github.com/rcedgar/muscle/releases/download/5.1.0/muscle5.1.linux_intel64'
        
        # Download the executable
        r = requests.get(exe, allow_redirects=True)

        # Check if the download was successful
        if r.status_code == 200:
            # Download the file using tqdm
            with open('muscle', 'wb') as f:
                for chunk in tqdm(r.iter_content(chunk_size=1024), 
                                  total=len(r.content)/1024, unit='KB', 
                                  unit_scale=True, desc='Downloading MUSCLE'):
                    if chunk:
                        f.write(chunk)
            
            # Make the file executable
            os.chmod('muscle', 0o755)
            
            self.program = os.path.abspath('muscle')

            return True

        return False
        
    def align(self):
        """
        Run MUSCLE on a given FASTA file input.
        """
        muscle = MuscleCommandline(self.program, input=self.input, 
                                   out=self.output)
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

    pass







# TODO: Implement the following alignment algorithms
# Clustal Omega
# ClustalW
# Dialign
# MSAProbs
# MAFFT
# PRANK
# Probcons
# TCoffee
