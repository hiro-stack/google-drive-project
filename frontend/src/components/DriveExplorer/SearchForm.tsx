import React, { useState } from 'react';
import styles from '../../app/page.module.css';

interface SearchFormProps {
  onSearch: (query: string) => void;
}

export const SearchForm: React.FC<SearchFormProps> = ({ onSearch }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query);
  };

  const handleVoiceInput = () => {
    // Type assertion for SpeechRecognition API
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("このブラウザでは音声認識がサポートされていません。Chromeなどでお試しください。");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'ja-JP';  // Japanese
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.start();

    recognition.onresult = (event: any) => {
      const voiceResult = event.results[0][0].transcript;
      console.log('音声認識結果:', voiceResult);
      setQuery(voiceResult);
      onSearch(voiceResult);
    };

    recognition.onerror = (event: any) => {
      console.error('音声認識エラー:', event.error);
      alert(`音声認識中にエラーが発生しました: ${event.error}`);
    };
  };

  return (
    <form onSubmit={handleSubmit} className={styles.searchForm}>
      <input
        type="text"
        placeholder="Search files..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className={styles.searchInput}
      />
      <button type="submit" className={styles.searchButton}>
        Search
      </button>
      <button 
        type="button" 
        onClick={handleVoiceInput} 
        style={{ 
          backgroundColor: 'transparent',
          border: 'none',
          padding: '0',
          marginLeft: '0.5rem',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          opacity: 0.9,
          transition: 'opacity 0.2s',
          borderRadius: '50%', // クリック範囲を丸くする
          width: '40px',       // 正円にするための固定サイズ
          height: '40px',
        }}
        title="Voice Search"
        onMouseOver={(e) => e.currentTarget.style.opacity = '1'}
        onMouseOut={(e) => e.currentTarget.style.opacity = '0.9'}
      >
        <img 
          src="/mic-icon.png" 
          alt="Voice Search" 
          style={{ 
            width: '28px', 
            height: '28px', 
            objectFit: 'contain',
            // 生成された画像は「黒背景に白」なので、色反転は不要。
            // スクリーン合成で黒背景を透過させるだけでOK。
            mixBlendMode: 'screen'
          }}
        />
      </button>
    </form>
  );
};
