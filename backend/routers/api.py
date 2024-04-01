from fastapi import APIRouter, Response
from fastapi.responses import FileResponse

from models import (DownloadRequest, DownloadResponse, SpeciesRequest,
                    SpeciesResponse)
from modules import (download_fasta, fetch_gene_ids, fetch_species,
                     taxon_name_to_id)

router = APIRouter()


@router.post("/get_species")
async def get_species(request_data: SpeciesRequest) -> SpeciesResponse:
    """
    Queries the NCBI for gene and sequence identifiers for all species falling
    under the given taxon name. The dictionary mapping species to their gene
    and sequence identifiers is returned.

    Args:
        request_data (SpeciesRequest): The taxon name and gene name to query.
    
    Returns:
        SpeciesResponse: A dictionary mapping species to their gene and sequence
        identifiers.
    """
    # Extract the taxon_name and gene_name from the request body.
    taxon_name = request_data.taxonName
    gene_name = request_data.geneName

    print(
        f"Fetching Gene/Sequence IDs for {gene_name}",
        f"for all species under {taxon_name}..."
    )

    # Convert the taxonomy query to a taxonomy ID.
    taxonomy_id = taxon_name_to_id(taxon_name)

    # Fetch the genes that fall under the given taxonomy ID.
    gene_ids = fetch_gene_ids(taxonomy_id, gene_name)

    # Fetch the species that each gene belongs to.
    species_ids = fetch_species(gene_ids)

    return SpeciesResponse(status="Download completed", species_ids=species_ids)


@router.post("/download")
async def download(request_data: DownloadRequest) -> Response:
    # Extract the species data from the request body.
    species_data = request_data.species_data

    print(
        f"Downloading FASTA files for each gene in the given species data..."
    )

    # Download the FASTA sequences for each gene.
    file_path = download_fasta(species_data)

    return FileResponse(file_path, media_type='application/octet-stream', filename='fasta_files.zip')