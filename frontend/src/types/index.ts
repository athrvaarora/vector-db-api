// API Types matching the backend Pydantic models

export interface ChunkMetadata {
  source: string;
  created_at: string;
  updated_at: string;
  author?: string;
  tags: string[];
  language: string;
  char_count: number;
}

export interface Chunk {
  id: string;
  text: string;
  embedding: number[];
  metadata: ChunkMetadata;
  document_id: string;
}

export interface DocumentMetadata {
  title: string;
  description?: string;
  created_at: string;
  updated_at: string;
  author?: string;
  tags: string[];
  category?: string;
  file_type: string;
}

export interface Document {
  id: string;
  metadata: DocumentMetadata;
  library_id: string;
  chunk_ids: string[];
}

export interface LibraryMetadata {
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  owner?: string;
  tags: string[];
  is_public: boolean;
}

export interface Library {
  id: string;
  metadata: LibraryMetadata;
  document_ids: string[];
  is_indexed: boolean;
}

export interface SearchQuery {
  embedding: number[];
  k: number;
  metadata_filters?: Record<string, any>;
  similarity_threshold?: number;
}

export interface SearchResult {
  chunk: Chunk;
  similarity_score: number;
  document: Document;
}

export interface LibraryStats {
  total_documents: number;
  total_chunks: number;
  embedding_dimension?: number;
  index_type?: string;
  last_indexed?: string;
}

// Form types for creating/updating
export interface LibraryCreateForm {
  name: string;
  description?: string;
  owner?: string;
  tags: string[];
  is_public: boolean;
}

export interface DocumentCreateForm {
  title: string;
  description?: string;
  author?: string;
  tags: string[];
  category?: string;
  file_type: string;
  library_id: string;
}

export interface ChunkCreateForm {
  text: string;
  source: string;
  author?: string;
  tags: string[];
  document_id: string;
}

// Update types for editing
export interface DocumentUpdate {
  metadata?: DocumentMetadata;
}

export interface ChunkUpdate {
  text?: string;
  embedding?: number[];
  metadata?: ChunkMetadata;
}

// UI Types
export interface LoadingState {
  isLoading: boolean;
  error?: string;
}

export interface TableColumn<T> {
  key: keyof T | string;
  label: string;
  sortable?: boolean;
  render?: (item: T) => React.ReactNode;
}

export type IndexType = 'flat' | 'rp_lsh' | 'hierarchical';