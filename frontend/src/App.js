import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './Dashboard';
import AudioPlayer from './AudioPlayer';
import SessionLogs from './components/SessionLogs';
import SuggestionPanel from './components/SuggestionPanel';  // ADD THIS
import NotificationModal from './components/NotificationModal';
import { generateMusic, getSessionAnalytics, getGPTSuggestions } from './api';  // ADD getGPTSuggestions

function App() {
  // Core application state
  const [currentUser, setCurrentUser] = useState({
    id: 'user_001',
    name: 'Patient Name',
    preferences: {
      musicStyle: 'classical',
      volume: 0.7,
      autoPlay: true
    }
  });

  const [appState, setAppState] = useState({
    isLoading: false,
    currentView: 'dashboard', // 'dashboard', 'player', 'logs', 'ai'
    theme: 'light' // 'light', 'dark', 'high-contrast'
  });

  const [musicState, setMusicState] = useState({
    currentTrack: null,
    playlist: [],
    isPlaying: false,
    volume: 0.7,
    emotion: 'calm', // 'calm', 'happy', 'nostalgic', 'energetic'
    category: 'soothing' // 'familiar', 'soothing', 'uplifting'
  });

  const [sessionData, setSessionData] = useState({
    startTime: null,
    responses: [],
    emotionLog: [],
    musicHistory: []
  });

  // Session related state
  const [sessionLogs, setSessionLogs] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [sessionActive, setSessionActive] = useState(false);
  const [emotionalState, setEmotionalState] = useState('Neutral');
  const [memoryResponse, setMemoryResponse] = useState('None');
  const [currentSong, setCurrentSong] = useState(null);

  // AI Suggestions state
  const [suggestions, setSuggestions] = useState(null);

  const [notification, setNotification] = useState({
    show: false,
    type: '', // 'success', 'error', 'info', 'warning'
    title: '',
    message: ''
  });

  // Initialize session when component mounts
  useEffect(() => {
    initializeSession();
    loadUserPreferences();
    loadAnalytics();
  }, []);

  // Fetch suggestions when relevant state changes
  useEffect(() => {
    if (sessionActive) {
      fetchSuggestions();
    }
  }, [emotionalState, memoryResponse, currentSong, sessionActive]);

  const loadAnalytics = async () => {
    try {
      const data = await getSessionAnalytics(7);
      setAnalytics(data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  };

  const fetchSuggestions = async () => {
    if (!sessionActive) {
      console.log('Session not active, skipping suggestions fetch');
      return;
    }

    try {
      console.log('Fetching suggestions...');
      const suggestions = await getGPTSuggestions({
        emotional_state: emotionalState,
        current_song: currentSong?.name || currentSong?.title,
        memory_response: memoryResponse
      });
      setSuggestions(suggestions);
      console.log('Suggestions received:', suggestions);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      // Use default suggestions if API fails
      setSuggestions({
        memory_prompts: [
          "Tell me about your favorite music from when you were young",
          "What songs did you dance to at your wedding?",
          "Do you remember any songs your parents used to sing?"
        ],
        activity_suggestions: [
          "Try gentle swaying to the rhythm",
          "Encourage humming along",
          "Ask about memories related to this song"
        ],
        care_tips: [
          "Patient seems receptive to music therapy today",
          "Consider playing more familiar songs",
          "Good time for reminiscence therapy"
        ]
      });
    }
  };

  // Initialize a new therapy session
  const initializeSession = () => {
    setSessionData({
      startTime: new Date().toISOString(),
      responses: [],
      emotionLog: [],
      musicHistory: []
    });
  };

  // Load user preferences from localStorage or backend
  const loadUserPreferences = () => {
    const savedPreferences = localStorage.getItem('userPreferences');
    if (savedPreferences) {
      const prefs = JSON.parse(savedPreferences);
      setCurrentUser(prev => ({
        ...prev,
        preferences: { ...prev.preferences, ...prefs }
      }));
      setMusicState(prev => ({
        ...prev,
        volume: prefs.volume || 0.7
      }));
    }
  };

  // Save user preferences
  // eslint-disable-next-line no-unused-vars
  const saveUserPreferences = (preferences) => {
    localStorage.setItem('userPreferences', JSON.stringify(preferences));
    setCurrentUser(prev => ({
      ...prev,
      preferences: { ...prev.preferences, ...preferences }
    }));
  };

  // Handle emotion selection
  const handleEmotionSelect = (emotion) => {
    setMusicState(prev => ({ ...prev, emotion }));
    setSessionData(prev => ({
      ...prev,
      emotionLog: [...prev.emotionLog, {
        emotion,
        timestamp: new Date().toISOString()
      }]
    }));

    // Map emotion to category
    const emotionToCategoryMap = {
      calm: 'soothing',
      happy: 'uplifting',
      nostalgic: 'familiar',
      energetic: 'uplifting'
    };

    const category = emotionToCategoryMap[emotion] || 'soothing';
    setMusicState(prev => ({ ...prev, category }));
  };

  // Handle memory response
  const handleMemoryResponse = (response) => {
    setSessionData(prev => ({
      ...prev,
      responses: [...prev.responses, {
        ...response,
        timestamp: new Date().toISOString()
      }]
    }));
  };

  // Handle music generation
  const handleGenerateMusic = async (prompt) => {
    setAppState(prev => ({ ...prev, isLoading: true }));

    try {
      const response = await generateMusic({
        prompt,
        emotion: musicState.emotion,
        userId: currentUser.id
      });

      if (response.success) {
        setMusicState(prev => ({
          ...prev,
          currentTrack: response.track,
          playlist: [...prev.playlist, response.track]
        }));

        showNotification('success', 'Music Generated', 'New track has been created successfully');
      }
    } catch (error) {
      showNotification('error', 'Generation Failed', error.message);
    } finally {
      setAppState(prev => ({ ...prev, isLoading: false }));
    }
  };

  // Show notification helper
  const showNotification = (type, title, message) => {
    setNotification({
      show: true,
      type,
      title,
      message
    });

    // Auto-hide after 5 seconds
    setTimeout(() => {
      setNotification(prev => ({ ...prev, show: false }));
    }, 5000);
  };

  // Handle view switching
  const switchView = (view) => {
    setAppState(prev => ({ ...prev, currentView: view }));
    // Fetch suggestions when AI tab is opened
    if (view === 'ai' && sessionActive) {
      fetchSuggestions();
    }
  };

  // Handle theme change
  const handleThemeChange = (theme) => {
    setAppState(prev => ({ ...prev, theme }));
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('appTheme', theme);
  };

  // Load saved theme on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('appTheme') || 'light';
    handleThemeChange(savedTheme);
  }, []);

  return (
    <div className={`app-container ${appState.theme}`}>
      {/* App Header */}
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">
            <span className="icon">🎵</span>
            MusicAlzheimer Therapy
          </h1>

          <nav className="app-nav">
            <button
              className={`nav-btn ${appState.currentView === 'dashboard' ? 'active' : ''}`}
              onClick={() => switchView('dashboard')}
              aria-label="Dashboard"
            >
              Dashboard
            </button>
            <button
              className={`nav-btn ${appState.currentView === 'player' ? 'active' : ''}`}
              onClick={() => switchView('player')}
              aria-label="Music Player"
            >
              Player
            </button>
            <button
              className={`nav-btn ${appState.currentView === 'logs' ? 'active' : ''}`}
              onClick={() => switchView('logs')}
              aria-label="Session Logs"
            >
              Logs
            </button>
            <button
              className={`nav-btn ${appState.currentView === 'ai' ? 'active' : ''}`}
              onClick={() => switchView('ai')}
              aria-label="AI Assistant"
            >
              AI Assistant
            </button>
          </nav>

          <div className="header-controls">
            {/* Theme Switcher */}
            <div className="theme-switcher">
              <button
                onClick={() => handleThemeChange('light')}
                className={appState.theme === 'light' ? 'active' : ''}
                aria-label="Light theme"
              >
                ☀️
              </button>
              <button
                onClick={() => handleThemeChange('dark')}
                className={appState.theme === 'dark' ? 'active' : ''}
                aria-label="Dark theme"
              >
                🌙
              </button>
              <button
                onClick={() => handleThemeChange('high-contrast')}
                className={appState.theme === 'high-contrast' ? 'active' : ''}
                aria-label="High contrast theme"
              >
                ⚡
              </button>
            </div>

            {/* User Info */}
            <div className="user-info">
              <span className="user-name">{currentUser.name}</span>
              <span className="user-avatar">👤</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="app-main">
        {appState.isLoading && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <p>Processing...</p>
          </div>
        )}

        {/* Dashboard View */}
        {appState.currentView === 'dashboard' && (
          <Dashboard
            user={currentUser}
            musicState={musicState}
            sessionData={sessionData}
            sessionLogs={sessionLogs}
            analytics={analytics}
            sessionActive={sessionActive}
            setSessionActive={setSessionActive}
            emotionalState={emotionalState}
            setEmotionalState={setEmotionalState}
            memoryResponse={memoryResponse}
            setMemoryResponse={setMemoryResponse}
            currentSong={currentSong}
            setCurrentSong={setCurrentSong}
            onEmotionSelect={handleEmotionSelect}
            onMemoryResponse={handleMemoryResponse}
            onGenerateMusic={handleGenerateMusic}
            onMusicStateChange={setMusicState}
            onNotification={showNotification}
            setSessionLogs={setSessionLogs}
            loadAnalytics={loadAnalytics}
          />
        )}

        {/* Player View */}
        {appState.currentView === 'player' && (
          <AudioPlayer
            currentTrack={musicState.currentTrack || currentSong}
            playlist={musicState.playlist}
            isPlaying={musicState.isPlaying}
            volume={musicState.volume}
            onPlayPause={() => setMusicState(prev => ({
              ...prev,
              isPlaying: !prev.isPlaying
            }))}
            onVolumeChange={(volume) => setMusicState(prev => ({
              ...prev,
              volume
            }))}
            onTrackChange={(track) => {
              setMusicState(prev => ({
                ...prev,
                currentTrack: track
              }));
              setCurrentSong(track);
            }}
          />
        )}

        {/* Logs View */}
        {appState.currentView === 'logs' && (
          <div className="logs-view-container">
            <SessionLogs
              logs={sessionLogs}
              analytics={analytics}
              sessions={sessionLogs}
              onExportSession={(sessionIds) => {
                console.log('Export sessions:', sessionIds);
                showNotification('info', 'Export', 'Session export functionality to be implemented');
              }}
              onDeleteSession={(sessionIds) => {
                console.log('Delete sessions:', sessionIds);
                setSessionLogs(prev => prev.filter(log => !sessionIds.includes(log.id)));
                showNotification('success', 'Deleted', 'Sessions deleted successfully');
              }}
              onViewDetails={(session) => {
                console.log('View details:', session);
                showNotification('info', 'Details', 'Detailed view to be implemented');
              }}
            />
          </div>
        )}

        {/* AI Assistant View */}
        {appState.currentView === 'ai' && (
          <div className="ai-view-container">
            <div className="ai-header">
              <h2>🤖 AI Assistant</h2>
              {!sessionActive && (
                <div className="ai-notice">
                  <p>⚠️ Start a session in the Dashboard to enable AI suggestions</p>
                </div>
              )}
            </div>

            <SuggestionPanel
              suggestions={suggestions}
              emotionalState={emotionalState}
              memoryResponse={memoryResponse}
              onSuggestionAccept={(suggestion) => {
                console.log('Suggestion accepted:', suggestion);
                showNotification('info', 'Suggestion Applied', suggestion);
              }}
              onRefresh={() => {
                console.log('Refreshing suggestions');
                fetchSuggestions();
              }}
            />
          </div>
        )}
      </main>

      {/* Notification Modal */}
      {notification.show && (
        <NotificationModal
          type={notification.type}
          title={notification.title}
          message={notification.message}
          onClose={() => setNotification(prev => ({ ...prev, show: false }))}
        />
      )}

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <p>© 2024 MusicAlzheimer Therapy System</p>
          <p className="session-info">
            Session Active: {sessionData.startTime ?
              `${Math.floor((new Date() - new Date(sessionData.startTime)) / 60000)} minutes` :
              'Not started'}
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;