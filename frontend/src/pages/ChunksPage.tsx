import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ChevronLeftIcon,
  DocumentTextIcon,
  TagIcon,
  UserIcon,
  ClockIcon,
  PlusIcon,
} from '@heroicons/react/24/outline';
import { Chunk, Document, ChunkUpdate } from '../types';
import { chunkApi, documentApi } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import CreateChunkModal from '../components/CreateChunkModal';
import EditChunkModal from '../components/EditChunkModal';

const ChunksPage: React.FC = () => {
  const { documentId } = useParams<{ documentId: string }>();
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [document, setDocument] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedChunks, setExpandedChunks] = useState<Set<string>>(new Set());
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingChunk, setEditingChunk] = useState<Chunk | null>(null);

  useEffect(() => {
    if (documentId) {
      loadDocumentAndChunks();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [documentId]);

  const loadDocumentAndChunks = async () => {
    if (!documentId) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const [documentData, chunksData] = await Promise.all([
        documentApi.getById(documentId),
        chunkApi.getByDocument(documentId)
      ]);
      
      setDocument(documentData);
      setChunks(chunksData);
    } catch (err: any) {
      console.error('Error loading document and chunks:', err);
      if (err.response?.status === 404) {
        setError('Document not found. It may have been deleted or the link is outdated.');
      } else {
        setError(err.response?.data?.detail || 'Failed to load chunks');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteChunk = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this chunk? This action cannot be undone.')) {
      return;
    }

    try {
      await chunkApi.delete(id);
      loadDocumentAndChunks();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete chunk');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const truncateText = (text: string, maxLength: number = 300) => {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
  };

  const toggleExpandChunk = (chunkId: string) => {
    const newExpanded = new Set(expandedChunks);
    if (newExpanded.has(chunkId)) {
      newExpanded.delete(chunkId);
    } else {
      newExpanded.add(chunkId);
    }
    setExpandedChunks(newExpanded);
  };

  const handleCreateChunk = async (chunkData: any, embedding: number[]) => {
    try {
      await chunkApi.create(chunkData, embedding);
      setShowCreateModal(false);
      loadDocumentAndChunks();
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to create chunk');
    }
  };

  const handleEditChunk = (chunk: Chunk) => {
    setEditingChunk(chunk);
    setShowEditModal(true);
  };

  const handleUpdateChunk = async (chunkId: string, updateData: ChunkUpdate) => {
    try {
      await chunkApi.update(chunkId, updateData);
      setShowEditModal(false);
      setEditingChunk(null);
      loadDocumentAndChunks();
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to update chunk');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        {document ? (
          <div className="flex items-center space-x-2">
            <Link
              to="/documents"
              className="text-gray-400 hover:text-gray-600"
            >
              <ChevronLeftIcon className="h-5 w-5" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {document.metadata.title}
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                Chunks in this document
              </p>
            </div>
          </div>
        ) : (
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Chunks</h1>
            <p className="mt-1 text-sm text-gray-500">
              Document chunks
            </p>
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <ErrorMessage
          message={error}
          onRetry={loadDocumentAndChunks}
        />
      )}

      {/* Content */}
      {chunks.length === 0 ? (
                  <div className="text-center py-12">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No chunks</h3>
            <p className="mt-1 text-sm text-gray-500">
              This document doesn't contain any chunks yet.
            </p>
            <div className="mt-6">
              <button
                type="button"
                className="btn-primary"
                onClick={() => setShowCreateModal(true)}
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Add Chunk
              </button>
            </div>
          </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium text-gray-900">
              Chunks ({chunks.length})
            </h2>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500">
                Vector dimension: {chunks[0]?.embedding.length || 'N/A'}
              </div>
              <button
                type="button"
                className="btn-primary"
                onClick={() => setShowCreateModal(true)}
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Add Chunk
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {chunks.map((chunk, index) => (
              <div
                key={chunk.id}
                className="card hover:shadow-md transition-shadow duration-200"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    {/* Chunk number and source */}
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-sm font-medium text-gray-900">
                        Chunk #{index + 1}
                      </span>
                      <span className="text-sm text-gray-500">
                        Source: {chunk.metadata.source}
                      </span>
                    </div>

                    {/* Chunk content */}
                    <div className="mt-2">
                      <p className="text-sm text-gray-900 leading-relaxed whitespace-pre-wrap">
                        {expandedChunks.has(chunk.id) ? chunk.text : truncateText(chunk.text)}
                      </p>
                    </div>

                    {/* Metadata */}
                    <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-gray-500">
                      <div className="flex items-center">
                        <ClockIcon className="h-3 w-3 mr-1" />
                        {formatDate(chunk.metadata.created_at)}
                      </div>
                      {chunk.metadata.author && (
                        <div className="flex items-center">
                          <UserIcon className="h-3 w-3 mr-1" />
                          {chunk.metadata.author}
                        </div>
                      )}
                      <div className="flex items-center">
                        <span className="mr-1">Length:</span>
                        {chunk.metadata.char_count} chars
                      </div>
                      <div className="flex items-center">
                        <span className="mr-1">Language:</span>
                        {chunk.metadata.language}
                      </div>
                      <div className="flex items-center">
                        <span className="mr-1">Embedding:</span>
                        {chunk.embedding.length}D
                      </div>
                    </div>

                    {/* Tags */}
                    {chunk.metadata.tags.length > 0 && (
                      <div className="mt-2 flex items-center space-x-1">
                        <TagIcon className="h-3 w-3 text-gray-400" />
                        <div className="flex flex-wrap gap-1">
                          {chunk.metadata.tags.map((tag) => (
                            <span
                              key={tag}
                              className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="mt-4 flex items-center justify-between">
                  <div className="flex space-x-3">
                    {chunk.text.length > 300 && (
                      <button
                        onClick={() => toggleExpandChunk(chunk.id)}
                        className="text-primary-600 hover:text-primary-500 text-sm font-medium"
                      >
                        {expandedChunks.has(chunk.id) ? 'Collapse' : 'Expand'}
                      </button>
                    )}
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEditChunk(chunk)}
                      className="text-gray-600 hover:text-gray-500 text-sm font-medium"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteChunk(chunk.id)}
                      className="text-red-600 hover:text-red-500 text-sm font-medium"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Create Chunk Modal */}
      {showCreateModal && documentId && (
        <CreateChunkModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateChunk}
          documentId={documentId}
        />
      )}

      {/* Edit Chunk Modal */}
      {showEditModal && editingChunk && (
        <EditChunkModal
          isOpen={showEditModal}
          onClose={() => {
            setShowEditModal(false);
            setEditingChunk(null);
          }}
          onUpdate={handleUpdateChunk}
          chunk={editingChunk}
        />
      )}
    </div>
  );
};

export default ChunksPage;