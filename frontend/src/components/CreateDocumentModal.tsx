import React, { useState } from 'react';
import { Dialog } from '@headlessui/react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { DocumentCreateForm } from '../types';
import LoadingSpinner from './LoadingSpinner';

interface CreateDocumentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: DocumentCreateForm) => Promise<void>;
  libraryId?: string;
}

const CreateDocumentModal: React.FC<CreateDocumentModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  libraryId,
}) => {
  const [formData, setFormData] = useState<DocumentCreateForm>({
    title: '',
    description: '',
    author: '',
    tags: [],
    category: '',
    file_type: 'text',
    library_id: libraryId || '',
  });
  const [tagInput, setTagInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim()) {
      setError('Document title is required');
      return;
    }

    if (!formData.library_id) {
      setError('Library ID is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await onSubmit(formData);
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        author: '',
        tags: [],
        category: '',
        file_type: 'text',
        library_id: libraryId || '',
      });
      setTagInput('');
    } catch (err: any) {
      setError(err.message || 'Failed to create document');
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
              Create New Document
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
              <label htmlFor="title" className="label">
                Title *
              </label>
              <input
                type="text"
                id="title"
                className="input"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Enter document title"
                required
              />
            </div>

            <div>
              <label htmlFor="description" className="label">
                Description
              </label>
              <textarea
                id="description"
                rows={3}
                className="input"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Enter document description"
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
              <label htmlFor="category" className="label">
                Category
              </label>
              <select
                id="category"
                className="input"
                value={formData.category}
                onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
              >
                <option value="">Select category</option>
                <option value="research">Research</option>
                <option value="analysis">Analysis</option>
                <option value="report">Report</option>
                <option value="tutorial">Tutorial</option>
                <option value="documentation">Documentation</option>
                <option value="guide">Guide</option>
              </select>
            </div>

            <div>
              <label htmlFor="file_type" className="label">
                File Type
              </label>
              <select
                id="file_type"
                className="input"
                value={formData.file_type}
                onChange={(e) => setFormData(prev => ({ ...prev, file_type: e.target.value }))}
              >
                <option value="text">Text</option>
                <option value="pdf">PDF</option>
                <option value="docx">Word Document</option>
                <option value="html">HTML</option>
                <option value="markdown">Markdown</option>
              </select>
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
                {loading ? <LoadingSpinner size="sm" /> : 'Create Document'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Dialog>
  );
};

export default CreateDocumentModal;