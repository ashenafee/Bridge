# Bridge

![Banner](/assets/Bridge%20Banner.png)
![GitHub](https://img.shields.io/github/license/ashenafee/Bridge?style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/ashenafee/Bridge?style=for-the-badge)

An evolutionary biology analysis suite bridging sequence data to phylogenetic trees.

## Extra Documentation

- [App Setup](documentation/App%20Setup.md)

## About
Bridge is a genetic analysis toolkit built using Python. It currently has support for:

- Acquiring biological sequences from different databases
- Running BLAST searches
- Filtering downloaded sequences results based off taxonomy
- Filtering BLAST results based off taxonomy
- Aligning sequences
- Generating phylogenetic trees

Currently, Bridge can search [GenBank](https://www.ncbi.nlm.nih.gov/genbank/) and [Ensembl](https://useast.ensembl.org/index.html) for biological sequences. From these sources, one can download:

- Gene sequences
- Transcript sequences
- Protein sequences

## Pre-requisites

- [Python 3.10+](https://www.python.org/)
- [BLAST+](https://blast.ncbi.nlm.nih.gov/doc/blast-help/downloadblastdata.html)

## Installation

### From source

1. Clone the repository

```bash
git clone https://github.com/ashenafee/Bridge.git
```

2. Navigate to the repository

```bash
cd Bridge
```

3. Make the setup script executable

```bash
chmod +x ./setup
```

4. Run the setup script

```bash
./setup
```

5. Activate the virtual environment

```bash
source "venv/bin/activate"
```

6. Launch the program

```bash
python bridge.py --help
```

## Usage

### Downloading sequences

To download sequences, specify which database you'd like to download from and provide the species name(s) as well as sequence(s) you'd like to download.

#### Downloading from GenBank

```bash
python bridge.py -gb -g GENE -s SPECIES -o OUTPUT
```

For example, say we want to download the following genes for the species *Homo sapiens*:

- *TRPA1*
- *RHO*
- *TP53*

We can do so by running the following command:

```bash
python bridge.py -gb -g "TRPA1,RHO,TP53" -s "Homo sapiens" -o "sequences.fasta"
```

#### Downloading from Ensembl

```bash
python bridge.py -es -g GENE -s SPECIES -o OUTPUT
```

For example, say we want to download the following genes for the species *Homo sapiens*:

- *TRPA1*
- *RHO*
- *TP53*

We can do so by running the following command:

```bash
python bridge.py -es -g "TRPA1,RHO,TP53" -s "Homo sapiens" -o "sequences.fasta"
```

### Running BLAST searches

To run BLAST searches, specify the file containing the sequences you'd like to search against.

#### Running BLAST searches with default parameters

```bash
python bridge.py -b -f FILE -o OUTPUT
```

For example, say we have a file named `sequences.fasta` and want to run BLAST on it. Then we can do so by running the following command:

```bash
python bridge.py -b -f "sequences.fasta" -o "blast_results.txt"
```

#### Running BLAST searches with custom parameters

```bash
python bridge.py -b -f FILE -bp PARAMETERS -o OUTPUT
```

For example, say we have a file named `sequences.fasta` and want to run BLAST on it with the following parameters:

- *evalue* = 0.001
- *word_size* = 11
- *gapopen* = 11
- *max_target_seqs* = 5

We can do so by running the following command:

```bash
python bridge.py -b -f "sequences.fasta" -bp "evalue=0.001,word_size=11,gapopen=11,max_target_seqs=5" -o "blast_results.txt"
```

#### Running BLAST searches with a gene and species

```bash
python bridge.py -b -g GENE -s SPECIES -o OUTPUT
```

For example, say we want to run BLAST using *RHO* in the species *Homo sapiens*. We can do so by running the following command:

```bash
python bridge.py -b -g "RHO" -s "Homo sapiens" -o "blast_results.txt"
```

### Filtering results

To filter results, specify the file containing the results you'd like to filter and the taxonomy you'd like to filter by.


#### Filtering BLAST results

```bash
python bridge.py -ft TAXONOMY -f FILE -o OUTPUT -bf
```

For example, say we have a file named `blast_results.txt` and want to filter it by the taxonomy *Mammalia*. Then we can do so by running the following command:

```bash
python bridge.py -ft "Mammalia" -f "blast_results.txt" -o "filtered.txt" -bf
```

#### Filtering downloaded sequences

```bash
python bridge.py -ft TAXONOMY -f SUMMARY_FILE -o OUTPUT
```

For example, say we have a file named `summary.txt` and want to filter it by the taxonomy *Mammalia*. Then we can do so by running the following command:

```bash
python bridge.py -ft "Mammalia" -f "summary.txt" -o "filtered.txt"
```

Note: This only works for sequences downloaded from GenBank.

### Aligning sequences

To align sequences, specify the file containing the sequences you'd like to align.

#### Aligning using MUSCLE

```bash
python bridge.py -a "muscle" -t RANK -f FILE -o OUTPUT
```

For example, say we have a file named `sequences.fasta` and want to align it using MUSCLE. Then we can do so by running the following command:

```bash
python bridge.py -a "muscle" -t "order" -f "sequences.fasta" -o "aligned.fasta"
```

This will create an alignment file named `aligned.fasta`, which is then used to generate a tree. The distribution of sequences in the tree will be displayed by the specified rank (i.e., 20% of species in the alignment are Primates).

## Frequently Asked Questions

**When running the setup script, I get `virtualenv command not found`. How do I fix this?**

It's likely that `virtualenv` is not bundled with your installation of Python. Run the command below and then re-run the setup script to fix the issue:

```bash
pip install virtualenv
```

## Known issues

- Cannot search GenBank for large (~500) amounts of sequences at once
- Cannot accurately specify how many BLAST results to return
- Installing MUSCLE dynamically is difficult on macOS due to chip architecture differences

## Roadmap

- [x] Add filtering capabilities for BLAST results
- [x] Allow the user to search for a gene and species to run a BLAST search on
- [x] Add support for aligning sequences
- [x] Add support for phylogenetic tree generation
- [ ] Add automatic BLAST download if not found in PATH
- [ ] Create a basic GUI to make the program more user-friendly

## Contributing

Contributions are welcome! If you run into a new issue, please create a new issue on the [issues](https://github.com/ashenafee/Bridge/issues) page. If you'd like to contribute to the project, please fork the repository and submit a pull request.

## Authors

- **Ashenafee Mandefro** - *Whole project* - [ashenafee](https://www.ashenafee.com/)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
