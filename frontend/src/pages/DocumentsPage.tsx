import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  PlusIcon,
  DocumentIcon,
  ChevronLeftIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  ClockIcon,
  UserIcon,

  DocumentTextIcon,
  ArchiveBoxIcon,
} from '@heroicons/react/24/outline';
import { Document, Library, DocumentUpdate } from '../types';
import { documentApi, libraryApi } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import CreateDocumentModal from '../components/CreateDocumentModal';
import EditDocumentModal from '../components/EditDocumentModal';
import Button from '../components/Button';

const DocumentsPage: React.FC = () => {
  const { libraryId } = useParams<{ libraryId: string }>();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [library, setLibrary] = useState<Library | null>(null);
  const [libraries, setLibraries] = useState<Library[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingDocument, setEditingDocument] = useState<Document | null>(null);

  useEffect(() => {
    if (libraryId) {
      loadLibraryAndDocuments();
    } else {
      loadAllDocuments();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [libraryId]);

  const loadLibraryAndDocuments = async () => {
    if (!libraryId) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const [libraryData, documentsData] = await Promise.all([
        libraryApi.getById(libraryId),
        documentApi.getByLibrary(libraryId)
      ]);
      
      setLibrary(libraryData);
      setDocuments(documentsData);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('Library not found. It may have been deleted.');
      } else {
        setError(err.response?.data?.detail || 'Failed to load library and documents');
      }
    } finally {
      setLoading(false);
    }
  };

  const loadAllDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [documentsData, librariesData] = await Promise.all([
        documentApi.getAll(),
        libraryApi.getAll()
      ]);
      
      setDocuments(documentsData);
      setLibraries(librariesData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDocument = async (documentData: any) => {
    try {
      if (!libraryId) {
        throw new Error('Library ID is required');
      }
      
      await documentApi.create({
        ...documentData,
        library_id: libraryId
      });
      setShowCreateModal(false);
      await loadLibraryAndDocuments();
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to create document');
    }
  };

  const handleDeleteDocument = async (documentId: string) => {
    if (!window.confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
      return;
    }

    try {
      await documentApi.delete(documentId);
      if (libraryId) {
        await loadLibraryAndDocuments();
      } else {
        await loadAllDocuments();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete document');
    }
  };

  const handleEditDocument = (document: Document) => {
    setEditingDocument(document);
    setShowEditModal(true);
  };

  const handleUpdateDocument = async (documentId: string, documentData: DocumentUpdate) => {
    try {
      await documentApi.update(documentId, documentData);
      setShowEditModal(false);
      setEditingDocument(null);
      
      if (libraryId) {
        await loadLibraryAndDocuments();
      } else {
        await loadAllDocuments();
      }
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to update document');
    }
  };

  const getLibraryName = (documentLibraryId: string) => {
    const lib = libraries.find(l => l.id === documentLibraryId);
    return lib ? lib.metadata.name : 'Unknown Library';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading documents..." />
      </div>
    );
  }

  if (error && error.includes('not found')) {
    return (
      <div className="text-center py-16">
        <div className="w-16 h-16 mx-auto mb-4 bg-red-100  rounded-xl flex items-center justify-center border border-red-200 ">
          <ArchiveBoxIcon className="h-8 w-8 text-red-600 " />
        </div>
        <h3 className="text-xl font-semibold text-neutral-800  mb-2">
          Library Not Found
        </h3>
        <p className="text-neutral-600  mb-6">
          The library you're looking for may have been deleted or moved.
        </p>
        <Link to="/">
          <Button variant="primary" icon={ChevronLeftIcon}>
            Go to Libraries
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-50 to-secondary-50   rounded-xl p-6 border border-primary-200/50 ">
        <div className="flex items-center justify-between mb-4">
          <div>
            {libraryId && library ? (
              <>
                <div className="flex items-center space-x-2 mb-2">
                  <Link to="/">
                    <Button variant="ghost" size="sm" icon={ChevronLeftIcon}>
                      Libraries
                    </Button>
                  </Link>
                  <span className="text-neutral-400">/</span>
                  <span className="text-neutral-600 ">{library.metadata.name}</span>
                </div>
                <h1 className="text-2xl font-bold text-neutral-800 ">
                  Documents
                </h1>
                <p className="text-neutral-600 ">
                  {documents.length} document{documents.length !== 1 ? 's' : ''} in this library
                </p>
              </>
            ) : (
              <>
                <h1 className="text-2xl font-bold text-neutral-800  mb-1">
                  All Documents
                </h1>
                <p className="text-neutral-600 ">
                  Browse documents from all libraries
                </p>
              </>
            )}
          </div>
          
          {libraryId && (
            <Button
              variant="primary"
              icon={PlusIcon}
              onClick={() => setShowCreateModal(true)}
            >
              Add Document
            </Button>
          )}
        </div>

        {/* Quick Stats */}
        {documents.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white/60  rounded-lg p-4 text-center border border-surface-200 ">
              <div className="text-xl font-bold text-primary-600  mb-1">
                {documents.length}
              </div>
              <div className="text-sm text-neutral-600 ">
                Total Documents
              </div>
            </div>
            <div className="bg-white/60  rounded-lg p-4 text-center border border-surface-200 ">
              <div className="text-xl font-bold text-secondary-600  mb-1">
                {new Set(documents.map(d => d.metadata.file_type)).size}
              </div>
              <div className="text-sm text-neutral-600 ">
                File Types
              </div>
            </div>
            <div className="bg-white/60  rounded-lg p-4 text-center border border-surface-200 ">
              <div className="text-xl font-bold text-accent-600  mb-1">
                {new Set(documents.map(d => d.metadata.author)).size}
              </div>
              <div className="text-sm text-neutral-600 ">
                Authors
              </div>
            </div>
            <div className="bg-white/60  rounded-lg p-4 text-center border border-surface-200 ">
              <div className="text-xl font-bold text-warning-600  mb-1">
                {new Set(documents.flatMap(d => d.metadata.tags)).size}
              </div>
              <div className="text-sm text-neutral-600 ">
                Unique Tags
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && !error.includes('not found') && <ErrorMessage message={error} />}

      {/* Documents Grid */}
      {documents.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          {documents.map((document) => (
            <div key={document.id} className="library-card">
              {/* Document Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-secondary-100  border border-secondary-200 ">
                    <DocumentIcon className="h-5 w-5 text-secondary-600 " />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-neutral-800  truncate">
                      {document.metadata.title}
                    </h3>
                    <div className="flex items-center space-x-3 text-xs text-neutral-500 ">
                      <span className="flex items-center">
                        <DocumentTextIcon className="h-3 w-3 mr-1" />
                        {document.metadata.file_type}
                      </span>
                      <span className="flex items-center">
                        <ClockIcon className="h-3 w-3 mr-1" />
                        {formatDate(document.metadata.created_at)}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="badge-secondary text-xs">
                  {document.metadata.category || 'General'}
                </div>
              </div>

              {/* Library Name (for all documents view) */}
              {!libraryId && (
                <div className="mb-3">
                  <span className="badge-primary text-xs">
                    {getLibraryName(document.library_id)}
                  </span>
                </div>
              )}

              {/* Document Description */}
              {document.metadata.description && (
                <p className="text-sm text-neutral-600  mb-3 line-clamp-2">
                  {document.metadata.description}
                </p>
              )}

              {/* Author and Category */}
              <div className="flex items-center justify-between mb-3 text-sm">
                <div className="flex items-center space-x-2">
                  {document.metadata.author && (
                    <span className="flex items-center text-neutral-600 ">
                      <UserIcon className="h-4 w-4 mr-1" />
                      {document.metadata.author}
                    </span>
                  )}
                </div>
              </div>

              {/* Tags */}
              {document.metadata.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {document.metadata.tags.slice(0, 3).map((tag, tagIndex) => (
                    <span 
                      key={tag} 
                      className={`badge-${tagIndex % 2 === 0 ? 'primary' : 'accent'} text-xs`}
                    >
                      {tag}
                    </span>
                  ))}
                  {document.metadata.tags.length > 3 && (
                    <span className="badge-neutral text-xs">
                      +{document.metadata.tags.length - 3}
                    </span>
                  )}
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-between pt-3 border-t border-surface-200 ">
                <div className="flex space-x-1">
                  <Link to={`/documents/${document.id}/chunks`}>
                    <Button variant="outline" size="sm" icon={EyeIcon}>
                      Chunks
                    </Button>
                  </Link>
                </div>
                
                <div className="flex space-x-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleEditDocument(document)}
                    icon={PencilIcon}
                  >
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteDocument(document.id)}
                    icon={TrashIcon}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50 "
                  >
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <div className="w-16 h-16 mx-auto mb-4 bg-secondary-100  rounded-xl flex items-center justify-center border border-secondary-200 ">
            <DocumentIcon className="h-8 w-8 text-secondary-600 " />
          </div>
          <h3 className="text-xl font-semibold text-neutral-800  mb-2">
            No documents yet
          </h3>
          <p className="text-neutral-600  mb-6 max-w-md mx-auto">
            {libraryId 
              ? 'Add your first document to this library to get started.' 
              : 'No documents found across all libraries.'}
          </p>
          {libraryId && (
            <Button
              variant="primary"
              icon={PlusIcon}
              onClick={() => setShowCreateModal(true)}
            >
              Add Your First Document
            </Button>
          )}
        </div>
      )}

      {/* Create Document Modal */}
      {showCreateModal && (
        <CreateDocumentModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateDocument}
          libraryId={libraryId}
        />
      )}

      {/* Edit Document Modal */}
      {showEditModal && editingDocument && (
        <EditDocumentModal
          isOpen={showEditModal}
          document={editingDocument}
          onClose={() => {
            setShowEditModal(false);
            setEditingDocument(null);
          }}
          onUpdate={handleUpdateDocument}
        />
      )}
    </div>
  );
};

export default DocumentsPage;