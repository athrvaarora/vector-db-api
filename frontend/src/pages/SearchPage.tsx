import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  MagnifyingGlassIcon,
  DocumentIcon,
  ClockIcon,
  UserIcon,
  TagIcon,
  ChevronDownIcon,
  SparklesIcon,
  AdjustmentsHorizontalIcon,

  BoltIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';
import { Library, SearchResult } from '../types';
import { libraryApi, generateEmbedding } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import Button from '../components/Button';

const SearchPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [libraries, setLibraries] = useState<Library[]>([]);
  const [selectedLibrary, setSelectedLibrary] = useState<string>('');
  const [searchText, setSearchText] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [librariesLoading, setLibrariesLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [k, setK] = useState(10);
  const [similarityThreshold, setSimilarityThreshold] = useState(0.0);
  const [searchTimeout, setSearchTimeout] = useState<NodeJS.Timeout | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [searchStats, setSearchStats] = useState({
    totalSearches: 0,
    avgSimilarity: 0,
    searchTime: 0,
  });

  useEffect(() => {
    loadLibraries();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const libraryParam = searchParams.get('library');
    if (libraryParam) {
      setSelectedLibrary(libraryParam);
    }
  }, [searchParams]);

  useEffect(() => {
    return () => {
      if (searchTimeout) {
        clearTimeout(searchTimeout);
      }
    };
  }, [searchTimeout]);

  useEffect(() => {
    if (selectedLibrary && searchText.trim()) {
      performSearch();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedLibrary]);

  const loadLibraries = async () => {
    try {
      setLibrariesLoading(true);
      const librariesData = await libraryApi.getAll();
      setLibraries(librariesData);
      
      if (librariesData.length > 0 && !selectedLibrary) {
        setSelectedLibrary(librariesData[0].id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load libraries');
    } finally {
      setLibrariesLoading(false);
    }
  };

  const performSearch = async () => {
    if (!searchText.trim()) {
      setSearchResults([]);
      setError(null);
      return;
    }
    
    if (!selectedLibrary) {
      setError('Please select a library');
      return;
    }

    try {
      const startTime = Date.now();
      setLoading(true);
      setError(null);
      
      const embedding = await generateEmbedding(searchText);
      
      const results = await libraryApi.search(selectedLibrary, {
        embedding,
        k,
        similarity_threshold: similarityThreshold > 0 ? similarityThreshold : undefined,
      });
      
      const endTime = Date.now();
      const searchTime = endTime - startTime;
      
      setSearchResults(results);
      
      // Update search stats
      setSearchStats(prev => ({
        totalSearches: prev.totalSearches + 1,
        avgSimilarity: results.length > 0 ? results.reduce((sum, r) => sum + r.similarity_score, 0) / results.length : 0,
        searchTime,
      }));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    await performSearch();
  };

  const handleSearchTextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newText = e.target.value;
    setSearchText(newText);
    
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }
    
    const timeout = setTimeout(() => {
      performSearch();
    }, 500);
    
    setSearchTimeout(timeout);
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

  const highlightSearchTerms = (text: string, searchTerm: string) => {
    if (!searchTerm.trim()) return text;
    
    const regex = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} className="bg-primary-100  px-1 py-0.5 rounded text-primary-900 ">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  const getSimilarityBadge = (score: number) => {
    if (score >= 0.8) return 'badge-secondary';
    if (score >= 0.6) return 'badge-primary';
    if (score >= 0.4) return 'badge-warning';
    return 'badge-accent';
  };

  if (librariesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading libraries..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-50 to-secondary-50   rounded-xl p-6 border border-primary-200/50 ">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-neutral-800  mb-2">
            Semantic Document Search
          </h1>
          <p className="text-neutral-600 ">
            Find documents using advanced vector similarity search
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-white/60  rounded-lg p-4 text-center border border-surface-200 ">
            <div className="flex items-center justify-center mb-2">
              <BoltIcon className="h-5 w-5 text-primary-600 " />
            </div>
            <div className="text-xl font-bold text-primary-700  mb-1">
              {searchStats.totalSearches}
            </div>
            <div className="text-xs text-neutral-600 ">
              Total Searches
            </div>
          </div>
          <div className="bg-white/60  rounded-lg p-4 text-center border border-surface-200 ">
            <div className="flex items-center justify-center mb-2">
              <ChartBarIcon className="h-5 w-5 text-accent-600 " />
            </div>
            <div className="text-xl font-bold text-accent-700  mb-1">
              {(searchStats.avgSimilarity * 100).toFixed(0)}%
            </div>
            <div className="text-xs text-neutral-600 ">
              Avg Similarity
            </div>
          </div>
          <div className="bg-white/60  rounded-lg p-4 text-center border border-surface-200 ">
            <div className="flex items-center justify-center mb-2">
              <SparklesIcon className="h-5 w-5 text-secondary-600 " />
            </div>
            <div className="text-xl font-bold text-secondary-700  mb-1">
              {searchStats.searchTime}ms
            </div>
            <div className="text-xs text-neutral-600 ">
              Last Search
            </div>
          </div>
        </div>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="grid md:grid-cols-3 gap-4">
            {/* Library Selection */}
            <div>
              <label htmlFor="library" className="label">
                Library
              </label>
              <select
                id="library"
                value={selectedLibrary}
                onChange={(e) => setSelectedLibrary(e.target.value)}
                className="input"
                required
              >
                <option value="">Choose library</option>
                {libraries.map((library) => (
                  <option key={library.id} value={library.id}>
                    {library.metadata.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Filters Toggle */}
            <div>
              <label className="label">Options</label>
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
                icon={AdjustmentsHorizontalIcon}
                fullWidth
              >
                Advanced
                <ChevronDownIcon className={`ml-2 h-4 w-4 transform transition-transform ${showFilters ? 'rotate-180' : ''}`} />
              </Button>
            </div>

            {/* Search Button */}
            <div>
              <label className="label">Action</label>
              <Button
                type="submit"
                variant="primary"
                disabled={!selectedLibrary || loading}
                loading={loading}
                loadingText="Searching..."
                icon={MagnifyingGlassIcon}
                fullWidth
              >
                Search
              </Button>
            </div>
          </div>

          {/* Search Input */}
          <div className="relative">
            <input
              type="text"
              className="input pl-12 pr-4 py-3 text-base"
              placeholder="Enter your search query..."
              value={searchText}
              onChange={handleSearchTextChange}
            />
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center">
              {loading ? (
                <LoadingSpinner size="sm" />
              ) : (
                <MagnifyingGlassIcon className="h-5 w-5 text-primary-400" />
              )}
            </div>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="grid md:grid-cols-2 gap-4 p-4 bg-surface-50  rounded-lg border border-surface-200 ">
              <div>
                <label htmlFor="k" className="label">
                  Max Results
                </label>
                <input
                  type="number"
                  id="k"
                  min="1"
                  max="50"
                  value={k}
                  onChange={(e) => setK(parseInt(e.target.value))}
                  className="input"
                />
              </div>
              <div>
                <label htmlFor="threshold" className="label">
                  Similarity Threshold
                </label>
                <input
                  type="number"
                  id="threshold"
                  min="0"
                  max="1"
                  step="0.1"
                  value={similarityThreshold}
                  onChange={(e) => setSimilarityThreshold(parseFloat(e.target.value))}
                  className="input"
                />
              </div>
            </div>
          )}
        </form>
      </div>

      {/* Error Message */}
      {error && <ErrorMessage message={error} />}

      {/* Search Results */}
      {searchResults.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-neutral-800 ">
              Search Results
            </h2>
            <div className="badge-neutral">
              {searchResults.length} result{searchResults.length !== 1 ? 's' : ''}
            </div>
          </div>
          
          <div className="grid gap-4">
            {searchResults.map((result, index) => (
              <div key={`${result.chunk.id}-${index}`} className="card-interactive">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-start space-x-3 flex-1">
                    <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary-100  border border-primary-200  text-sm font-bold text-primary-700 ">
                      {index + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-semibold text-neutral-800  mb-1 truncate">
                        {result.document.metadata.title}
                      </h3>
                      <div className="flex items-center space-x-4 text-sm text-neutral-500 ">
                        <span className="flex items-center">
                          <DocumentIcon className="h-4 w-4 mr-1" />
                          {result.document.metadata.file_type}
                        </span>
                        <span className="flex items-center">
                          <ClockIcon className="h-4 w-4 mr-1" />
                          {formatDate(result.chunk.metadata.created_at)}
                        </span>
                        {result.chunk.metadata.author && (
                          <span className="flex items-center">
                            <UserIcon className="h-4 w-4 mr-1" />
                            {result.chunk.metadata.author}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className={`${getSimilarityBadge(result.similarity_score)} font-bold`}>
                    {(result.similarity_score * 100).toFixed(1)}%
                  </div>
                </div>

                <div className="text-neutral-700  mb-3 leading-relaxed">
                  {highlightSearchTerms(result.chunk.text, searchText)}
                </div>

                {result.chunk.metadata.tags.length > 0 && (
                  <div className="flex items-center space-x-2">
                    <TagIcon className="h-4 w-4 text-neutral-400" />
                    <div className="flex flex-wrap gap-1">
                      {result.chunk.metadata.tags.map((tag, tagIndex) => (
                        <span
                          key={tag}
                          className={`badge-${tagIndex % 2 === 0 ? 'primary' : 'secondary'} text-xs`}
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && searchText && searchResults.length === 0 && !error && (
        <div className="text-center py-16">
          <div className="w-16 h-16 mx-auto mb-4 bg-neutral-100  rounded-xl flex items-center justify-center border border-neutral-200 ">
            <MagnifyingGlassIcon className="h-8 w-8 text-neutral-400" />
          </div>
          <h3 className="text-xl font-semibold text-neutral-800  mb-2">
            No results found
          </h3>
          <p className="text-neutral-500  max-w-md mx-auto">
            Try adjusting your search terms, selecting a different library, or lowering the similarity threshold.
          </p>
        </div>
      )}
    </div>
  );
};

export default SearchPage;