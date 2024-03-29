import os
from argparse import ArgumentParser

from align import Muscle
from blast import blastn, blast_by_species_and_symbol
from ensembl import Ensembl
from filter import filter_summary, filter_blast
from genbank import GenBank, GenBankDDL
from iq import Tree


def setup_parser() -> ArgumentParser:
    """
    Set up the argument parser.
    """
    parser = ArgumentParser(description='Run a BLAST search by downloading the '
                                        'sequence for the given symbol and '
                                        'species.')

    # Setup-related arguments
    parser.add_argument('-is', '--initial_setup', dest='initial_setup',
                        action='store_const', const=True, default=False,
                        required=False, help='Run the initial setup for the '
                                             'program.')
    parser.add_argument('-f', '--file', required=False,
                        help='The file to use in analysis.')
    parser.add_argument('-o', '--output', required=False,
                        help='The output file name.')

    # Query-related arguments
    parser.add_argument('-g', '--gene', required=False,
                        help='The gene to search for.')
    parser.add_argument('-s', '--species', required=False,
                        help='The species to search for.')
    parser.add_argument('-gb', dest='genbank', action='store_const',
                        const=True, default=False, required=False,
                        help='Specify for a GenBank search.')
    parser.add_argument('-es', dest='ensembl', action='store_const',
                        const=True, default=False, required=False,
                        help='Specify for a Ensembl search.')

    # BLAST arguments
    parser.add_argument('-b', dest='blast', action='store_const',
                        const=True, default=False, required=False,
                        help='The path to the BLAST file to use.')
    parser.add_argument('-bp', '--blast_params', required=False,
                        help='The parameters to use for the BLAST search. \
                            Only use with -b.')

    # Filtering arguments
    parser.add_argument('-ft', '--filter', required=False,
                        help='The lineage to filter the results by. \
                            Only use with -b.')
    parser.add_argument('-bf', dest='blast_filter', action='store_const',
                        const=True, default=False, required=False,
                        help='Specify to filter the BLAST results. \
                            Only use with -ft.')

    # Alignment arguments
    parser.add_argument('-a', '--align', required=False,
                        help='The algorithm to use for MSA.')
    parser.add_argument('-t', '--taxonomy', required=False,
                        help='The taxonomic rank to show distribution by. \
                            Only use with -a.')

    return parser


def _summary_filter_path(file: str, output: str) -> str:
    """
    Format the output path for the filtered summary file.
    :param file: The file to use.
    :param output: The output file name.
    """
    # Get absolute path of file
    file_path = os.path.abspath(file)

    # Get the directory of the file
    file_dir = os.path.dirname(file_path)

    # Combine the directory and the output file name
    output_path = os.path.join(file_dir, output)

    # See if the path ends in .txt
    if not output_path.endswith('.txt'):
        # Add .txt to the end of the path
        output_path += '.txt'

    return output_path


def main() -> None:
    """
    Run the main program.
    """
    parser = setup_parser()
    args = parser.parse_args()

    # Check if the user is running the initial setup
    if args.initial_setup:
        # Ask the user for their NCBI email
        email = input('Please enter your NCBI email: ')
        # Ask the user for their NCBI API key
        api_key = input('Please enter your NCBI API key: ')

        # Write the email and API key to the env file
        with open('.env', 'w') as f:
            f.write(f'EMAIL=\'{email}\'\nNCBI_API_KEY={api_key}')

        # Exit the program
        print('Setup complete. Please run the program again.')
        exit()

    # Check if some file output name is specified
    if args.blast or args.genbank or args.ensembl or args.filter or args.align:
        if not args.output:
            print('Please specify an output file name.')
            print('Use -o <output>')
            exit()

    # Check if the user is searching GenBank
    if args.genbank:
        if args.species and args.gene:
            # Split the species and gene(s) into a list (in-case multiple)
            genes = args.gene.split(',')
            species = args.species.split(',')

            # Search for the symbol in the GenBank database
            gb = GenBank(genes, species)
            data = gb.search()
            gb.summarize(args.output, data)
            gb.download(args.output)
        else:
            print('Please specify a species and gene to search for.')
            print('Use -s <species> -g <gene>')
            exit()

    # Check if the user is searching BLAST
    if args.blast:

        # Check if custom parameters have been specified
        params = None
        if args.blast_params:
            # Split the parameters by comma
            params = args.blast_params.split(',')
            # Make the parameters a dictionary
            params = {param.split('=')[0]: param.split('=')[1]
                      for param in params}

        if args.file:
            # User is searching by file
            if args.output:
                blastn(args.file, out=args.output, params=params)
            else:
                blastn(args.file, params=params)
        else:
            # User is searching by name and gene symbol
            if args.species and args.gene and args.output:
                genes = args.gene.split(',')
                species = args.species.split(',')

                blast_by_species_and_symbol(species, genes, output=args.output)

        exit()

    # Check if the user is searching Ensembl
    if args.ensembl:
        if args.species and args.gene:
            genes = args.gene.split(',')
            species = args.species.split(',')

            es = Ensembl(species=species, genes=genes)
            data = es.search()
            es.summarize(data, args.output)
            es.download(args.output)
        else:
            print('Please specify a species and gene to search for.')
            print('Use -s <species> -g <gene>')
            exit()

    # Check if the user is filtering the BLAST results
    if args.filter:
        if args.file:
            if args.blast_filter:
                # Open the BLAST results
                filtered = filter_blast(args.file, args.filter)

                # Download the filtered results
                gb = GenBankDDL(records=filtered)
                gb.download(filename=args.output)
            else:
                # Open the summary file
                with open(args.file, 'r') as f:
                    lines = f.readlines()

                # Filter the summary file
                lines = filter_summary(lines, args.filter)

                if args.output:
                    # Format where the output should go
                    output_name = _summary_filter_path(args.file, args.output)

                    with open(output_name, 'w') as f:
                        f.writelines(lines)
                else:
                    print(''.join(lines))
        else:
            print('No file specified.')
            print('Use -f <file>')
            exit()

    # Check if the user is aligning the sequences
    if args.align:

        # If a filter is not given, use the default
        if not args.filter:
            args.filter = 'order'

        # Check for the algorithm to use
        if args.align == 'muscle':
            # Setup MUSCLE
            muscle = Muscle(args.file, args.output)

            # Check if MUSCLE exists
            if not muscle.check_installed():
                # Install MUSCLE
                muscle.install_muscle()

            muscle.align()

            # Run the output through IQ-TREE
            tree = Tree(input=muscle.output, output=f"{muscle.output}-tree",
                        rank=args.taxonomy)

            # Check if IQ-TREE exists
            if not tree.check_installed():
                # Install IQ-TREE
                tree.install()

            tree.run()
        else:
            print('Please specify a valid alignment algorithm.')
            print('Valid algorithms: muscle')
            print('Use -a <algorithm>')
            exit()

    exit()


if __name__ == "__main__":
    main()
