import React from 'react';
import { Breadcrumb } from '../../types/drive';
import styles from '../../app/page.module.css';

interface BreadcrumbsProps {
  breadcrumbs: Breadcrumb[];
  onBreadcrumbClick: (index: number) => void;
}

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ breadcrumbs, onBreadcrumbClick }) => {
  return (
    <nav className={styles.breadcrumbs}>
      {breadcrumbs.map((crumb, index) => (
        <span key={index} className={styles.breadcrumbItem}>
          {index > 0 && <span className={styles.separator}>/</span>}
          <button 
            onClick={() => onBreadcrumbClick(index)}
            className={index === breadcrumbs.length - 1 ? styles.activeCrumb : styles.crumbLink}
          >
            {crumb.name}
          </button>
        </span>
      ))}
    </nav>
  );
};
