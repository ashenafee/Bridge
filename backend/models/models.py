from typing import Dict, List

from pydantic import BaseModel


class Identifier(BaseModel):
    txid: str
    gene_id: str
    nuc_id: str


class SpeciesRequest(BaseModel):
    taxonName: str
    geneName: str


class SpeciesResponse(BaseModel):
    status: str
    species_ids: Dict[str, List[Identifier]]


class DownloadRequest(BaseModel):
    species_data: Dict[str, List[Identifier]]


class DownloadResponse(BaseModel):
    status: str