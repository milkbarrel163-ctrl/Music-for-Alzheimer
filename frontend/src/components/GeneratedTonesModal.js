import React, { useState, useRef, useEffect } from 'react';
import './GeneratedTonesModal.css';

const GeneratedTonesModal = ({
  isOpen,
  onClose,
  generatedTone = null,
  onSaveTone,
  onRegenerateTone,
  isGenerating = false
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [showWaveform, setShowWaveform] = useState(true);
  const [toneName, setToneName] = useState('');
  const [toneNotes, setToneNotes] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('soothing');
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);

  const audioRef = useRef(null);
  const canvasRef = useRef(null);
  const animationRef = useRef(null);

  // Advanced settings state
  const [advancedSettings, setAdvancedSettings] = useState({
    frequency: 440, // Hz
    waveType: 'sine', // sine, square, sawtooth, triangle
    reverb: 0.3,
    delay: 0,
    lowPass: 1000,
    highPass: 100,
    duration: 120 // seconds
  });

  // Sample generated tone data if not provided
  const sampleTone = {
    id: 'tone_001',
    name: 'Calming Waves',
    url: '#',
    duration: '2:30',
    category: 'soothing',
    emotion: 'calm',
    createdAt: new Date().toISOString(),
    parameters: {
      frequency: 432,
      waveType: 'sine',
      reverb: 0.4
    },
    waveformData: generateWaveformData()
  };

  const tone = generatedTone || sampleTone;

  // Generate sample waveform data
  function generateWaveformData() {
    const data = [];
    for (let i = 0; i < 100; i++) {
      data.push(Math.sin(i * 0.1) * 50 + Math.random() * 20);
    }
    return data;
  }

  // Draw waveform visualization
  useEffect(() => {
    if (showWaveform && canvasRef.current && tone.waveformData) {
      drawWaveform();
    }
  }, [showWaveform, tone, currentTime]);

  const drawWaveform = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const data = tone.waveformData || [];

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Set style
    ctx.strokeStyle = getComputedStyle(document.documentElement)
      .getPropertyValue('--primary-color');
    ctx.lineWidth = 2;

    // Draw waveform
    ctx.beginPath();
    const sliceWidth = width / data.length;
    let x = 0;

    for (let i = 0; i < data.length; i++) {
      const v = data[i] / 100;
      const y = (v * height) / 2 + height / 2;

      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }

      x += sliceWidth;
    }

    ctx.stroke();

    // Draw progress indicator
    if (duration > 0) {
      const progress = currentTime / duration;
      const progressX = width * progress;

      ctx.strokeStyle = getComputedStyle(document.documentElement)
        .getPropertyValue('--success-color');
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(progressX, 0);
      ctx.lineTo(progressX, height);
      ctx.stroke();
    }
  };

  // Handle play/pause
  const handlePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  // Handle save
  const handleSave = () => {
    if (!toneName.trim()) {
      alert('Please enter a name for the tone');
      return;
    }

    const toneData = {
      ...tone,
      name: toneName,
      notes: toneNotes,
      category: selectedCategory,
      savedAt: new Date().toISOString()
    };

    onSaveTone(toneData);
    handleClose();
  };

  // Handle regenerate
  const handleRegenerate = () => {
    const settings = showAdvancedSettings ? advancedSettings : null;
    onRegenerateTone(settings);
  };

  // Handle close
  const handleClose = () => {
    if (audioRef.current) {
      audioRef.current.pause();
    }
    setIsPlaying(false);
    setToneName('');
    setToneNotes('');
    onClose();
  };

  // Update advanced setting
  const updateAdvancedSetting = (key, value) => {
    setAdvancedSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  // Format time
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="generated-tones-modal" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="tones-modal-header">
          <h2 className="tones-modal-title">
            <span>🎵</span>
            Generated Tone
          </h2>
          <button className="modal-close" onClick={handleClose}>×</button>
        </div>

        {/* Main Content */}
        <div className="tones-modal-content">
          {/* Audio Player Section */}
          <div className="tone-player-section">
            <audio
              ref={audioRef}
              src={tone.url}
              onTimeUpdate={(e) => setCurrentTime(e.target.currentTime)}
              onLoadedMetadata={(e) => setDuration(e.target.duration)}
              onEnded={() => setIsPlaying(false)}
            />

            {/* Waveform Visualization */}
            {showWaveform && (
              <div className="waveform-container">
                <canvas
                  ref={canvasRef}
                  width={600}
                  height={150}
                  className="waveform-canvas"
                />
                <div className="waveform-time">
                  <span>{formatTime(currentTime)}</span>
                  <span>{formatTime(duration)}</span>
                </div>
              </div>
            )}

            {/* Player Controls */}
            <div className="player-controls">
              <button
                className="play-pause-btn"
                onClick={handlePlayPause}
                disabled={!tone.url || tone.url === '#'}
              >
                {isPlaying ? '⏸️' : '▶️'}
              </button>

              <div className="progress-bar-container">
                <div
                  className="progress-bar-fill"
                  style={{ width: `${(currentTime / duration) * 100 || 0}%` }}
                />
              </div>

              <div className="volume-control">
                <span>🔊</span>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={volume}
                  onChange={(e) => {
                    setVolume(e.target.value);
                    if (audioRef.current) {
                      audioRef.current.volume = e.target.value;
                    }
                  }}
                  className="volume-slider"
                />
              </div>
            </div>
          </div>

          {/* Tone Information */}
          <div className="tone-info-section">
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Created:</span>
                <span className="info-value">
                  {new Date(tone.createdAt).toLocaleString()}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Duration:</span>
                <span className="info-value">{tone.duration}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Emotion:</span>
                <span className="info-value emotion-tag">{tone.emotion}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Category:</span>
                <span className="info-value">{tone.category}</span>
              </div>
            </div>
          </div>

          {/* Save Settings */}
          <div className="save-settings">
            <h3>Save This Tone</h3>

            <div className="form-group">
              <label htmlFor="tone-name">Name *</label>
              <input
                id="tone-name"
                type="text"
                value={toneName}
                onChange={(e) => setToneName(e.target.value)}
                placeholder="Enter a name for this tone..."
                className="tone-name-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="tone-notes">Notes (Optional)</label>
              <textarea
                id="tone-notes"
                value={toneNotes}
                onChange={(e) => setToneNotes(e.target.value)}
                placeholder="Add any notes about this tone..."
                rows="3"
                className="tone-notes-input"
              />
            </div>

            <div className="form-group">
              <label>Category</label>
              <div className="category-buttons">
                {['familiar', 'soothing', 'uplifting'].map(cat => (
                  <button
                    key={cat}
                    className={`category-btn ${selectedCategory === cat ? 'active' : ''}`}
                    onClick={() => setSelectedCategory(cat)}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Advanced Settings */}
          <div className="advanced-section">
            <button
              className="toggle-advanced"
              onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
            >
              <span>{showAdvancedSettings ? '▼' : '▶'}</span>
              Advanced Settings
            </button>

            {showAdvancedSettings && (
              <div className="advanced-settings">
                <div className="settings-grid">
                  <div className="setting-item">
                    <label>Frequency (Hz)</label>
                    <input
                      type="range"
                      min="100"
                      max="1000"
                      value={advancedSettings.frequency}
                      onChange={(e) => updateAdvancedSetting('frequency', e.target.value)}
                    />
                    <span className="setting-value">{advancedSettings.frequency} Hz</span>
                  </div>

                  <div className="setting-item">
                    <label>Wave Type</label>
                    <select
                      value={advancedSettings.waveType}
                      onChange={(e) => updateAdvancedSetting('waveType', e.target.value)}
                    >
                      <option value="sine">Sine</option>
                      <option value="square">Square</option>
                      <option value="sawtooth">Sawtooth</option>
                      <option value="triangle">Triangle</option>
                    </select>
                  </div>

                  <div className="setting-item">
                    <label>Reverb</label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={advancedSettings.reverb}
                      onChange={(e) => updateAdvancedSetting('reverb', e.target.value)}
                    />
                    <span className="setting-value">{Math.round(advancedSettings.reverb * 100)}%</span>
                  </div>

                  <div className="setting-item">
                    <label>Duration (seconds)</label>
                    <input
                      type="number"
                      min="30"
                      max="300"
                      value={advancedSettings.duration}
                      onChange={(e) => updateAdvancedSetting('duration', e.target.value)}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="tones-modal-footer">
          <button className="btn-secondary" onClick={handleClose}>
            Cancel
          </button>

          <button
            className="btn-regenerate"
            onClick={handleRegenerate}
            disabled={isGenerating}
          >
            {isGenerating ? (
              <>
                <span className="spinner"></span>
                Regenerating...
              </>
            ) : (
              <>
                <span>🔄</span>
                Regenerate
              </>
            )}
          </button>

          <button
            className="btn-primary"
            onClick={handleSave}
            disabled={!toneName.trim()}
          >
            <span>💾</span>
            Save Tone
          </button>
        </div>
      </div>
    </div>
  );
};

export default GeneratedTonesModal;