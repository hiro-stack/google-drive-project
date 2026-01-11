import React from 'react';
import { DriveItem } from '../../types/drive';
import styles from '../../app/page.module.css';

interface DriveItemCardProps {
  item: DriveItem;
  onClick: (item: DriveItem) => void;
}

export const DriveItemCard: React.FC<DriveItemCardProps> = ({ item, onClick }) => {
  const isFolder = item.mimeType === 'application/vnd.google-apps.folder';

  return (
    <button 
      className={`${styles.card} ${!isFolder ? styles.fileCard : ''}`}
      onClick={() => onClick(item)}
      type="button"
      style={{ width: '100%', textAlign: 'left', border: 'none', background: 'var(--card-bg)', cursor: 'pointer' }}
    >
      <div className={styles.cardIcon}>
        {isFolder ? '📁' : '📄'}
      </div>
      <div className={styles.cardContent}>
        <h3 className={styles.cardTitle}>{item.name}</h3>
        <span className={styles.cardId}>{isFolder ? 'Folder' : 'File'}</span>
      </div>
    </button>
  );
};
