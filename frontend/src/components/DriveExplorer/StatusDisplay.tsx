import React from 'react';
import styles from '../../app/page.module.css';

interface StatusDisplayProps {
  loading: boolean;
  error: string | null;
  isEmpty: boolean;
  onRetry: () => void;
}

export const StatusDisplay: React.FC<StatusDisplayProps> = ({ loading, error, isEmpty, onRetry }) => {
  if (loading) {
    return (
      <div className={styles.loadingState}>
        <div className={styles.spinner}></div>
        <p>Syncing with Google Drive...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorState}>
        <h2>Connection Error</h2>
        <p>{error}</p>
        <p style={{ fontSize: '0.9rem', color: '#64748b', marginTop: '1rem', maxWidth: '500px' }}>
          Make sure the backend is running and 'service_account.json' is configured correctly.
        </p>
        <button 
          className={styles.retryBtn}
          onClick={onRetry}
        >
          Retry
        </button>
      </div>
    );
  }

  if (isEmpty) {
    return (
      <div className={styles.emptyState}>
        <p>This folder is empty.</p>
      </div>
    );
  }

  return null;
};
