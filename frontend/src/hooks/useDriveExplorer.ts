import { useState, useEffect, useCallback } from 'react';
import { DriveItem, Breadcrumb } from '../types/drive';

import { normalizeQuery } from '../utils/stringUtils';

export const useDriveExplorer = () => {
  const [items, setItems] = useState<DriveItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [breadcrumbs, setBreadcrumbs] = useState<Breadcrumb[]>([{ id: null, name: 'Home' }]);

  const fetchItems = useCallback(async (folderId: string | null = null, queryText: string = '') => {
    console.log('Fetching items for folderId:', folderId, 'Query:', queryText);
    
    // Normalize query if present
    const normalizedQuery = queryText ? normalizeQuery(queryText) : '';
    console.log('Normalized Query:', normalizedQuery);

    setLoading(true);
    setError(null);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
      
      const params = new URLSearchParams();
      if (folderId) params.append('folder_id', folderId);
      if (normalizedQuery) params.append('query', normalizedQuery);
      
      const queryString = params.toString();
      console.log('Requesting URL:', `${apiUrl}/folders/?${queryString}`);
      
      const res = await fetch(`${apiUrl}/folders/?${queryString}`);
      
      if (!res.ok) {
        throw new Error('Failed to fetch items. Backend might be down or API error.');
      }
      const data = await res.json();
      console.log('Fetched data:', data);
      setItems(data);
    } catch (err: any) {
      console.error('Fetch error:', err);
      setError(err.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchItems(null);
  }, [fetchItems]);

  const handleFolderClick = (folder: DriveItem) => {
    console.log('Clicked folder:', folder);
    if (folder.mimeType === 'application/vnd.google-apps.folder') {
      console.log('Navigating into folder:', folder.name);
      setBreadcrumbs(prev => [...prev, { id: folder.id, name: folder.name }]);
      fetchItems(folder.id);
    }
  };

  const handleFileClick = (item: DriveItem) => {
    console.log('Clicked file:', item);
    if (item.webViewLink) {
      window.open(item.webViewLink, '_blank');
    } else {
      console.warn('No webViewLink found for item:', item);
      alert("No preview link available for this file.");
    }
  };

  const handleItemClick = (item: DriveItem) => {
    if (item.mimeType === 'application/vnd.google-apps.folder') {
      handleFolderClick(item);
    } else {
      handleFileClick(item);
    }
  };

  const handleBreadcrumbClick = (index: number) => {
    const newBreadcrumbs = breadcrumbs.slice(0, index + 1);
    setBreadcrumbs(newBreadcrumbs);
    fetchItems(newBreadcrumbs[index].id);
  };

  const refresh = () => {
    const currentFolderId = breadcrumbs[breadcrumbs.length - 1].id;
    fetchItems(currentFolderId);
  };

  const search = (query: string) => {
    const currentFolderId = breadcrumbs[breadcrumbs.length - 1].id;
    fetchItems(currentFolderId, query);
  };

  return {
    items,
    loading,
    error,
    breadcrumbs,
    handleItemClick,
    handleBreadcrumbClick,
    refresh,
    search
  };
};
