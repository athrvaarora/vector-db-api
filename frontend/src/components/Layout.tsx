import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Bars3Icon,
  XMarkIcon,
  BookOpenIcon,
  DocumentIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';

interface LayoutProps {
  children: React.ReactNode;
}

const navigation = [
  { 
    name: 'Libraries', 
    href: '/', 
    icon: BookOpenIcon,
  },
  { 
    name: 'Documents', 
    href: '/documents', 
    icon: DocumentIcon,
  },
  { 
    name: 'Search', 
    href: '/search', 
    icon: MagnifyingGlassIcon,
  },
];

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="min-h-screen">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50 fade-in">
          <div 
            className="fixed inset-0 bg-neutral-900/50 backdrop-blur-sm" 
            onClick={() => setSidebarOpen(false)} 
          />
          <div className="fixed inset-y-0 left-0 flex w-72 flex-col bg-white/90 backdrop-blur-xl shadow-2xl slide-up border-r border-surface-200">
            <div className="flex h-16 items-center justify-between px-6 border-b border-neutral-200">
              <div className="flex items-center space-x-3">
                <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 shadow-lg">
                  <BookOpenIcon className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-bold text-neutral-800">Vector DB</h1>
                  <p className="text-xs text-neutral-500">Semantic Search</p>
                </div>
              </div>
              <button
                type="button"
                className="p-2 text-neutral-400 hover:text-neutral-600 transition-colors rounded-lg hover:bg-neutral-100"
                onClick={() => setSidebarOpen(false)}
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>
            
            <nav className="flex-1 space-y-1 p-4">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={isActive ? 'nav-item-active' : 'nav-item'}
                    onClick={() => setSidebarOpen(false)}
                  >
                    <item.icon className="h-5 w-5 mr-3" />
                    {item.name}
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>
      )}

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-72 lg:flex-col">
        <div className="flex flex-col flex-1 bg-white/90 backdrop-blur-xl border-r border-surface-200 shadow-xl">
          {/* Sidebar header */}
          <div className="flex items-center justify-between px-6 py-6 border-b border-surface-200">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 shadow-lg">
                <BookOpenIcon className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-neutral-800">Vector DB</h1>
                <p className="text-sm text-neutral-500">Semantic Search</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 p-4">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={isActive ? 'nav-item-active' : 'nav-item'}
                >
                  <item.icon className="h-5 w-5 mr-3" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-72">
        {/* Top bar */}
        <div className="sticky top-0 z-10 bg-white/90 backdrop-blur-xl border-b border-surface-200 shadow-sm">
          <div className="flex h-20 items-center justify-between px-6">
            <div className="flex items-center space-x-4">
              <button
                type="button"
                className="lg:hidden p-2 text-neutral-400 hover:text-neutral-600 transition-colors rounded-xl hover:bg-neutral-100"
                onClick={() => setSidebarOpen(true)}
              >
                <Bars3Icon className="h-6 w-6" />
              </button>
              
              <div className="hidden sm:block">
                <h2 className="text-xl font-bold text-neutral-800">
                  {navigation.find(item => item.href === location.pathname)?.name || 'Vector Database'}
                </h2>
                <p className="text-sm text-neutral-500">
                  {navigation.find(item => item.href === location.pathname)?.name === 'Libraries' && 'Manage your document collections'}
                  {navigation.find(item => item.href === location.pathname)?.name === 'Documents' && 'Browse all documents'}
                  {navigation.find(item => item.href === location.pathname)?.name === 'Search' && 'Semantic vector search'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="p-6">
          <div className="fade-in">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;