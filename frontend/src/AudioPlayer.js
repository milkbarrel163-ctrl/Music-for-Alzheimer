import React, { useState, useEffect, useRef } from 'react';
import './AudioPlayer.css';

const AudioPlayer = ({
  currentTrack,
  playlist = [],
  isPlaying,
  volume = 0.7,
  onPlayPause,
  onVolumeChange,
  onTrackChange,
  onNotification
}) => {
  const audioRef = useRef(null);
  const progressRef = useRef(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [showPlaylist, setShowPlaylist] = useState(false);
  const [repeatMode, setRepeatMode] = useState('none'); // 'none', 'one', 'all'
  const [shuffleMode, setShuffleMode] = useState(false);
  const [playedTracks, setPlayedTracks] = useState([]);

  // Initialize audio element
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    audio.volume = volume;

    const handleLoadStart = () => setIsLoading(true);
    const handleLoadedData = () => {
      setIsLoading(false);
      setDuration(audio.duration);
    };
    const handleTimeUpdate = () => setCurrentTime(audio.currentTime);
    const handleEnded = () => handleTrackEnd();
    const handleError = (e) => {
      setIsLoading(false);
      if (onNotification) {
        onNotification('error', 'Playback Error', 'Failed to load the audio file');
      }
    };

    audio.addEventListener('loadstart', handleLoadStart);
    audio.addEventListener('loadeddata', handleLoadedData);
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);

    return () => {
      audio.removeEventListener('loadstart', handleLoadStart);
      audio.removeEventListener('loadeddata', handleLoadedData);
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
    };
  }, [currentTrack]);

  // Handle play/pause state
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !currentTrack) return;

    if (isPlaying) {
      audio.play().catch(err => {
        console.error('Playback failed:', err);
        onPlayPause();
      });
    } else {
      audio.pause();
    }
  }, [isPlaying, currentTrack]);

  // Update volume
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
    }
  }, [volume]);

  // Handle track end
  const handleTrackEnd = () => {
    if (repeatMode === 'one') {
      // Repeat current track
      audioRef.current.currentTime = 0;
      audioRef.current.play();
    } else if (playlist.length > 0) {
      // Play next track
      playNextTrack();
    } else {
      onPlayPause(); // Stop playing
    }
  };

  // Play next track
  const playNextTrack = () => {
    if (playlist.length === 0) return;

    const currentIndex = playlist.findIndex(track => track.id === currentTrack?.id);
    let nextIndex;

    if (shuffleMode) {
      // Random track selection
      const unplayedTracks = playlist.filter(
        (track, index) => !playedTracks.includes(index) && index !== currentIndex
      );

      if (unplayedTracks.length === 0) {
        // All tracks played, reset
        setPlayedTracks([]);
        nextIndex = Math.floor(Math.random() * playlist.length);
      } else {
        const randomTrack = unplayedTracks[Math.floor(Math.random() * unplayedTracks.length)];
        nextIndex = playlist.indexOf(randomTrack);
      }

      setPlayedTracks(prev => [...prev, nextIndex]);
    } else {
      // Sequential playback
      nextIndex = currentIndex + 1;

      if (nextIndex >= playlist.length) {
        if (repeatMode === 'all') {
          nextIndex = 0;
        } else {
          onPlayPause(); // Stop at end
          return;
        }
      }
    }

    onTrackChange(playlist[nextIndex]);
  };

  // Play previous track
  const playPreviousTrack = () => {
    if (playlist.length === 0) return;

    const currentIndex = playlist.findIndex(track => track.id === currentTrack?.id);
    let prevIndex = currentIndex - 1;

    if (prevIndex < 0) {
      if (repeatMode === 'all') {
        prevIndex = playlist.length - 1;
      } else {
        prevIndex = 0;
      }
    }

    onTrackChange(playlist[prevIndex]);
  };

  // Seek to position
  const handleSeek = (e) => {
    const rect = progressRef.current.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    const newTime = percent * duration;

    audioRef.current.currentTime = newTime;
    setCurrentTime(newTime);
  };

  // Format time display
  const formatTime = (seconds) => {
    if (isNaN(seconds)) return '0:00';

    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Toggle repeat mode
  const toggleRepeatMode = () => {
    const modes = ['none', 'one', 'all'];
    const currentIndex = modes.indexOf(repeatMode);
    const nextIndex = (currentIndex + 1) % modes.length;
    setRepeatMode(modes[nextIndex]);
  };

  // Toggle shuffle mode
  const toggleShuffleMode = () => {
    setShuffleMode(!shuffleMode);
    setPlayedTracks([]);
  };

  return (
    <div className="audio-player">
      {/* Hidden audio element */}
      <audio
        ref={audioRef}
        src={currentTrack?.url}
        preload="metadata"
      />

      {/* Player Container */}
      <div className="player-container">
        {/* Track Info */}
        <div className="track-info">
          <div className="track-artwork">
            {currentTrack?.artwork ? (
              <img src={currentTrack.artwork} alt={currentTrack.title} />
            ) : (
              <div className="artwork-placeholder">🎵</div>
            )}
          </div>

          <div className="track-details">
            <h3 className="track-title">
              {currentTrack?.title || 'No track selected'}
            </h3>
            <p className="track-artist">
              {currentTrack?.artist || 'Unknown artist'}
            </p>
            <p className="track-category">
              {currentTrack?.category || 'Uncategorized'}
            </p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="progress-section">
          <span className="time-display">{formatTime(currentTime)}</span>
          <div
            className="progress-bar"
            ref={progressRef}
            onClick={handleSeek}
          >
            <div
              className="progress-fill"
              style={{ width: `${(currentTime / duration) * 100 || 0}%` }}
            >
              <span className="progress-handle"></span>
            </div>
          </div>
          <span className="time-display">{formatTime(duration)}</span>
        </div>

        {/* Playback Controls */}
        <div className="playback-controls">
          <button
            className={`control-btn ${shuffleMode ? 'active' : ''}`}
            onClick={toggleShuffleMode}
            title="Shuffle"
          >
            🔀
          </button>

          <button
            className="control-btn"
            onClick={playPreviousTrack}
            disabled={playlist.length === 0}
            title="Previous"
          >
            ⏮️
          </button>

          <button
            className="control-btn play-btn"
            onClick={onPlayPause}
            disabled={!currentTrack}
            title={isPlaying ? 'Pause' : 'Play'}
          >
            {isLoading ? '⏳' : isPlaying ? '⏸️' : '▶️'}
          </button>

          <button
            className="control-btn"
            onClick={playNextTrack}
            disabled={playlist.length === 0}
            title="Next"
          >
            ⏭️
          </button>

          <button
            className={`control-btn ${repeatMode !== 'none' ? 'active' : ''}`}
            onClick={toggleRepeatMode}
            title={`Repeat: ${repeatMode}`}
          >
            {repeatMode === 'one' ? '🔂' : '🔁'}
          </button>
        </div>

        {/* Volume and Playlist Controls */}
        <div className="secondary-controls">
          <div className="volume-control">
            <span className="volume-icon">
              {volume === 0 ? '🔇' : volume < 0.5 ? '🔉' : '🔊'}
            </span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={volume}
              onChange={(e) => onVolumeChange(parseFloat(e.target.value))}
              className="volume-slider"
            />
            <span className="volume-value">{Math.round(volume * 100)}%</span>
          </div>

          <button
            className="control-btn playlist-toggle"
            onClick={() => setShowPlaylist(!showPlaylist)}
            title="Toggle Playlist"
          >
            📋 Playlist ({playlist.length})
          </button>
        </div>
      </div>

      {/* Playlist Panel */}
      {showPlaylist && (
        <div className="playlist-panel">
          <h3 className="playlist-title">Current Playlist</h3>
          <div className="playlist-items">
            {playlist.length === 0 ? (
              <p className="empty-playlist">No tracks in playlist</p>
            ) : (
              playlist.map((track, index) => (
                <div
                  key={track.id}
                  className={`playlist-item ${track.id === currentTrack?.id ? 'active' : ''}`}
                  onClick={() => onTrackChange(track)}
                >
                  <span className="track-number">{index + 1}</span>
                  <div className="track-info-mini">
                    <span className="track-title-mini">{track.title}</span>
                    <span className="track-artist-mini">{track.artist}</span>
                  </div>
                  <span className="track-duration">
                    {track.duration || '0:00'}
                  </span>
                  {track.id === currentTrack?.id && isPlaying && (
                    <span className="playing-indicator">▶️</span>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AudioPlayer;