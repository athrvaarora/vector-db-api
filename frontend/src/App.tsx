import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import LibrariesPage from './pages/LibrariesPage';
import SearchPage from './pages/SearchPage';
import DocumentsPage from './pages/DocumentsPage';
import ChunksPage from './pages/ChunksPage';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<LibrariesPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/libraries/:libraryId/documents" element={<DocumentsPage />} />
          <Route path="/documents/:documentId/chunks" element={<ChunksPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;