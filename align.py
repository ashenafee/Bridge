import os
import sys
import tarfile
from shutil import which
from threading import Thread
from time import sleep

import requests
from Bio.Align.Applications import MuscleCommandline
from tqdm import tqdm


class Muscle:
    """
    A wrapper class for interacting with the MUSCLE MSA through Biopython.
    """

    def __init__(self, user_input: str, output: str):
        """
        Initialize the MUSCLE wrapper class.
        :param user_input: The input file for MUSCLE.
        :param output: The output file for MUSCLE.
        """
        self.input = user_input

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
            # Windows
            return self._install_windows()

        elif sys.platform == 'darwin':
            # macOS
            return self._install_macos()

        elif sys.platform == 'linux':
            # Linux
            return self._install_linux()

        return False

    def _install_windows(self) -> bool:
        """
        Install MUSCLE on Windows. Returns True if successful, False otherwise.
        """
        # Check if MUSCLE is already installed
        if os.path.exists('muscle.exe'):
            return True

        # Request the data for the Windows executable
        exe = 'https://drive5.com/muscle/downloads3.8.31/muscle3.8.31_i86win32.\
        exe'
        r = requests.get(exe, stream=True)

        # Check if the request was successful
        if r.status_code == 200:
            # Save the executable
            total_size = int(r.headers.get('content-length', 0))
            block_size = 1024
            t = tqdm(total=total_size, unit='iB', unit_scale=True)
            with open('muscle.exe', 'wb') as f:
                for data in r.iter_content(block_size):
                    t.update(len(data))
                    f.write(data)
            t.close()

            # Set the program path for this object
            self.program = os.path.abspath('muscle.exe')

            return True

        return False

    def _install_macos(self) -> bool:
        """
        Install MUSCLE on macOS. Returns True if successful, False otherwise.
        The executable installed is for Intel processors as MUSCLE v3.8.31
        does not have an ARM executable.
        """
        # Check if MUSCLE is already installed
        if os.path.exists('muscle'):
            return True

        # Request the data for the macOS executable
        exe = 'https://drive5.com/muscle/downloads3.8.31/muscle3.8.31_i86darwin\
        64.tar.gz'
        return self._install_unix(exe)

    def _install_linux(self) -> bool:
        """
        Install MUSCLE on Linux. Returns True if successful, False otherwise.
        """
        # Check if MUSCLE is already installed
        if os.path.exists('muscle'):
            return True

        # Request the data for the Linux executable
        exe = 'https://drive5.com/muscle/downloads3.8.31/muscle3.8.31_i86linux6\
        4.tar.gz'

        # Download the executable
        return self._install_unix(exe)

    def _install_unix(self, exe: str) -> bool:
        """
        Helper function to install MUSCLE on Unix-based systems.
        :param exe: The URL to the executable.
        """
        r = requests.get(exe, allow_redirects=True)
        # Check if the download was successful
        if r.status_code == 200:
            # Save the executable
            self._save_muscle_dl(r)

            # Extract the tarball
            with tarfile.open('muscle.tar.gz', 'r:gz') as tar:
                tar.extractall()

            # Remove the tarball
            os.remove('muscle.tar.gz')

            self.program = os.path.abspath('muscle')

            return True
        return False

    def _save_muscle_dl(self, r: requests.Response) -> None:
        """
        Helper function to save the MUSCLE download using tqdm.
        :param r: The request object.
        """
        with open('muscle.tar.gz', 'wb') as f:
            for chunk in tqdm(r.iter_content(chunk_size=1024),
                              total=len(r.content) / 1024, unit='KB',
                              unit_scale=True, desc='Downloading MUSCLE'):
                if chunk:
                    f.write(chunk)

    def align(self) -> None:
        """
        Run MUSCLE on a given FASTA file input.
        """
        muscle = MuscleCommandline(self.program, input=self.input,
                                   out=self.output)

        # Run MUSCLE on a separate thread
        t = Thread(target=self._run_muscle, args=(muscle,))
        t.start()

        # Show a progress bar
        pbar = tqdm(bar_format='[ALIGN] - Time elapsed:\t{elapsed}', )

        # Update the progress bar
        while t.is_alive():
            pbar.update(1)
            sleep(1)

        # Close the progress bar
        pbar.close()
        t.join()

    def _run_muscle(self, muscle: MuscleCommandline) -> None:
        """
        Helper function to run MUSCLE on a separate thread.
        :param muscle: The MuscleCommandline object.
        """
        muscle()
