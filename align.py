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
        # Check the user's OS
        if sys.platform == 'win32':
            # Download the Windows executable
            exe = 'https://github.com/rcedgar/muscle/releases/download/5.1.0/muscle5.1.win64.exe'
        elif sys.platform == 'darwin':
            # Download the Mac executable
            # Check if the Mac is Apple Silicon or Intel
            if platform.machine() == 'arm64':

                # https://github.com/rcedgar/muscle/pull/47
                # TODO: Add the Apple Silicon executable
                # Currently, the executable must be built from source and even
                # then requires some libraries to be installed manually.

                # Clone the MUSCLE repository
                subprocess.run(['git', 'clone', '-b', 'dev', 'https://github.com/blake-riley/muscle.git'])

                # Install the dependencies
                subprocess.run(['brew', 'install', 'gcc'])
                subprocess.run(['brew', 'install', 'libomp'])

                # Change to the MUSCLE directory
                os.chdir('muscle/src')

                # Get libomp directory
                libomp_dir = subprocess.run(['brew', '--prefix', 'libomp'], capture_output=True).stdout.decode('utf-8').strip()

                # Change the header import in myutils.h
                with open('./myutils.h', 'r') as f:
                    lines = f.readlines()
                
                with open('./myutils.h', 'w') as f:
                    for line in lines:
                        if line.startswith('#include <omp.h>'):
                            f.write(f'#include "{libomp_dir}/include/omp.h"\n')
                        else:
                            f.write(line)
                
                # Change the header import in locallock.h
                with open('./locallock.h', 'r') as f:
                    lines = f.readlines()
                
                with open('./locallock.h', 'w') as f:
                    for line in lines:
                        if line.startswith('#include <omp.h>'):
                            f.write(f'#include "{libomp_dir}/include/omp.h"\n')
                        else:
                            f.write(line)
                
                # Build MUSCLE
                subprocess.run(['make'], 
                               env={'CXXFLAGS': f'-I{libomp_dir}/include', 
                                    'LIBS': f'{libomp_dir}/lib/libomp.dylib'})

                # Move the executable to the current directory
                subprocess.run(['mv', './Darwin/muscle', '../muscle-1'])
                os.chdir('..')
                subprocess.run(['mv', './muscle-1', '../muscle-1'])

                # Change back to the original directory
                os.chdir('..')

                # Remove the MUSCLE repository
                subprocess.run(['rm', '-rf', 'muscle'])

                # Rename the executable
                os.rename('./muscle-1', './muscle')

                # Make the file executable
                os.chmod('muscle', 0o755)

                return True

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
