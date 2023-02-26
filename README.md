# Bridge
An evolutionary biology analysis suite bridging sequence data to phylogenetic trees.

## About
Bridge is a genetic analysis toolkit built using Python. It currently has support for:

- Acquiring biological sequences from different databases
- Running BLAST searches
- Filtering BLAST results based off taxonomy

Currently, Bridge can search: [GenBank](https://www.ncbi.nlm.nih.gov/genbank/) and [Ensembl](https://useast.ensembl.org/index.html) for biological sequences. From these sources, one can download:

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

2. Install the dependencies

```bash
pip install -r requirements.txt
```

3. Launch the program

```bash
python bridge.py --help
```

## Usage

### Downloading sequences

To download sequences, specify which database you'd like to download from and provide the species name(s) as well as sequence(s) you'd like to download.

#### Downloading from GenBank

```bash
python bridge.py -gb -g GENE -s SPECIES
```

For example, say we want to download the following genes for the species *Homo sapiens*:

- *TRPA1*
- *RHO*
- *TP53*

We can do so by running the following command:

```bash
python bridge.py -gb -g "TRPA1,RHO,TP53" -s "Homo sapiens"
```

#### Downloading from Ensembl

```bash
python bridge.py -es -g GENE -s SPECIES
```

For example, say we want to download the following genes for the species *Homo sapiens*:

- *TRPA1*
- *RHO*
- *TP53*

We can do so by running the following command:

```bash
python bridge.py -es -g "TRPA1,RHO,TP53" -s "Homo sapiens"
```

### Running BLAST searches

To run BLAST searches, specify the file containing the sequences you'd like to search against.

```bash
python bridge.py -b -f FILE
```

For example, say we have a file named `sequences.fasta` and want to run BLAST on it. Then we can do so by running the following command:

```bash
python bridge.py -b -f "sequences.fasta"
```

#### Running BLAST searches with custom parameters

To run BLAST searches with custom parameters, specify the file containing the sequences you'd like to search against and the parameters you'd like to use.

```bash
python bridge.py -b -f FILE -bp PARAMETERS
```

For example, say we have a file named `sequences.fasta` and want to run BLAST on it with the following parameters:

- *evalue* = 0.001
- *word_size* = 3
- *gapopen* = 11
- *max_target_seqs* = 5

We can do so by running the following command:

```bash
python bridge.py -b -f "sequences.fasta" -bp "evalue=0.001,word_size=3,gapopen=11,max_target_seqs=5"
```

### Filtering BLAST results

To filter BLAST results, specify the file containing the BLAST results you'd like to filter and the taxonomy you'd like to filter by.

```bash
python bridge.py -ft TAXONOMY -f FILE -o OUTPUT_FILE -bf
```

For example, say we have a file named `blast_results.txt` and want to filter it by the taxonomy *Mammalia*. Then we can do so by running the following command:

```bash
python bridge.py -ft "Mammalia" -f "blast_results.txt" -o "filtered.txt" -bf
```

### Filtering downloaded sequences

For sequences downloaded from GenBank, you can filter them by taxonomy using the following command:

```bash
python bridge.py -ft TAXONOMY -f SUMMARY_FILE -o OUTPUT_FILE
```

For example, say we have a file named `summary.txt` and want to filter it by the taxonomy *Mammalia*. Then we can do so by running the following command:

```bash
python bridge.py -ft "Mammalia" -f "summary.txt" -o "filtered.txt"
```

## Known issues

- BLAST searches result in a CPU usage limit error
- Cannot search GenBank for large (~500) amounts of sequences at once

## Roadmap

- [] Add filtering capabilities for BLAST results
- [] Allow the user to search for a gene and species to run a BLAST search on
- [] Create a basic GUI to make the program more user-friendly
- [] Add support for aligning sequences
- [] Add support for phylogenetic tree generation

## Contributing

Contributions are welcome! If you run into a new issue, please create a new issue on the [issues](https://github.com/ashenafee/Bridge/issues) page. If you'd like to contribute to the project, please fork the repository and submit a pull request.

## Authors

- **Ashenafee Mandefro** - *Whole project* - [ashenafee](https://www.ashenafee.com/)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.