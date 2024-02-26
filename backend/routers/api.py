from fastapi import APIRouter
from modules import taxon_name_to_id, fetch_gene_ids, fetch_species, download_fasta, concatenate_fasta
from pydantic import BaseModel


router = APIRouter()


class DownloadRequest(BaseModel):
    taxonName: str
    geneName: str


@router.post("/download")
async def download(request_data: DownloadRequest):
    # Extract the taxon_name and gene_name from the request body.
    taxon_name = request_data.taxonName
    gene_name = request_data.geneName

    print(f"Downloading FASTA sequences for {gene_name} from {taxon_name}...")

    # Convert the taxonomy query to a taxonomy ID.
    taxonomy_id = taxon_name_to_id(taxon_name)

    # Fetch the genes that fall under the given taxonomy ID.
    gene_ids = fetch_gene_ids(taxonomy_id, gene_name)

    # Fetch the species that each gene belongs to.
    species_ids = fetch_species(gene_ids)

    # Download the FASTA sequences for each gene.
    download_fasta(species_ids)

    # Concatenate the FASTAs into one FASTA file.
    concatenate_fasta()

    return {"status": "Download completed"}