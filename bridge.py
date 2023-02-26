from genbank import GenBank, GenBankDDL
from argparse import ArgumentParser
from blast import blastn
from ensembl import Ensembl
from filter import filter_summary, filter_blast
import os


def setup_parser() -> ArgumentParser:
    """
    Setup the argument parser.
    :return:
    """
    parser = ArgumentParser(description='Run a BLAST search by downloading the '
                                        'sequence for the given symbol and '
                                        'species.')
    parser.add_argument('-f', '--file', required=False,
                        help='The file to use in analysis.')
    parser.add_argument('-o', '--output', required=False,
                        help='The output file name.')
    parser.add_argument('-g', '--gene', required=False,
                        help='The gene to search for.')
    parser.add_argument('-s', '--species', required=False,
                        help='The species to search for.')
    parser.add_argument('-b', dest='blast', action='store_const', 
                        const=True, default=False, required=False,
                        help='The path to the BLAST file to use.')
    parser.add_argument('-bp', '--blast_params', required=False,
                        help='The parameters to use for the BLAST search. \
                            Only use with -b.')
    parser.add_argument('-gb', dest='genbank', action='store_const',
                        const=True, default=False, required=False,
                        help='Specify for a GenBank search.')
    parser.add_argument('-es', dest='ensembl', action='store_const',
                        const=True, default=False, required=False,
                        help='Specify for a Ensembl search.')
    parser.add_argument('-ft', '--filter', required=False,
                        help='The lineage to filter the results by. \
                            Only use with -b.')
    parser.add_argument('-bf', dest='blast_filter', action='store_const',
                        const=True, default=False, required=False,
                        help='Specify to filter the BLAST results. \
                            Only use with -ft.')

    return parser


def main() -> None:
    """
    Run the main program.
    """
    parser = setup_parser()
    args = parser.parse_args()

    if args.genbank:

        if args.species and args.gene:
            genes = args.gene.split(',')
            species = args.species.split(',')
            
            gb = GenBank(genes, species)
            data = gb.search()
            gb.summarize(args.output, data)
            gb.download(args.output)

    if args.blast:

        # Check if custom parameters have been specified
        params = {}
        
        if args.blast_params:
            # Split the parameters by comma
            params = args.blast_params.split(',')
            # Make the parameters a dictionary
            params = {param.split('=')[0]: param.split('=')[1] 
                      for param in params}

        if args.file:
            blastn(args.file, out=args.output, params=params)
        else:
            exit()
    
    if args.ensembl: # TODO: Test
            
            if args.species and args.gene:
                genes = args.gene.split(',')
                species = args.species.split(',')
                
                es = Ensembl(species=species, genes=genes)
                data = es.search()
                es.summarize(data, args.output)
                es.download(args.output)
    
    if args.filter:
        if args.file:

            if args.blast_filter:
                # Open the BLAST results
                filtered = filter_blast(args.file, args.filter)

                # Download the filtered results
                gb = GenBankDDL(records=filtered)
                gb.download(filename=args.output)

            else:

                with open(args.file, 'r') as f:
                    lines = f.readlines()
                
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
    
    # Exit the program
    exit()


def _summary_filter_path(file: str, output: str) -> str:
    """
    Format the output path for the filtered summaryf ile.
    :param file: The file to use.
    :param output: The output file name.
    :return: The output path.
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


if __name__ == "__main__":
    main()
