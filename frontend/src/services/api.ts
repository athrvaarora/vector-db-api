import axios from 'axios';
import { 
  Library, 
  Document, 
  Chunk, 
  LibraryStats, 
  SearchQuery, 
  SearchResult,
  LibraryCreateForm,
  DocumentCreateForm,
  ChunkCreateForm,
  DocumentUpdate,
  ChunkUpdate,
  IndexType
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Library API
export const libraryApi = {
  // Get all libraries
  getAll: async (): Promise<Library[]> => {
    const response = await api.get('/libraries');
    return response.data;
  },

  // Get library by ID
  getById: async (id: string): Promise<Library> => {
    const response = await api.get(`/libraries/${id}`);
    return response.data;
  },

  // Create new library
  create: async (library: LibraryCreateForm): Promise<Library> => {
    const response = await api.post('/libraries', {
      metadata: {
        ...library,
        tags: library.tags || [],
      }
    });
    return response.data;
  },

  // Update library
  update: async (id: string, library: Partial<LibraryCreateForm>): Promise<Library> => {
    const response = await api.put(`/libraries/${id}`, {
      metadata: {
        ...library,
        updated_at: new Date().toISOString(),
      }
    });
    return response.data;
  },

  // Delete library
  delete: async (id: string): Promise<void> => {
    await api.delete(`/libraries/${id}`);
  },

  // Get library statistics
  getStats: async (id: string): Promise<LibraryStats> => {
    const response = await api.get(`/libraries/${id}/stats`);
    return response.data;
  },

  // Index library
  index: async (id: string, indexType: IndexType = 'flat'): Promise<void> => {
    await api.post(`/libraries/${id}/index?index_type=${indexType}`);
  },

  // Search library
  search: async (id: string, query: SearchQuery): Promise<SearchResult[]> => {
    const response = await api.post(`/libraries/${id}/search`, query);
    return response.data;
  },
};

// Document API
export const documentApi = {
  // Get all documents
  getAll: async (): Promise<Document[]> => {
    const response = await api.get('/documents');
    return response.data;
  },

  // Get documents in library
  getByLibrary: async (libraryId: string): Promise<Document[]> => {
    const response = await api.get(`/libraries/${libraryId}/documents`);
    return response.data;
  },

  // Get document by ID
  getById: async (id: string): Promise<Document> => {
    const response = await api.get(`/documents/${id}`);
    return response.data;
  },

  // Create new document
  create: async (document: DocumentCreateForm): Promise<Document> => {
    const response = await api.post('/documents', {
      metadata: {
        title: document.title,
        description: document.description,
        author: document.author,
        tags: document.tags || [],
        category: document.category,
        file_type: document.file_type,
      },
      library_id: document.library_id,
    });
    return response.data;
  },

  // Update document
  update: async (id: string, document: DocumentUpdate): Promise<Document> => {
    const response = await api.put(`/documents/${id}`, document);
    return response.data;
  },

  // Delete document
  delete: async (id: string): Promise<void> => {
    await api.delete(`/documents/${id}`);
  },
};

// Chunk API
export const chunkApi = {
  // Get chunks in document
  getByDocument: async (documentId: string): Promise<Chunk[]> => {
    const response = await api.get(`/documents/${documentId}/chunks`);
    return response.data;
  },

  // Get chunk by ID
  getById: async (id: string): Promise<Chunk> => {
    const response = await api.get(`/chunks/${id}`);
    return response.data;
  },

  // Create new chunk
  create: async (chunk: ChunkCreateForm, embedding: number[]): Promise<Chunk> => {
    const response = await api.post('/chunks', {
      text: chunk.text,
      embedding: embedding,
      metadata: {
        source: chunk.source,
        author: chunk.author,
        tags: chunk.tags || [],
        language: 'en',
        char_count: chunk.text.length,
      },
      document_id: chunk.document_id,
    });
    return response.data;
  },

  // Update chunk
  update: async (id: string, chunk: ChunkUpdate): Promise<Chunk> => {
    const response = await api.put(`/chunks/${id}`, chunk);
    return response.data;
  },

  // Delete chunk
  delete: async (id: string): Promise<void> => {
    await api.delete(`/chunks/${id}`);
  },
};

// Health check
export const healthApi = {
  check: async (): Promise<{ status: string; service: string; version: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

// Utility function to generate embeddings via backend API
export const generateEmbedding = async (text: string): Promise<number[]> => {
  try {
    const response = await api.post('/embeddings', { text });
    return response.data.embedding;
  } catch (error) {
    console.error('Error generating embedding:', error);
    // Fallback to random embedding for demo purposes
    const dimension = 1024;
    const embedding = Array.from({ length: dimension }, () => Math.random() - 0.5);
    const norm = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0));
    return embedding.map(val => val / norm);
  }
};

export default api;