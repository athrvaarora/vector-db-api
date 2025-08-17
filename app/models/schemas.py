"""
Pydantic models for Vector Database entities.
Following SOLID principles and domain-driven design.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class ChunkMetadata(BaseModel):
    """Metadata for a chunk."""
    model_config = ConfigDict(extra="forbid")
    
    source: str = Field(..., description="Source of the chunk")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    language: str = "en"
    char_count: int = Field(ge=0)


class ChunkCreate(BaseModel):
    """Schema for creating a chunk."""
    model_config = ConfigDict(extra="forbid")
    
    text: str = Field(..., min_length=1, max_length=10000)
    embedding: List[float] = Field(..., min_length=1)
    metadata: ChunkMetadata
    document_id: UUID


class ChunkUpdate(BaseModel):
    """Schema for updating a chunk."""
    model_config = ConfigDict(extra="forbid")
    
    text: Optional[str] = Field(None, min_length=1, max_length=10000)
    embedding: Optional[List[float]] = Field(None, min_length=1)
    metadata: Optional[ChunkMetadata] = None


class Chunk(BaseModel):
    """Complete chunk model."""
    model_config = ConfigDict(extra="forbid")
    
    id: UUID = Field(default_factory=uuid4)
    text: str
    embedding: List[float]
    metadata: ChunkMetadata
    document_id: UUID


class DocumentMetadata(BaseModel):
    """Metadata for a document."""
    model_config = ConfigDict(extra="forbid")
    
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    file_type: str = "text"


class DocumentCreate(BaseModel):
    """Schema for creating a document."""
    model_config = ConfigDict(extra="forbid")
    
    metadata: DocumentMetadata
    library_id: UUID


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""
    model_config = ConfigDict(extra="forbid")
    
    metadata: Optional[DocumentMetadata] = None


class Document(BaseModel):
    """Complete document model."""
    model_config = ConfigDict(extra="forbid")
    
    id: UUID = Field(default_factory=uuid4)
    metadata: DocumentMetadata
    library_id: UUID
    chunk_ids: List[UUID] = Field(default_factory=list)


class LibraryMetadata(BaseModel):
    """Metadata for a library."""
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    owner: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_public: bool = False


class LibraryCreate(BaseModel):
    """Schema for creating a library."""
    model_config = ConfigDict(extra="forbid")
    
    metadata: LibraryMetadata


class LibraryUpdate(BaseModel):
    """Schema for updating a library."""
    model_config = ConfigDict(extra="forbid")
    
    metadata: Optional[LibraryMetadata] = None


class Library(BaseModel):
    """Complete library model."""
    model_config = ConfigDict(extra="forbid")
    
    id: UUID = Field(default_factory=uuid4)
    metadata: LibraryMetadata
    document_ids: List[UUID] = Field(default_factory=list)
    is_indexed: bool = False


class SearchQuery(BaseModel):
    """Schema for vector search queries."""
    model_config = ConfigDict(extra="forbid")
    
    embedding: List[float] = Field(..., min_length=1)
    k: int = Field(default=10, ge=1, le=100)
    metadata_filters: Optional[Dict[str, Any]] = None
    similarity_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    """Schema for search results."""
    model_config = ConfigDict(extra="forbid")
    
    chunk: Chunk
    similarity_score: float = Field(ge=-1.0, le=1.1)  # Allow small floating point precision errors
    document: Document


class LibraryStats(BaseModel):
    """Statistics for a library."""
    model_config = ConfigDict(extra="forbid")
    
    total_documents: int = Field(ge=0)
    total_chunks: int = Field(ge=0)
    embedding_dimension: Optional[int] = Field(None, ge=1)
    index_type: Optional[str] = None
    last_indexed: Optional[datetime] = None