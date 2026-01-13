import React, { useState } from 'react';
import styles from '../../app/page.module.css';

interface SearchFormProps {
  onSearch: (query: string) => void;
}

export const SearchForm: React.FC<SearchFormProps> = ({ onSearch }) => {
  const [query, setQuery] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const recognitionRef = React.useRef<any>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query);
  };

  const handleVoiceInput = () => {
    // Stop recording if already active (Toggle OFF)
    if (isRecording) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      return; // State will be updated in onend
    }

    // Start recording (Toggle ON)
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("このブラウザでは音声認識がサポートされていません。Chromeなどでお試しください。");
      return;
    }

    // Create new instance if not exists
    if (!recognitionRef.current) {
      const recognition = new SpeechRecognition();
      recognition.lang = 'ja-JP';
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onresult = (event: any) => {
        const voiceResult = event.results[0][0].transcript;
        console.log('音声認識結果:', voiceResult);
        setQuery(voiceResult);
        onSearch(voiceResult);
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognition.onerror = (event: any) => {
        console.error('音声認識エラー:', event.error);
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
    }

    try {
      recognitionRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Failed to start recognition:", error);
      setIsRecording(false);
    }
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
        className={styles.micButton}
        title={isRecording ? "Stop Recording" : "Start Voice Search"}
        style={isRecording ? { backgroundColor: '#ffebee', opacity: 1 } : {}}
      >
        <img 
          src="/mic-icon.png" 
          alt="Voice Search" 
          style={isRecording ? { filter: 'invert(1)' } : {}} 
        />
      </button>
    </form>
  );
};
