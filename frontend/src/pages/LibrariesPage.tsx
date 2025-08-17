import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  BookOpenIcon,
  ClockIcon,

  GlobeAltIcon,
  LockClosedIcon,
  CubeIcon,
  SparklesIcon,
  ChartBarIcon,
  BoltIcon,
  EyeIcon,
  TrashIcon,

  ArchiveBoxIcon,
} from '@heroicons/react/24/outline';
import { Library, LibraryStats, IndexType } from '../types';
import { libraryApi } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import CreateLibraryModal from '../components/CreateLibraryModal';
import Button from '../components/Button';

const LibrariesPage: React.FC = () => {
  const [libraries, setLibraries] = useState<Library[]>([]);
  const [libraryStats, setLibraryStats] = useState<Record<string, LibraryStats>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [indexingLibrary, setIndexingLibrary] = useState<string | null>(null);

  useEffect(() => {
    loadLibraries();
  }, []);

  const loadLibraries = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const librariesData = await libraryApi.getAll();
      setLibraries(librariesData);
      
      const statsPromises = librariesData.map(async (library) => {
        try {
          const stats = await libraryApi.getStats(library.id);
          return { libraryId: library.id, stats };
        } catch (err) {
          console.error(`Failed to load stats for library ${library.id}:`, err);
          return null;
        }
      });
      
      const statsResults = await Promise.all(statsPromises);
      const statsMap: Record<string, LibraryStats> = {};
      
      statsResults.forEach((result) => {
        if (result) {
          statsMap[result.libraryId] = result.stats;
        }
      });
      
      setLibraryStats(statsMap);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load libraries');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateLibrary = async (libraryData: any) => {
    try {
      await libraryApi.create(libraryData);
      setShowCreateModal(false);
      await loadLibraries();
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to create library');
    }
  };

  const handleDeleteLibrary = async (libraryId: string) => {
    if (!window.confirm('Are you sure you want to delete this library? This action cannot be undone.')) {
      return;
    }

    try {
      await libraryApi.delete(libraryId);
      await loadLibraries();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete library');
    }
  };

  const handleIndexLibrary = async (libraryId: string, indexType: IndexType = 'flat') => {
    try {
      setIndexingLibrary(libraryId);
      await libraryApi.index(libraryId, indexType);
      await loadLibraries();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to index library');
    } finally {
      setIndexingLibrary(null);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getIndexTypeIcon = (indexType?: string) => {
    switch (indexType) {
      case 'flat': return CubeIcon;
      case 'rp_lsh': return BoltIcon;
      case 'hierarchical': return ChartBarIcon;
      default: return CubeIcon;
    }
  };

  const getIndexTypeColor = (indexType?: string) => {
    switch (indexType) {
      case 'flat': return 'primary';
      case 'rp_lsh': return 'accent';
      case 'hierarchical': return 'secondary';
      default: return 'primary';
    }
  };

  // Calculate overall stats
  const totalLibraries = libraries.length;
  const totalDocuments = Object.values(libraryStats).reduce((sum, stats) => sum + stats.total_documents, 0);
  const totalChunks = Object.values(libraryStats).reduce((sum, stats) => sum + stats.total_chunks, 0);
  const indexedLibraries = libraries.filter(lib => lib.is_indexed).length;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading libraries..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <div className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-xl p-6 border border-primary-200/50">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-neutral-800 mb-1">
              Document Libraries
            </h1>
            <p className="text-neutral-600">
              Organize and manage your document collections with vector search
            </p>
          </div>
          <Button
            variant="primary"
            icon={PlusIcon}
            onClick={() => setShowCreateModal(true)}
          >
            New Library
          </Button>
        </div>
        
        {/* Quick Stats */}
        {totalLibraries > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white/60  rounded-lg p-4 text-center border border-surface-200 ">
              <div className="text-2xl font-bold text-primary-600  mb-1">
                {totalLibraries}
              </div>
              <div className="text-sm text-neutral-600 ">
                Libraries
              </div>
            </div>
            <div className="bg-white/60  rounded-lg p-4 text-center border border-surface-200 ">
              <div className="text-2xl font-bold text-secondary-600  mb-1">
                {totalDocuments}
              </div>
              <div className="text-sm text-neutral-600 ">
                Documents
              </div>
            </div>
            <div className="bg-white/60  rounded-lg p-4 text-center border border-surface-200 ">
              <div className="text-2xl font-bold text-accent-600  mb-1">
                {totalChunks}
              </div>
              <div className="text-sm text-neutral-600 ">
                Chunks
              </div>
            </div>
            <div className="bg-white/60  rounded-lg p-4 text-center border border-surface-200 ">
              <div className="text-2xl font-bold text-warning-600  mb-1">
                {indexedLibraries}
              </div>
              <div className="text-sm text-neutral-600 ">
                Indexed
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && <ErrorMessage message={error} />}

      {/* Libraries Grid */}
      {libraries.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          {libraries.map((library, index) => {
            const stats = libraryStats[library.id];
            const IndexIcon = getIndexTypeIcon(stats?.index_type);
            const indexColor = getIndexTypeColor(stats?.index_type);
            
            return (
              <div key={library.id} className="library-card">
                {/* Library Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary-100  border border-primary-200 ">
                      <BookOpenIcon className="h-5 w-5 text-primary-600 " />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-semibold text-neutral-800  truncate">
                        {library.metadata.name}
                      </h3>
                      <div className="flex items-center space-x-3 text-xs text-neutral-500 ">
                        <span className="flex items-center">
                          {library.metadata.is_public ? (
                            <GlobeAltIcon className="h-3 w-3 mr-1" />
                          ) : (
                            <LockClosedIcon className="h-3 w-3 mr-1" />
                          )}
                          {library.metadata.is_public ? 'Public' : 'Private'}
                        </span>
                        <span className="flex items-center">
                          <ClockIcon className="h-3 w-3 mr-1" />
                          {formatDate(library.metadata.created_at)}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Status badges */}
                  <div className="flex items-center space-x-1">
                    {library.is_indexed && stats?.index_type && (
                      <div className={`badge-${indexColor} text-xs flex items-center space-x-1`}>
                        <IndexIcon className="h-3 w-3" />
                        <span>{stats.index_type.toUpperCase()}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Library Description */}
                {library.metadata.description && (
                  <p className="text-sm text-neutral-600  mb-3 line-clamp-2">
                    {library.metadata.description}
                  </p>
                )}

                {/* Library Stats */}
                {stats && (
                  <div className="grid grid-cols-3 gap-2 mb-3">
                    <div className="text-center p-2 bg-primary-50  rounded border border-primary-200/50 ">
                      <div className="text-lg font-bold text-primary-700 ">
                        {stats.total_documents}
                      </div>
                      <div className="text-xs text-primary-600 ">
                        Docs
                      </div>
                    </div>
                    <div className="text-center p-2 bg-secondary-50  rounded border border-secondary-200/50 ">
                      <div className="text-lg font-bold text-secondary-700 ">
                        {stats.total_chunks}
                      </div>
                      <div className="text-xs text-secondary-600 ">
                        Chunks
                      </div>
                    </div>
                    <div className="text-center p-2 bg-accent-50  rounded border border-accent-200/50 ">
                      <div className="text-lg font-bold text-accent-700 ">
                        {stats.embedding_dimension || 'N/A'}
                      </div>
                      <div className="text-xs text-accent-600 ">
                        Dims
                      </div>
                    </div>
                  </div>
                )}

                {/* Tags */}
                {library.metadata.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {library.metadata.tags.slice(0, 3).map((tag, tagIndex) => (
                      <span 
                        key={tag} 
                        className={`badge-${tagIndex % 2 === 0 ? 'primary' : 'secondary'} text-xs`}
                      >
                        {tag}
                      </span>
                    ))}
                    {library.metadata.tags.length > 3 && (
                      <span className="badge-neutral text-xs">
                        +{library.metadata.tags.length - 3}
                      </span>
                    )}
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center justify-between pt-3 border-t border-surface-200 ">
                  <div className="flex space-x-1">
                    <Link to={`/libraries/${library.id}/documents`}>
                      <Button variant="outline" size="sm" icon={EyeIcon}>
                        View
                      </Button>
                    </Link>
                    <Link to={`/search?library=${library.id}`}>
                      <Button variant="ghost" size="sm" icon={MagnifyingGlassIcon}>
                        Search
                      </Button>
                    </Link>
                  </div>
                  
                  <div className="flex space-x-1">
                    {!library.is_indexed && stats && stats.total_chunks > 0 && (
                      <Button
                        variant="secondary"
                        size="sm"
                        loading={indexingLibrary === library.id}
                        loadingText="..."
                        onClick={() => handleIndexLibrary(library.id)}
                        icon={SparklesIcon}
                      >
                        Index
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteLibrary(library.id)}
                      icon={TrashIcon}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50 "
                    >
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-16">
          <div className="w-16 h-16 mx-auto mb-4 bg-primary-100  rounded-xl flex items-center justify-center border border-primary-200 ">
            <ArchiveBoxIcon className="h-8 w-8 text-primary-600 " />
          </div>
          <h3 className="text-xl font-semibold text-neutral-800  mb-2">
            No libraries yet
          </h3>
          <p className="text-neutral-600  mb-6 max-w-md mx-auto">
            Create your first library to start organizing your documents with powerful vector search.
          </p>
          <Button
            variant="primary"
            icon={PlusIcon}
            onClick={() => setShowCreateModal(true)}
          >
            Create Your First Library
          </Button>
        </div>
      )}

      {/* Create Library Modal */}
      {showCreateModal && (
        <CreateLibraryModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateLibrary}
        />
      )}
    </div>
  );
};

export default LibrariesPage;