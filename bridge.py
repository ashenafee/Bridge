from genbank import GenBank
from argparse import ArgumentParser
from blast import blastn
from ensembl import Ensembl
from filter import filter_summary
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
    parser.add_argument('-gb', dest='genbank', action='store_const',
                        const=True, default=False, required=False,
                        help='Specify for a GenBank search.')
    parser.add_argument('-es', dest='ensembl', action='store_const',
                        const=True, default=False, required=False,
                        help='Specify for a Ensembl search.')
    parser.add_argument('-ft', '--filter', required=False,
                        help='The lineage to filter the results by. \
                            Only use with -b.')

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

        if args.file:
            blastn(args.file, out=args.output)
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
        # Filter option has been specified
        if args.file:
            # File has been specified
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
