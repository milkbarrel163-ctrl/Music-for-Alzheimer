import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import AudioPlayer from './AudioPlayer';
import GenerateMusicModal from './components/GenerateMusicModal';
import MusicLibraryModal from './components/MusicLibraryModal';
import { generateMusic, getSessionAnalytics, getGPTSuggestions, startSession, logSession, getMusicByCategory } from './api';

function App() {
  // Core state
  const [currentSong, setCurrentSong] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(0.7);
  const [emotionalState, setEmotionalState] = useState('Neutral');
  const [memoryResponse, setMemoryResponse] = useState('None');
  const [musicCategory, setMusicCategory] = useState('familiar');

  // Session management
  const [sessionId, setSessionId] = useState(null);
  const [sessionStartTime, setSessionStartTime] = useState(null);
  const [sessionLogs, setSessionLogs] = useState([]);
  const sessionIntervalRef = useRef(null);

  // Music library
  const [musicLibrary, setMusicLibrary] = useState({
    familiar: [],
    soothing: [],
    uplifting: []
  });

  // AI Suggestions
  const [suggestions, setSuggestions] = useState(null);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [showLibraryModal, setShowLibraryModal] = useState(false);

  // Quick notification
  const [notification, setNotification] = useState('');

  // Initialize
  useEffect(() => {
    loadMusicLibrary();
    loadRecentLogs();
  }, []);

  // Auto-manage sessions based on playback
  useEffect(() => {
    if (isPlaying && !sessionId) {
      // Auto-start session when music starts
      startNewSession();
    } else if (!isPlaying && sessionId) {
      // Auto-end session when music stops
      endCurrentSession();
    }
  }, [isPlaying]);

  // Auto-log every 30 seconds during playback
  useEffect(() => {
    if (isPlaying && sessionId) {
      sessionIntervalRef.current = setInterval(() => {
        logSessionData();
      }, 30000); // Log every 30 seconds
    } else {
      if (sessionIntervalRef.current) {
        clearInterval(sessionIntervalRef.current);
      }
    }
    return () => {
      if (sessionIntervalRef.current) {
        clearInterval(sessionIntervalRef.current);
      }
    };
  }, [isPlaying, sessionId, emotionalState, memoryResponse]);

  // Fetch AI suggestions when state changes
  useEffect(() => {
    if (isPlaying && currentSong) {
      fetchSuggestions();
    }
  }, [emotionalState, memoryResponse, currentSong, isPlaying]);

  const loadMusicLibrary = async () => {
    try {
      const categories = ['familiar', 'soothing', 'uplifting'];
      const library = {};

      for (const category of categories) {
        const songs = await getMusicByCategory(category);
        library[category] = songs.map((song, index) => ({
          id: `${category}_${index}`,
          title: song.name,
          artist: 'Various',
          filename: song.filename,
          path: song.path,
          url: `http://localhost:8000${song.path}`,
          category: category
        }));
      }

      setMusicLibrary(library);

      // Auto-select first familiar song
      if (library.familiar && library.familiar.length > 0) {
        setCurrentSong(library.familiar[0]);
      }
    } catch (error) {
      console.error('Error loading music:', error);
      showNotification('Error loading music library');
    }
  };

  const loadRecentLogs = () => {
    // Load from localStorage or API
    const saved = localStorage.getItem('sessionLogs');
    if (saved) {
      setSessionLogs(JSON.parse(saved).slice(-5)); // Last 5 sessions
    }
  };

  const startNewSession = async () => {
    const newSessionId = `session_${Date.now()}`;
    try {
      await startSession({
        session_id: newSessionId,
        emotional_state: emotionalState
      });

      setSessionId(newSessionId);
      setSessionStartTime(new Date());
      showNotification('Session started');
    } catch (error) {
      console.error('Error starting session:', error);
    }
  };

  const endCurrentSession = async () => {
    if (sessionId) {
      await logSessionData();
      setSessionId(null);
      setSessionStartTime(null);
      showNotification('Session saved');
    }
  };

  const logSessionData = async () => {
    if (!sessionId || !currentSong) return;

    const duration = Math.floor((Date.now() - sessionStartTime) / 1000);

    try {
      await logSession({
        session_id: sessionId,
        emotional_state: emotionalState,
        memory_response: memoryResponse,
        song_played: currentSong.title,
        song_category: musicCategory,
        duration_seconds: duration,
        notes: ''
      });

      const logEntry = {
        id: sessionId,
        time: new Date().toLocaleTimeString(),
        song: currentSong.title,
        emotion: emotionalState,
        response: memoryResponse,
        duration: `${Math.floor(duration / 60)}m`
      };

      const newLogs = [...sessionLogs, logEntry].slice(-5); // Keep last 5
      setSessionLogs(newLogs);
      localStorage.setItem('sessionLogs', JSON.stringify(newLogs));
    } catch (error) {
      console.error('Error logging session:', error);
    }
  };

  const fetchSuggestions = async () => {
    try {
      const suggestions = await getGPTSuggestions({
        emotional_state: emotionalState,
        current_song: currentSong?.title,
        memory_response: memoryResponse
      });
      setSuggestions(suggestions);
    } catch (error) {
      // Fallback suggestions
      setSuggestions({
        memory_prompts: ["Ask about their favorite songs", "Discuss memories from this era"],
        activity_suggestions: ["Gentle swaying to the music", "Sing along if comfortable"],
        care_tips: ["Patient is responding well to music", "Consider similar songs"]
      });
    }
  };

  const handlePlayPause = () => {
    if (!currentSong) {
      // Auto-select first song from current category
      const songs = musicLibrary[musicCategory];
      if (songs && songs.length > 0) {
        setCurrentSong(songs[0]);
        setIsPlaying(true);
      }
    } else {
      setIsPlaying(!isPlaying);
    }
  };

  const handleSongSelect = (song) => {
    if (sessionId && currentSong) {
      logSessionData(); // Log previous song before switching
    }
    setCurrentSong(song);
    setIsPlaying(true);
  };

  const handleQuickPlay = (category) => {
    setMusicCategory(category);
    const songs = musicLibrary[category];
    if (songs && songs.length > 0) {
      const randomSong = songs[Math.floor(Math.random() * songs.length)];
      handleSongSelect(randomSong);
    }
  };

  const showNotification = (message) => {
    setNotification(message);
    setTimeout(() => setNotification(''), 3000);
  };

  // Emotion color mapping
  const emotionColors = {
    'Distressed': '#ef4444',
    'Neutral': '#6b7280',
    'Content': '#10b981',
    'Joyful': '#fbbf24'
  };

  return (
    <div className="app-simplified">
      {/* Header - Minimal */}
      <header className="app-header-simple">
        <h1>🎵 Music Therapy</h1>
        <div className="session-indicator">
          {isPlaying ? (
            <span className="session-active">● Recording Session</span>
          ) : (
            <span className="session-inactive">● Ready</span>
          )}
        </div>
      </header>

      {/* Main Content - Single Page */}
      <main className="app-main-unified">

        {/* Section 1: Quick Play */}
        <section className="quick-play-section">
          <div className="current-track-display">
            <div className="track-icon">🎵</div>
            <div className="track-info">
              <h2>{currentSong?.title || 'Select a song'}</h2>
              <p>{currentSong?.artist || 'No song playing'}</p>
            </div>
            <div className="play-controls">
              <button
                className="btn-play-main"
                onClick={handlePlayPause}
              >
                {isPlaying ? '⏸️' : '▶️'}
              </button>
              <div className="volume-control">
                <span>🔊</span>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={volume}
                  onChange={(e) => setVolume(parseFloat(e.target.value))}
                />
              </div>
            </div>
          </div>

          {/* Quick Category Buttons */}
          <div className="quick-categories">
            <button
              className={`category-btn ${musicCategory === 'familiar' ? 'active' : ''}`}
              onClick={() => handleQuickPlay('familiar')}
            >
              🏠 Familiar
            </button>
            <button
              className={`category-btn ${musicCategory === 'soothing' ? 'active' : ''}`}
              onClick={() => handleQuickPlay('soothing')}
            >
              🌊 Soothing
            </button>
            <button
              className={`category-btn ${musicCategory === 'uplifting' ? 'active' : ''}`}
              onClick={() => handleQuickPlay('uplifting')}
            >
              ⭐ Uplifting
            </button>
            <button
              className="category-btn library"
              onClick={() => setShowLibraryModal(true)}
            >
              📚 Browse Library
            </button>
            <button
              className="category-btn generate"
              onClick={() => setShowGenerateModal(true)}
            >
              🎨 Generate New
            </button>
          </div>

          {/* Song List - Compact */}
          <div className="song-list-compact">
            {musicLibrary[musicCategory]?.slice(0, 4).map(song => (
              <button
                key={song.id}
                className={`song-item ${currentSong?.id === song.id ? 'active' : ''}`}
                onClick={() => handleSongSelect(song)}
              >
                {song.title}
              </button>
            ))}
          </div>
        </section>

        {/* Section 2: Patient Status */}
        <section className="patient-status-section">
          <h3>Patient Status</h3>

          {/* Emotional State */}
          <div className="status-group">
            <label>Emotional State:</label>
            <div className="emotion-buttons">
              {['Distressed', 'Neutral', 'Content', 'Joyful'].map(emotion => (
                <button
                  key={emotion}
                  className={`emotion-btn ${emotionalState === emotion ? 'active' : ''}`}
                  onClick={() => setEmotionalState(emotion)}
                  style={{
                    backgroundColor: emotionalState === emotion ? emotionColors[emotion] : 'transparent',
                    borderColor: emotionColors[emotion]
                  }}
                >
                  {emotion === 'Distressed' && '😟'}
                  {emotion === 'Neutral' && '😐'}
                  {emotion === 'Content' && '😊'}
                  {emotion === 'Joyful' && '😄'}
                  {emotion}
                </button>
              ))}
            </div>
          </div>

          {/* Memory Response */}
          <div className="status-group">
            <label>Memory Response:</label>
            <div className="response-buttons">
              {['None', 'Some', 'Strong'].map(response => (
                <button
                  key={response}
                  className={`response-btn ${memoryResponse === response ? 'active' : ''}`}
                  onClick={() => setMemoryResponse(response)}
                  disabled={!isPlaying}
                >
                  {response}
                </button>
              ))}
            </div>
          </div>

          {/* AI Suggestions - Inline */}
          {suggestions && isPlaying && (
            <div className="ai-suggestions-inline">
              <h4>💡 Suggestions</h4>
              <div className="suggestion-cards">
                <div className="suggestion-card">
                  <strong>Try asking:</strong>
                  <p>{suggestions.memory_prompts?.[0] || 'Ask about memories'}</p>
                </div>
                <div className="suggestion-card">
                  <strong>Activity:</strong>
                  <p>{suggestions.activity_suggestions?.[0] || 'Encourage participation'}</p>
                </div>
                <div className="suggestion-card">
                  <strong>Note:</strong>
                  <p>{suggestions.care_tips?.[0] || 'Patient responding well'}</p>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Section 3: Recent Sessions */}
        <section className="sessions-section">
          <h3>Recent Sessions</h3>
          <div className="session-logs-compact">
            {sessionLogs.length === 0 ? (
              <p className="no-sessions">No sessions yet today</p>
            ) : (
              <table className="logs-table">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Song</th>
                    <th>Emotion</th>
                    <th>Response</th>
                    <th>Duration</th>
                  </tr>
                </thead>
                <tbody>
                  {sessionLogs.map(log => (
                    <tr key={log.id}>
                      <td>{log.time}</td>
                      <td>{log.song}</td>
                      <td>
                        <span style={{ color: emotionColors[log.emotion] }}>
                          {log.emotion}
                        </span>
                      </td>
                      <td>{log.response}</td>
                      <td>{log.duration}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </section>

      </main>

      {/* Notification Toast */}
      {notification && (
        <div className="notification-toast">
          {notification}
        </div>
      )}

      {/* Generate Music Modal */}
      {showGenerateModal && (
        <GenerateMusicModal
          onClose={() => setShowGenerateModal(false)}
          onGenerated={() => {
            loadMusicLibrary();
            showNotification('Music generated successfully');
          }}
        />
      )}

      {/* Music Library Modal */}
      {showLibraryModal && (
        <MusicLibraryModal
          musicLibrary={musicLibrary}
          onSelectTrack={handleSongSelect}
          onAddToPlaylist={() => {}} // Disabled - no playlist management
          currentTrack={currentSong}
          onClose={() => setShowLibraryModal(false)}
        />
      )}

      {/* Hidden Audio Player */}
      <div style={{ display: 'none' }}>
        <AudioPlayer
          currentTrack={currentSong}
          playlist={musicLibrary[musicCategory] || []}
          isPlaying={isPlaying}
          volume={volume}
          onPlayPause={() => setIsPlaying(!isPlaying)}
          onVolumeChange={setVolume}
          onTrackChange={handleSongSelect}
        />
      </div>
    </div>
  );
}

export default App;