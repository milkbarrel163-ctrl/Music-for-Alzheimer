import React, { useState, useEffect } from 'react';
import './Dashboard.css';
import MusicControls from './components/MusicControls';
import MemoryResponseControls from './components/MemoryResponseControls';
import EmotionSelector from './components/EmotionSelector';
import GenerateMusicModal from './components/GenerateMusicModal';
import MusicLibraryModal from './components/MusicLibraryModal';
import NotificationModal from './components/NotificationModal';
import AudioPlayer from './AudioPlayer';
import { startSession, logSession, getMusicByCategory } from './api';

function Dashboard({
  // Props from App.js
  sessionLogs,
  analytics,
  setSessionLogs,
  loadAnalytics,
  sessionActive,
  setSessionActive,
  emotionalState,
  setEmotionalState,
  memoryResponse,
  setMemoryResponse,
  currentSong,
  setCurrentSong
}) {
  // Session state
  const [sessionId, setSessionId] = useState(null);
  const [sessionStartTime, setSessionStartTime] = useState(null);

  // Music state
  const [currentCategory, setCurrentCategory] = useState('familiar');
  const [isPlaying, setIsPlaying] = useState(false);
  const [musicLibrary, setMusicLibrary] = useState({
    soothing: [],
    familiar: [],
    uplifting: []
  });

  // UI state
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [showLibraryModal, setShowLibraryModal] = useState(false);
  const [notification, setNotification] = useState(null);

  // Initialize
  useEffect(() => {
    loadMusicLibrary();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Auto-select music category based on emotional state
  useEffect(() => {
    const categoryMap = {
      'Distressed': 'soothing',
      'Neutral': 'familiar',
      'Content': 'familiar',
      'Joyful': 'uplifting'
    };
    setCurrentCategory(categoryMap[emotionalState] || 'familiar');
  }, [emotionalState]);

  const loadMusicLibrary = async () => {
    try {
      const categories = ['soothing', 'familiar', 'uplifting'];
      const library = {};

      for (const category of categories) {
        const songs = await getMusicByCategory(category);
        console.log(`Songs from ${category}:`, songs);

        // Transform backend data to match MusicLibraryModal format
        library[category] = songs.map((song, index) => ({
          id: `${category}_${index}`,
          title: song.name,
          artist: 'Various',
          duration: '3:00',
          emotion: category === 'soothing' ? 'calm' :
                   category === 'uplifting' ? 'happy' : 'nostalgic',
          filename: song.filename,
          path: song.path,
          // Make sure we have the full URL for audio playback
          url: `http://localhost:8000${song.path}`
        }));
      }

      setMusicLibrary(library);
      console.log('Music library loaded:', library);

      // Auto-select first song if available
      if (library.familiar && library.familiar.length > 0) {
        console.log('Auto-selecting first familiar song:', library.familiar[0]);
      }
    } catch (error) {
      console.error('Error loading music library:', error);
      showNotification('Error loading music library', 'error');
    }
  };

  const handleStartSession = async () => {
    const newSessionId = `session_${Date.now()}`;
    try {
      await startSession({
        session_id: newSessionId,
        emotional_state: emotionalState
      });

      setSessionId(newSessionId);
      setSessionActive(true);
      setSessionStartTime(Date.now());
      setSessionLogs([]);
      showNotification('Session started successfully', 'success');
    } catch (error) {
      console.error('Error starting session:', error);
      showNotification('Error starting session', 'error');
    }
  };

  const handleEndSession = () => {
    if (currentSong && sessionActive) {
      logSessionData();
    }

    setSessionActive(false);
    setIsPlaying(false);
    setCurrentSong(null);
    showNotification('Session ended', 'info');
    loadAnalytics();
  };

  const logSessionData = async () => {
    if (!sessionId || !currentSong) return;

    const duration = Math.floor((Date.now() - sessionStartTime) / 1000);

    try {
      await logSession({
        session_id: sessionId,
        emotional_state: emotionalState,
        memory_response: memoryResponse,
        song_played: currentSong.name || currentSong.title,
        song_category: currentCategory,
        duration_seconds: duration,
        notes: ''
      });

      const logEntry = {
        id: `log_${Date.now()}`,
        timestamp: new Date().toISOString(),
        date: new Date().toISOString().split('T')[0],
        startTime: new Date(sessionStartTime).toLocaleTimeString(),
        emotional_state: emotionalState,
        patientMood: emotionalState.toLowerCase(),
        memory_response: memoryResponse,
        song_played: currentSong.name || currentSong.title,
        tracksPlayed: 1,
        duration: `${duration} sec`,
        engagement: memoryResponse === 'Strong' ? 'high' : memoryResponse === 'Some' ? 'medium' : 'low'
      };
      setSessionLogs(prev => [...prev, logEntry]);
    } catch (error) {
      console.error('Error logging session:', error);
    }
  };

  const handlePlaySong = (song) => {
    console.log('Playing song:', song);

    if (currentSong) {
      logSessionData();
    }

    // Ensure the song has all necessary properties for playback
    const songToPlay = {
      id: song.id,
      title: song.title || song.name || 'Unknown',
      name: song.title || song.name,
      artist: song.artist || 'Various',
      path: song.path,
      filename: song.filename,
      url: song.url || `http://localhost:8000${song.path}`,
      category: currentCategory,  // Add category for display
      ...song
    };

    setCurrentSong(songToPlay);
    setIsPlaying(true);
    setSessionStartTime(Date.now());

    console.log('Current song set to:', songToPlay);
    console.log('Audio URL:', songToPlay.url);
  };

  const handleStopMusic = () => {
    if (sessionActive && currentSong) {
      logSessionData();
    }
    setIsPlaying(false);
    setCurrentSong(null);
  };

  const handleEmotionalStateChange = (newState) => {
    setEmotionalState(newState);
    if (sessionActive && currentSong) {
      logSessionData();
    }
  };

  const handleMemoryResponseChange = (response) => {
    setMemoryResponse(response);
    if (sessionActive && currentSong) {
      logSessionData();
    }
  };

  const handleGenerateMusic = () => {
    setShowGenerateModal(true);
  };

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  return (
    <div className="dashboard dashboard-full-width">
      <header className="dashboard-header">
        <h1>🎵 Alzheimer's Music Therapy</h1>
        <div className="session-controls">
          {!sessionActive ? (
            <button className="btn btn-primary" onClick={handleStartSession}>
              Start Session
            </button>
          ) : (
            <>
              <span className="session-indicator">Session Active</span>
              <button className="btn btn-danger" onClick={handleEndSession}>
                End Session
              </button>
            </>
          )}
        </div>
      </header>

      <div className="dashboard-content-full">
        <div className="control-section">
          <EmotionSelector
            emotionalState={emotionalState}
            onChange={handleEmotionalStateChange}
            disabled={!sessionActive}
          />

          <MemoryResponseControls
            memoryResponse={memoryResponse}
            onChange={handleMemoryResponseChange}
            disabled={!sessionActive || !currentSong}
          />
          {(!sessionActive || !currentSong) && (
            <small style={{color: 'orange', fontSize: '12px', display: 'block', marginTop: '-10px'}}>
              {!sessionActive ? 'Start session to enable' : 'Select a song to enable memory response'}
            </small>
          )}
        </div>

        <MusicControls
          currentTrack={currentSong}
          category={currentCategory}
          musicLibrary={musicLibrary}
          isPlaying={isPlaying}
          disabled={!sessionActive}
          onCategoryChange={(category) => {
            console.log('Changing category to:', category);
            setCurrentCategory(category);
          }}
          onEmotionChange={(emotion) => {
            console.log('Changing emotion to:', emotion);
            const emotionMap = {
              'calm': 'Neutral',
              'happy': 'Joyful',
              'nostalgic': 'Content',
              'energetic': 'Joyful'
            };
            setEmotionalState(emotionMap[emotion] || 'Neutral');
          }}
          onPlayPause={() => {
            console.log('MusicControls play/pause clicked. Current song:', currentSong);
            console.log('Is playing:', isPlaying);
            if (currentSong) {
              setIsPlaying(!isPlaying);
            } else {
              // If no song selected, try to play first song from current category
              const categoryTracks = musicLibrary[currentCategory] || [];
              if (categoryTracks.length > 0) {
                console.log('No song selected, playing first track from category');
                handlePlaySong(categoryTracks[0]);
              } else {
                console.log('No songs available in current category');
              }
            }
          }}
          onStop={handleStopMusic}
          onVolumeChange={(volume) => {
            console.log('Volume changed to:', volume);
          }}
          onGenerateMusic={handleGenerateMusic}
          onShuffle={() => {
            const categoryTracks = musicLibrary[currentCategory] || [];
            if (categoryTracks.length > 0) {
              const randomTrack = categoryTracks[Math.floor(Math.random() * categoryTracks.length)];
              handlePlaySong(randomTrack);
            }
          }}
          emotion={emotionalState.toLowerCase()}
          volume={0.7}
          onOpenLibrary={() => {
            console.log('Opening library modal');
            console.log('Current music library:', musicLibrary);
            setShowLibraryModal(true);
          }}
          onOpenGenerator={() => {
            console.log('Opening generator modal');
            setShowGenerateModal(true);
          }}
        />

        {/* Debug info - uncomment to see current state */}
        {/*
        <div style={{background: '#e0e0e0', padding: '10px', margin: '10px 0', borderRadius: '5px', fontSize: '12px'}}>
          <strong>Debug Info:</strong>
          <div>Current Song: {currentSong ? currentSong.title || currentSong.name || 'Unnamed' : 'None'}</div>
          <div>Is Playing: {isPlaying ? 'Yes' : 'No'}</div>
          <div>Session Active: {sessionActive ? 'Yes' : 'No'}</div>
          <div>Audio URL: {currentSong?.url || 'No URL'}</div>
        </div>
        */}

        {/* AudioPlayer with correct props */}
        <AudioPlayer
          currentTrack={currentSong}  // Changed from 'song' to 'currentTrack'
          playlist={musicLibrary[currentCategory] || []}  // Show current category songs
          isPlaying={isPlaying}
          volume={0.7}
          onPlayPause={() => {
            console.log('AudioPlayer play/pause clicked');
            if (currentSong) {
              setIsPlaying(!isPlaying);
            } else {
              // If no song selected, play first song from current category
              const categoryTracks = musicLibrary[currentCategory] || [];
              if (categoryTracks.length > 0) {
                handlePlaySong(categoryTracks[0]);
              }
            }
          }}
          onVolumeChange={(newVolume) => {
            console.log('Volume changed to:', newVolume);
            // You can store volume in state if needed
          }}
          onTrackChange={(track) => {
            console.log('Track changed to:', track);
            handlePlaySong(track);
          }}
          onNotification={(type, title, message) => {
            console.log(`Notification: ${type} - ${title}: ${message}`);
            showNotification(message, type);
          }}
        />
      </div>

      {/* Modals */}
      {showGenerateModal && (
        <GenerateMusicModal
          onClose={() => setShowGenerateModal(false)}
          onGenerated={() => {
            loadMusicLibrary();
            showNotification('Music generated successfully', 'success');
          }}
        />
      )}

      {showLibraryModal && (
        <MusicLibraryModal
          musicLibrary={musicLibrary}
          onSelectTrack={handlePlaySong}
          onAddToPlaylist={(tracks) => {
            console.log('Add to playlist:', tracks);
          }}
          currentTrack={currentSong}
          onClose={() => setShowLibraryModal(false)}
        />
      )}

      {notification && (
        <NotificationModal
          message={notification.message}
          type={notification.type}
          onClose={() => setNotification(null)}
        />
      )}
    </div>
  );
}

export default Dashboard;