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
        className={styles.searchButton}
        style={{ 
          backgroundColor: '#fff', // 白背景を明示
          padding: '0',           // 画像を最大化するためパディング削除
          border: 'none',
          borderRadius: '50%',    // 完全な丸にする
          width: '42px',          // Searchボタンの高さに合わせる
          height: '42px',
          minWidth: '42px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',     // 四角い画像の角を隠す
          marginLeft: '0.5rem'
        }}
        title="Voice Search"
      >
        <img 
          src="/mic-icon.png" 
          alt="Voice Search" 
          style={{ 
            width: '24px', 
            height: '24px', 
            objectFit: 'contain',
            mixBlendMode: 'multiply' // 画像の白背景をボタンの白背景と馴染ませる（念のため）
          }}
        />
      </button>
    </form>
  );
};
