import React, { useState } from 'react';
import { Dialog } from '@headlessui/react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { ChunkCreateForm } from '../types';
import { generateEmbedding } from '../services/api';
import LoadingSpinner from './LoadingSpinner';

interface CreateChunkModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: ChunkCreateForm, embedding: number[]) => Promise<void>;
  documentId: string;
}

const CreateChunkModal: React.FC<CreateChunkModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  documentId,
}) => {
  const [formData, setFormData] = useState<ChunkCreateForm>({
    text: '',
    source: '',
    author: '',
    tags: [],
    document_id: documentId,
  });
  const [tagInput, setTagInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.text.trim()) {
      setError('Chunk text is required');
      return;
    }

    if (!formData.source.trim()) {
      setError('Source is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Generate embedding for the text
      const embedding = await generateEmbedding(formData.text);
      
      await onSubmit(formData, embedding);
      
      // Reset form
      setFormData({
        text: '',
        source: '',
        author: '',
        tags: [],
        document_id: documentId,
      });
      setTagInput('');
    } catch (err: any) {
      setError(err.message || 'Failed to create chunk');
    } finally {
      setLoading(false);
    }
  };

  const handleAddTag = () => {
    const tag = tagInput.trim();
    if (tag && !formData.tags.includes(tag)) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tag]
      }));
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleTagInputKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  return (
    <Dialog
      open={isOpen}
      onClose={onClose}
      className="fixed inset-0 z-50 overflow-y-auto"
    >
      <div className="flex items-center justify-center min-h-screen px-4">
        <Dialog.Overlay className="fixed inset-0 bg-gray-500 bg-opacity-75" />
        
        <div className="relative bg-white rounded-lg max-w-lg w-full p-6">
          <div className="flex items-center justify-between mb-4">
            <Dialog.Title className="text-lg font-medium text-gray-900">
              Create New Chunk
            </Dialog.Title>
            <button
              type="button"
              className="text-gray-400 hover:text-gray-600"
              onClick={onClose}
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="text" className="label">
                Text Content *
              </label>
              <textarea
                id="text"
                rows={6}
                className="input"
                value={formData.text}
                onChange={(e) => setFormData(prev => ({ ...prev, text: e.target.value }))}
                placeholder="Enter the chunk text content..."
                required
                maxLength={10000}
              />
              <div className="mt-1 text-xs text-gray-500">
                {formData.text.length}/10,000 characters
              </div>
            </div>

            <div>
              <label htmlFor="source" className="label">
                Source *
              </label>
              <input
                type="text"
                id="source"
                className="input"
                value={formData.source}
                onChange={(e) => setFormData(prev => ({ ...prev, source: e.target.value }))}
                placeholder="e.g., page_1, section_2, paragraph_3"
                required
              />
            </div>

            <div>
              <label htmlFor="author" className="label">
                Author
              </label>
              <input
                type="text"
                id="author"
                className="input"
                value={formData.author}
                onChange={(e) => setFormData(prev => ({ ...prev, author: e.target.value }))}
                placeholder="Enter author name"
              />
            </div>

            <div>
              <label htmlFor="tags" className="label">
                Tags
              </label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  id="tags"
                  className="input flex-1"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyPress={handleTagInputKeyPress}
                  placeholder="Add a tag and press Enter"
                />
                <button
                  type="button"
                  onClick={handleAddTag}
                  className="btn-outline px-3"
                >
                  Add
                </button>
              </div>
              
              {formData.tags.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {formData.tags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                    >
                      {tag}
                      <button
                        type="button"
                        onClick={() => handleRemoveTag(tag)}
                        className="ml-1 text-primary-600 hover:text-primary-500"
                      >
                        <XMarkIcon className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            {error && (
              <div className="text-sm text-red-600 bg-red-50 p-2 rounded-md">
                {error}
              </div>
            )}

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="btn-outline"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn-primary"
                disabled={loading}
              >
                {loading ? <LoadingSpinner size="sm" /> : 'Create Chunk'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Dialog>
  );
};

export default CreateChunkModal;