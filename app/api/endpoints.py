"""
FastAPI REST endpoints for the Vector Database.
Following RESTful API design principles and FastAPI best practices.
"""
from typing import List, Optional
from uuid import UUID
import os
import httpx

from fastapi import APIRouter, HTTPException, Query, status, Body
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from ..models.schemas import (
    Library, LibraryCreate, LibraryUpdate,
    Document, DocumentCreate, DocumentUpdate,
    Chunk, ChunkCreate, ChunkUpdate,
    SearchQuery, SearchResult, LibraryStats
)
from ..services.vector_service import VectorDatabaseService


# Global service instance (in production, use dependency injection)
vector_service = VectorDatabaseService()

# Create API router
router = APIRouter()


# Library Endpoints

@router.post("/libraries", response_model=Library, status_code=status.HTTP_201_CREATED, tags=["Libraries"])
async def create_library(library_data: LibraryCreate) -> Library:
    """Create a new library."""
    try:
        library = vector_service.create_library(library_data)
        return library
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create library: {str(e)}"
        )


@router.get("/libraries", response_model=List[Library], tags=["Libraries"])
async def list_libraries() -> List[Library]:
    """List all libraries."""
    try:
        return vector_service.list_libraries()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list libraries: {str(e)}"
        )


@router.get("/libraries/{library_id}", response_model=Library, tags=["Libraries"])
async def get_library(library_id: UUID) -> Library:
    """Get a library by ID."""
    library = vector_service.get_library(library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    return library


@router.put("/libraries/{library_id}", response_model=Library, tags=["Libraries"])
async def update_library(library_id: UUID, update_data: LibraryUpdate) -> Library:
    """Update a library."""
    library = vector_service.update_library(library_id, update_data)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    return library


@router.delete("/libraries/{library_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Libraries"])
async def delete_library(library_id: UUID) -> None:
    """Delete a library and all its contents."""
    success = vector_service.delete_library(library_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )


@router.get("/libraries/{library_id}/stats", response_model=LibraryStats, tags=["Libraries"])
async def get_library_stats(library_id: UUID) -> LibraryStats:
    """Get statistics for a library."""
    stats = vector_service.get_library_stats(library_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    return stats


# Document Endpoints

@router.get("/documents", response_model=List[Document], tags=["Documents"])
async def list_all_documents() -> List[Document]:
    """List all documents across all libraries."""
    libraries = vector_service.list_libraries()
    all_documents = []
    for library in libraries:
        documents = vector_service.list_documents(library.id)
        all_documents.extend(documents)
    return all_documents


@router.post("/documents", response_model=Document, status_code=status.HTTP_201_CREATED, tags=["Documents"])
async def create_document(document_data: DocumentCreate) -> Document:
    """Create a new document in a library."""
    document = vector_service.create_document(document_data)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    return document


@router.get("/libraries/{library_id}/documents", response_model=List[Document], tags=["Documents"])
async def list_documents(library_id: UUID) -> List[Document]:
    """List all documents in a library."""
    # Verify library exists
    if not vector_service.get_library(library_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    return vector_service.list_documents(library_id)


@router.get("/documents/{document_id}", response_model=Document, tags=["Documents"])
async def get_document(document_id: UUID) -> Document:
    """Get a document by ID."""
    document = vector_service.get_document(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document


@router.put("/documents/{document_id}", response_model=Document, tags=["Documents"])
async def update_document(document_id: UUID, update_data: DocumentUpdate) -> Document:
    """Update a document."""
    document = vector_service.update_document(document_id, update_data)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Documents"])
async def delete_document(document_id: UUID) -> None:
    """Delete a document and all its chunks."""
    success = vector_service.delete_document(document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )


# Chunk Endpoints

@router.post("/chunks", response_model=Chunk, status_code=status.HTTP_201_CREATED, tags=["Chunks"])
async def create_chunk(chunk_data: ChunkCreate) -> Chunk:
    """Create a new chunk in a document."""
    chunk = vector_service.create_chunk(chunk_data)
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return chunk


@router.get("/documents/{document_id}/chunks", response_model=List[Chunk], tags=["Chunks"])
async def list_chunks(document_id: UUID) -> List[Chunk]:
    """List all chunks in a document."""
    # Verify document exists
    if not vector_service.get_document(document_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return vector_service.list_chunks(document_id)


@router.get("/chunks/{chunk_id}", response_model=Chunk, tags=["Chunks"])
async def get_chunk(chunk_id: UUID) -> Chunk:
    """Get a chunk by ID."""
    chunk = vector_service.get_chunk(chunk_id)
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chunk not found"
        )
    return chunk


@router.put("/chunks/{chunk_id}", response_model=Chunk, tags=["Chunks"])
async def update_chunk(chunk_id: UUID, update_data: ChunkUpdate) -> Chunk:
    """Update a chunk."""
    chunk = vector_service.update_chunk(chunk_id, update_data)
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chunk not found"
        )
    return chunk


@router.delete("/chunks/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Chunks"])
async def delete_chunk(chunk_id: UUID) -> None:
    """Delete a chunk."""
    success = vector_service.delete_chunk(chunk_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chunk not found"
        )


# Indexing and Search Endpoints

@router.post("/libraries/{library_id}/index", status_code=status.HTTP_200_OK, tags=["Indexing"])
async def index_library(
    library_id: UUID,
    index_type: str = Query(default="flat", regex="^(flat|rp_lsh|hierarchical)$")
) -> JSONResponse:
    """Index a library with the specified algorithm."""
    # Verify library exists
    if not vector_service.get_library(library_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    
    try:
        success = vector_service.index_library(library_id, index_type)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to index library"
            )
        
        return JSONResponse(
            content={"message": f"Library indexed successfully with {index_type} algorithm"},
            status_code=status.HTTP_200_OK
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index library: {str(e)}"
        )


@router.post("/libraries/{library_id}/search", response_model=List[SearchResult], tags=["Search"])
async def search_library(library_id: UUID, query: SearchQuery) -> List[SearchResult]:
    """Search a library for similar chunks."""
    # Verify library exists
    if not vector_service.get_library(library_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    
    try:
        results = vector_service.search_library(library_id, query)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search library: {str(e)}"
        )


# Generate Embedding Endpoint

@router.post("/embeddings", status_code=status.HTTP_200_OK, tags=["Utilities"])
async def generate_embedding(request: dict) -> JSONResponse:
    """Generate embedding for search text using Cohere API."""
    import httpx
    
    # Extract text from request
    text = request.get("text")
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text field is required"
        )
    
    # Get API key from environment variables
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    if not COHERE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="COHERE_API_KEY environment variable not set. Please configure your API key."
        )
    
    COHERE_API_URL = "https://api.cohere.ai/v1/embed"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                COHERE_API_URL,
                headers={
                    "Authorization": f"Bearer {COHERE_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "texts": [text],
                    "model": "embed-english-v3.0",
                    "input_type": "search_query"
                },
                timeout=30.0
            )
            response.raise_for_status()
            
            data = response.json()
            return JSONResponse(
                content={"embedding": data["embeddings"][0]},
                status_code=status.HTTP_200_OK
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embedding: {str(e)}"
        )


# Health Check Endpoint

@router.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "vector-database",
            "version": "1.0.0"
        },
        status_code=status.HTTP_200_OK
    )