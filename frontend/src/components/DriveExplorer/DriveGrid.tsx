import React from 'react';
import { DriveItem } from '../../types/drive';
import { DriveItemCard } from './DriveItemCard';
import styles from '../../app/page.module.css';

interface DriveGridProps {
  items: DriveItem[];
  onItemClick: (item: DriveItem) => void;
}

export const DriveGrid: React.FC<DriveGridProps> = ({ items, onItemClick }) => {
  if (items.length === 0) return null;

  return (
    <div className={styles.grid}>
      {items.map((item) => (
        <DriveItemCard 
          key={item.id} 
          item={item} 
          onClick={onItemClick} 
        />
      ))}
    </div>
  );
};
