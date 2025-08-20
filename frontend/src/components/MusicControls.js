import React, { useState } from 'react';
import './MusicControls.css';

const MusicControls = ({
  currentTrack,
  isPlaying,
  volume,
  emotion,
  category,
  onPlayPause,
  onStop,
  onVolumeChange,
  onEmotionChange,
  onCategoryChange,
  onGenerateMusic,
  onOpenLibrary,
  onShuffle,
  disabled = false
}) => {
  const [showVolumeSlider, setShowVolumeSlider] = useState(false);
  const [showEmotionPanel, setShowEmotionPanel] = useState(false);

  const emotions = [
    { id: 'calm', label: 'Calm', icon: '😌', color: '#60A5FA' },
    { id: 'happy', label: 'Happy', icon: '😊', color: '#FCD34D' },
    { id: 'nostalgic', label: 'Nostalgic', icon: '🥰', color: '#F9A8D4' },
    { id: 'energetic', label: 'Energetic', icon: '⚡', color: '#FB923C' }
  ];

  const categories = [
    { id: 'familiar', label: 'Familiar', icon: '🏠' },
    { id: 'soothing', label: 'Soothing', icon: '🌊' },
    { id: 'uplifting', label: 'Uplifting', icon: '🌟' }
  ];

  const handleEmotionSelect = (emotionId) => {
    onEmotionChange(emotionId);
    setShowEmotionPanel(false);
  };

  const getVolumeIcon = () => {
    if (volume === 0) return '🔇';
    if (volume < 0.3) return '🔈';
    if (volume < 0.7) return '🔉';
    return '🔊';
  };

  return (
    <div className={`music-controls ${disabled ? 'disabled' : ''}`}>
      {/* Main Control Bar */}
      <div className="controls-main">
        {/* Track Info */}
        <div className="controls-track-info">
          <div className="track-mini-artwork">
            {currentTrack?.artwork ? (
              <img src={currentTrack.artwork} alt={currentTrack.title} />
            ) : (
              <span className="artwork-placeholder-mini">🎵</span>
            )}
          </div>
          <div className="track-mini-details">
            <span className="track-mini-title">
              {currentTrack?.title || 'No track selected'}
            </span>
            <span className="track-mini-artist">
              {currentTrack?.artist || 'Select a track to begin'}
            </span>
          </div>
        </div>

        {/* Playback Controls */}
        <div className="controls-playback">
          <button
            className="control-btn-mini"
            onClick={onPlayPause}
            disabled={!currentTrack || disabled}
            aria-label={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? '⏸️' : '▶️'}
          </button>

          <button
            className="control-btn-mini"
            onClick={onStop}
            disabled={!currentTrack || disabled}
            aria-label="Stop"
          >
            ⏹️
          </button>

          <button
            className="control-btn-mini"
            onClick={onShuffle}
            disabled={disabled}
            aria-label="Shuffle"
          >
            🔀
          </button>
        </div>

        {/* Emotion & Category Controls */}
        <div className="controls-mood">
          <div className="emotion-selector-mini">
            <button
              className="emotion-btn-mini"
              onClick={() => setShowEmotionPanel(!showEmotionPanel)}
              disabled={disabled}
              style={{
                backgroundColor: emotions.find(e => e.id === emotion)?.color + '20'
              }}
            >
              <span className="emotion-icon">
                {emotions.find(e => e.id === emotion)?.icon || '😊'}
              </span>
              <span className="emotion-label">
                {emotions.find(e => e.id === emotion)?.label || 'Select Mood'}
              </span>
              <span className="dropdown-arrow">▼</span>
            </button>

            {showEmotionPanel && (
              <div className="emotion-dropdown">
                {emotions.map(e => (
                  <button
                    key={e.id}
                    className={`emotion-option ${emotion === e.id ? 'active' : ''}`}
                    onClick={() => handleEmotionSelect(e.id)}
                    style={{
                      backgroundColor: emotion === e.id ? e.color + '30' : 'transparent'
                    }}
                  >
                    <span>{e.icon}</span>
                    <span>{e.label}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="category-selector-mini">
            {categories.map(cat => (
              <button
                key={cat.id}
                className={`category-btn-mini ${category === cat.id ? 'active' : ''}`}
                onClick={() => onCategoryChange(cat.id)}
                disabled={disabled}
                title={cat.label}
              >
                {cat.icon}
              </button>
            ))}
          </div>
        </div>

        {/* Volume & Actions */}
        <div className="controls-actions">
          <div className="volume-control-mini">
            <button
              className="volume-btn-mini"
              onClick={() => setShowVolumeSlider(!showVolumeSlider)}
              disabled={disabled}
            >
              {getVolumeIcon()}
            </button>

            {showVolumeSlider && (
              <div className="volume-slider-popup">
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={volume}
                  onChange={(e) => onVolumeChange(parseFloat(e.target.value))}
                  className="volume-slider-vertical"
                  orient="vertical"
                />
                <span className="volume-label">{Math.round(volume * 100)}%</span>
              </div>
            )}
          </div>

          <button
            className="action-btn-mini generate"
            onClick={onGenerateMusic}
            disabled={disabled}
            title="Generate AI Music"
          >
            <span>🎨</span>
            <span className="btn-label">Generate</span>
          </button>

          <button
            className="action-btn-mini library"
            onClick={onOpenLibrary}
            disabled={disabled}
            title="Music Library"
          >
            <span>📚</span>
            <span className="btn-label">Library</span>
          </button>
        </div>
      </div>

      {/* Quick Stats Bar */}
      <div className="controls-stats">
        <div className="stat-item">
          <span className="stat-label">Session</span>
          <span className="stat-value">Active</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Mood</span>
          <span className="stat-value">{emotion || 'None'}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Response</span>
          <span className="stat-value">Good</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Engagement</span>
          <span className="stat-value">High</span>
        </div>
      </div>
    </div>
  );
};

export default MusicControls;