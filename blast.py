import os
import subprocess
from threading import Thread
from time import sleep

from Bio import SearchIO
from Bio.Blast.Applications import NcbiblastnCommandline
from tqdm import tqdm

from genbank import GenBank, GenBankDDL


def blastn(query, params=None, db='nt', out="blastn.out.txt", ms=100, ev=0.05,
           ws=11, rw=2, pn=-3, go=5, ge=2, tl=18, tt='coding') -> None:
    """
    Run a blastn search on the given query.
    :param params: The parameters to use for the BLAST search.
    :param query: The query file.
    :param db: The database to search.
    :param out: The output file.
    :param ms: The maximum amount of target sequences to return.
    :param ev: The e-value threshold.
    :param ws: The word size.
    :param rw: The reward for a match.
    :param pn: The penalty for a mismatch.
    :param go: The gap opening cost.
    :param ge: The gap extension cost.
    :param tl: The template length.
    :param tt: The template type.
    """
    # Create the BLAST command to run
    blastn_cline = NcbiblastnCommandline(query=query,
                                         db=db,
                                         task='dc-megablast',
                                         remote=True,
                                         outfmt='6 std staxid',
                                         out=out,
                                         max_target_seqs=ms,
                                         evalue=ev,
                                         word_size=ws,
                                         reward=rw,
                                         penalty=pn,
                                         gapopen=go,
                                         gapextend=ge,
                                         template_length=tl,
                                         template_type=tt,
                                         )

    # Configure any custom parameters
    if params:
        blastn_cline = _setup_blast_params(blastn_cline, params)
    else:
        blastn_cline = _setup_blast_params(blastn_cline, {})

    # Create a new thread to run the BLAST search
    t = Thread(target=_blast_thread, args=(blastn_cline,))
    t.start()

    # Show an indeterminate progress bar
    pbar = tqdm(bar_format='[BLAST] - Time elapsed:\t{elapsed}', )

    # Update the progress bar
    while t.is_alive():
        pbar.update(1)
        sleep(1)

    # Close the progress bar
    pbar.close()
    t.join()

    # Download the BLAST results
    _download_blast_results(out)


def _download_blast_results(out: str) -> None:
    """
    Download the BLAST results.
    :param out: The output file.
    """
    # Open the BLAST results
    with open(out, 'r') as f:
        lines = f.readlines()

    # Get the accessions of the results
    accessions = [line.split('\t')[1] for line in lines]

    # Use Biopython's Entrez module to download the sequences
    gb = GenBankDDL(records=accessions)
    gb.download(f'{out}')


def _blast_thread(blastn: NcbiblastnCommandline) -> None:
    """
    Thread to run the BLAST search.
    :param blastn: The BLAST command to run.
    """
    subprocess.call(str(blastn), shell=True)


def _setup_blast_params(executable: NcbiblastnCommandline,
                        params: dict) -> NcbiblastnCommandline:
    """
    Set up the BLAST parameters.
    :param executable: The BLAST executable.
    :param params: The parameters to use.
    """
    # Try to turn numbers into integers
    for x in params:
        try:
            params[x] = int(params[x])
        except ValueError:
            pass

    # Set the parameters
    for x, y in params.items():
        setattr(executable, x, y)

    return executable


def read_blast(blast_file: str) -> dict:
    """
    Read the blast file and parse information.
    :param blast_file: The BLAST file.
    """
    # Read the BLAST file
    results = SearchIO.read(blast_file, 'blast-tab', fields=['std', 'staxid'])
    results_raw = open(blast_file, 'r').readlines()

    # Parse the taxids into a dictionary
    parsed = {}
    for i in range(len(results)):
        result = results[i]
        parsed[result.id] = {
            'fragments': result.fragments,
            'hsps': result.hsps,
            'taxid': results_raw[i].split('\t')[-1].strip()
        }

    return parsed


def blast_by_species_and_symbol(species: list, symbol: list,
                                output: str) -> None:
    """
    Run a BLAST search by downloading the sequence for the given symbol and
    species.
    :param species: The species to search for.
    :param symbol: The symbol to search for.
    :param output: The output file.
    """
    # Search for the symbol in the GenBank database
    gb = GenBank(symbol, species)
    data = gb.search()

    # Download the sequence
    gb.download(filename="btemp", records=data)

    # Run the BLAST search
    blastn('btemp.fasta', out=output)

    # Delete the temporary FASTA file
    os.remove('btemp.fasta')
