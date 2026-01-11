'use client';

import { useState, useEffect } from 'react';
import styles from './page.module.css';
import dynamic from 'next/dynamic';

interface Folder {
  id: string;
  name: string;
  mimeType: string;
}

const ClientHome = dynamic(() => import('../components/ClientHome'), { ssr: false });

export default function Home() {
  return <ClientHome />;
}
