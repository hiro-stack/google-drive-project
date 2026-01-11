'use client';

import { useState, useEffect } from 'react';
import styles from '../app/page.module.css';
import { useDriveExplorer } from '../hooks/useDriveExplorer';
import { Breadcrumbs } from './DriveExplorer/Breadcrumbs';
import { StatusDisplay } from './DriveExplorer/StatusDisplay';
import { DriveGrid } from './DriveExplorer/DriveGrid';
import { SearchForm } from './DriveExplorer/SearchForm';

export default function ClientHome() {
  const [isMounted, setIsMounted] = useState(false);
  const { 
    items, 
    loading, 
    error, 
    breadcrumbs, 
    handleItemClick, 
    handleBreadcrumbClick, 
    refresh,
    search
  } = useDriveExplorer();

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return null;
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>Google Drive Explorer</h1>
        <p className={styles.subtitle}>共有されたGoogle Driveの中身を、安心して見ることができます。</p>
        
        <SearchForm onSearch={search} />

        <Breadcrumbs 
          breadcrumbs={breadcrumbs} 
          onBreadcrumbClick={handleBreadcrumbClick} 
        />
      </header>

      <main className={styles.main}>
        <StatusDisplay 
          loading={loading} 
          error={error} 
          isEmpty={!loading && !error && items.length === 0}
          onRetry={refresh} // Refresh re-fetches the current folder
        />

        {!loading && !error && (
          <DriveGrid 
            items={items} 
            onItemClick={handleItemClick} 
          />
        )}
      </main>
      
      <footer className={styles.footer}>
        <div className={styles.footerContent}>
          &copy; {new Date().getFullYear()} Drive Explorer System
        </div>
      </footer>
    </div>
  );
}
