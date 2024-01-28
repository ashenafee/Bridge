from fastapi import FastAPI
from routers import api

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Batch Download", version="0.1.0", summary="Batch download FASTA sequences from NCBI")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the API router
app.include_router(api.router, prefix="/api")

