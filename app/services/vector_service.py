"""
Vector Database Service Layer.
Implements business logic following Domain-Driven Design principles.
"""
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from ..domain.rwlock import ReadWriteLock, DatabaseSnapshot
from ..index.base import VectorIndex
from ..index.flat import FlatIndex
from ..index.rplsh import RPLSHIndex
from ..index.metrics import HierarchicalIndex
from ..models.schemas import (
    Chunk, ChunkCreate, ChunkUpdate,
    Document, DocumentCreate, DocumentUpdate,
    Library, LibraryCreate, LibraryUpdate,
    SearchQuery, SearchResult, LibraryStats
)


class VectorDatabaseService:
    """
    Main service for vector database operations.
    
    Implements the business logic layer with proper separation of concerns.
    Uses read-write locks for thread safety and supports multiple indexing algorithms.
    """
    
    def __init__(self) -> None:
        # Thread-safe storage
        self._libraries: Dict[UUID, Library] = {}
        self._documents: Dict[UUID, Document] = {}
        self._chunks: Dict[UUID, Chunk] = {}
        
        # Indexes for each library
        self._library_indexes: Dict[UUID, VectorIndex] = {}
        
        # Thread safety
        self._lock = ReadWriteLock()
        
        # Supported index types
        self._index_types = {
            "flat": FlatIndex,
            "rp_lsh": RPLSHIndex,
            "hierarchical": HierarchicalIndex
        }
    
    # Library CRUD Operations
    
    def create_library(self, library_data: LibraryCreate) -> Library:
        """Create a new library."""
        with self._lock.write_lock():
            library = Library(metadata=library_data.metadata)
            self._libraries[library.id] = library
            return library
    
    def get_library(self, library_id: UUID) -> Optional[Library]:
        """Get a library by ID."""
        with self._lock.read_lock():
            return self._libraries.get(library_id)
    
    def list_libraries(self) -> List[Library]:
        """List all libraries."""
        with self._lock.read_lock():
            return list(self._libraries.values())
    
    def update_library(self, library_id: UUID, update_data: LibraryUpdate) -> Optional[Library]:
        """Update a library."""
        with self._lock.write_lock():
            if library_id not in self._libraries:
                return None
            
            library = self._libraries[library_id]
            if update_data.metadata:
                # Update timestamp
                update_data.metadata.updated_at = datetime.utcnow()
                library.metadata = update_data.metadata
            
            return library
    
    def delete_library(self, library_id: UUID) -> bool:
        """Delete a library and all its contents."""
        with self._lock.write_lock():
            if library_id not in self._libraries:
                return False
            
            library = self._libraries[library_id]
            
            # Delete all documents and chunks
            for doc_id in library.document_ids.copy():
                self._delete_document_internal(doc_id)
            
            # Clean up index
            if library_id in self._library_indexes:
                del self._library_indexes[library_id]
            
            # Delete library
            del self._libraries[library_id]
            return True
    
    # Document CRUD Operations
    
    def create_document(self, document_data: DocumentCreate) -> Optional[Document]:
        """Create a new document in a library."""
        with self._lock.write_lock():
            if document_data.library_id not in self._libraries:
                return None
            
            document = Document(
                metadata=document_data.metadata,
                library_id=document_data.library_id
            )
            
            self._documents[document.id] = document
            
            # Add to library
            library = self._libraries[document_data.library_id]
            library.document_ids.append(document.id)
            library.is_indexed = False  # Mark as needing reindexing
            
            return document
    
    def get_document(self, document_id: UUID) -> Optional[Document]:
        """Get a document by ID."""
        with self._lock.read_lock():
            return self._documents.get(document_id)
    
    def list_documents(self, library_id: UUID) -> List[Document]:
        """List all documents in a library."""
        with self._lock.read_lock():
            if library_id not in self._libraries:
                return []
            
            library = self._libraries[library_id]
            return [self._documents[doc_id] for doc_id in library.document_ids 
                   if doc_id in self._documents]
    
    def update_document(self, document_id: UUID, update_data: DocumentUpdate) -> Optional[Document]:
        """Update a document."""
        with self._lock.write_lock():
            if document_id not in self._documents:
                return None
            
            document = self._documents[document_id]
            if update_data.metadata:
                update_data.metadata.updated_at = datetime.utcnow()
                document.metadata = update_data.metadata
                
                # Mark library as needing reindexing
                if document.library_id in self._libraries:
                    self._libraries[document.library_id].is_indexed = False
            
            return document
    
    def delete_document(self, document_id: UUID) -> bool:
        """Delete a document and all its chunks."""
        with self._lock.write_lock():
            return self._delete_document_internal(document_id)
    
    def _delete_document_internal(self, document_id: UUID) -> bool:
        """Internal method to delete document (assumes write lock held)."""
        if document_id not in self._documents:
            return False
        
        document = self._documents[document_id]
        
        # Delete all chunks
        for chunk_id in document.chunk_ids.copy():
            self._delete_chunk_internal(chunk_id)
        
        # Remove from library
        if document.library_id in self._libraries:
            library = self._libraries[document.library_id]
            if document_id in library.document_ids:
                library.document_ids.remove(document_id)
            library.is_indexed = False
        
        # Delete document
        del self._documents[document_id]
        return True
    
    # Chunk CRUD Operations
    
    def create_chunk(self, chunk_data: ChunkCreate) -> Optional[Chunk]:
        """Create a new chunk in a document."""
        with self._lock.write_lock():
            if chunk_data.document_id not in self._documents:
                return None
            
            # Update char count in metadata
            chunk_data.metadata.char_count = len(chunk_data.text)
            
            chunk = Chunk(
                text=chunk_data.text,
                embedding=chunk_data.embedding,
                metadata=chunk_data.metadata,
                document_id=chunk_data.document_id
            )
            
            self._chunks[chunk.id] = chunk
            
            # Add to document
            document = self._documents[chunk_data.document_id]
            document.chunk_ids.append(chunk.id)
            
            # Mark library as needing reindexing
            if document.library_id in self._libraries:
                self._libraries[document.library_id].is_indexed = False
            
            return chunk
    
    def get_chunk(self, chunk_id: UUID) -> Optional[Chunk]:
        """Get a chunk by ID."""
        with self._lock.read_lock():
            return self._chunks.get(chunk_id)
    
    def list_chunks(self, document_id: UUID) -> List[Chunk]:
        """List all chunks in a document."""
        with self._lock.read_lock():
            if document_id not in self._documents:
                return []
            
            document = self._documents[document_id]
            return [self._chunks[chunk_id] for chunk_id in document.chunk_ids 
                   if chunk_id in self._chunks]
    
    def update_chunk(self, chunk_id: UUID, update_data: ChunkUpdate) -> Optional[Chunk]:
        """Update a chunk."""
        with self._lock.write_lock():
            if chunk_id not in self._chunks:
                return None
            
            chunk = self._chunks[chunk_id]
            updated = False
            
            if update_data.text is not None:
                chunk.text = update_data.text
                updated = True
            
            if update_data.embedding is not None:
                chunk.embedding = update_data.embedding
                updated = True
            
            if update_data.metadata is not None:
                update_data.metadata.updated_at = datetime.utcnow()
                if update_data.text is not None:
                    update_data.metadata.char_count = len(update_data.text)
                chunk.metadata = update_data.metadata
                updated = True
            
            if updated:
                # Mark library as needing reindexing
                document = self._documents.get(chunk.document_id)
                if document and document.library_id in self._libraries:
                    self._libraries[document.library_id].is_indexed = False
            
            return chunk
    
    def delete_chunk(self, chunk_id: UUID) -> bool:
        """Delete a chunk."""
        with self._lock.write_lock():
            return self._delete_chunk_internal(chunk_id)
    
    def _delete_chunk_internal(self, chunk_id: UUID) -> bool:
        """Internal method to delete chunk (assumes write lock held)."""
        if chunk_id not in self._chunks:
            return False
        
        chunk = self._chunks[chunk_id]
        
        # Remove from document
        if chunk.document_id in self._documents:
            document = self._documents[chunk.document_id]
            if chunk_id in document.chunk_ids:
                document.chunk_ids.remove(chunk_id)
            
            # Mark library as needing reindexing
            if document.library_id in self._libraries:
                self._libraries[document.library_id].is_indexed = False
                
                # Remove from index if exists
                if document.library_id in self._library_indexes:
                    self._library_indexes[document.library_id].remove_vector(chunk_id)
        
        # Delete chunk
        del self._chunks[chunk_id]
        return True
    
    # Indexing Operations
    
    def index_library(self, library_id: UUID, index_type: str = "flat") -> bool:
        """Index a library with the specified algorithm."""
        with self._lock.write_lock():
            if library_id not in self._libraries:
                return False
            
            if index_type not in self._index_types:
                raise ValueError(f"Unsupported index type: {index_type}")
            
            library = self._libraries[library_id]
            
            # Collect all chunks in the library
            all_chunks = []
            for doc_id in library.document_ids:
                if doc_id in self._documents:
                    document = self._documents[doc_id]
                    for chunk_id in document.chunk_ids:
                        if chunk_id in self._chunks:
                            all_chunks.append(self._chunks[chunk_id])
            
            if not all_chunks:
                return True  # Empty library is considered indexed
            
            # Determine embedding dimension
            dimension = len(all_chunks[0].embedding)
            
            # Create new index
            IndexClass = self._index_types[index_type]
            if index_type == "rp_lsh":
                index = IndexClass(dimension, num_hashes=16, num_bits=8)
            elif index_type == "hierarchical":
                index = IndexClass(dimension, max_connections=16, max_layers=5)
            else:
                index = IndexClass(dimension)
            
            # Add all chunks to index
            for chunk in all_chunks:
                index.add_vector(chunk.embedding, chunk.id)
            
            # Store index and mark library as indexed
            self._library_indexes[library_id] = index
            library.is_indexed = True
            
            return True
    
    def search_library(self, library_id: UUID, query: SearchQuery) -> List[SearchResult]:
        """Search a library for similar chunks."""
        with self._lock.read_lock():
            if library_id not in self._libraries:
                return []
            
            if library_id not in self._library_indexes:
                return []  # Library not indexed
            
            index = self._library_indexes[library_id]
            
            # Perform vector search
            results = index.search(query.embedding, query.k)
            
            # Build search results
            search_results = []
            for chunk_id, similarity in results:
                if chunk_id in self._chunks:
                    chunk = self._chunks[chunk_id]
                    
                    # Apply similarity threshold if specified
                    if query.similarity_threshold and similarity < query.similarity_threshold:
                        continue
                    
                    # Apply metadata filters if specified
                    if query.metadata_filters and not self._matches_filters(chunk, query.metadata_filters):
                        continue
                    
                    # Get document
                    document = self._documents.get(chunk.document_id)
                    if document:
                        search_results.append(SearchResult(
                            chunk=chunk,
                            similarity_score=similarity,
                            document=document
                        ))
            
            return search_results
    
    def get_library_stats(self, library_id: UUID) -> Optional[LibraryStats]:
        """Get statistics for a library."""
        with self._lock.read_lock():
            if library_id not in self._libraries:
                return None
            
            library = self._libraries[library_id]
            
            # Count documents and chunks
            total_documents = len(library.document_ids)
            total_chunks = 0
            embedding_dimension = None
            
            for doc_id in library.document_ids:
                if doc_id in self._documents:
                    document = self._documents[doc_id]
                    total_chunks += len(document.chunk_ids)
                    
                    # Get embedding dimension from first chunk
                    if embedding_dimension is None:
                        for chunk_id in document.chunk_ids:
                            if chunk_id in self._chunks:
                                chunk = self._chunks[chunk_id]
                                embedding_dimension = len(chunk.embedding)
                                break
            
            # Get index info
            index_type = None
            last_indexed = None
            if library_id in self._library_indexes:
                index = self._library_indexes[library_id]
                stats = index.get_stats()
                index_type = stats.get("type")
                last_indexed = library.metadata.updated_at
            
            return LibraryStats(
                total_documents=total_documents,
                total_chunks=total_chunks,
                embedding_dimension=embedding_dimension,
                index_type=index_type,
                last_indexed=last_indexed
            )
    
    def _matches_filters(self, chunk: Chunk, filters: Dict) -> bool:
        """Check if a chunk matches the given metadata filters."""
        # Simple implementation - can be extended
        for key, value in filters.items():
            if key == "tags":
                if not any(tag in chunk.metadata.tags for tag in value):
                    return False
            elif key == "author":
                if chunk.metadata.author != value:
                    return False
            elif key == "language":
                if chunk.metadata.language != value:
                    return False
            elif key == "created_after":
                if chunk.metadata.created_at <= value:
                    return False
            elif key == "created_before":
                if chunk.metadata.created_at >= value:
                    return False
        
        return True