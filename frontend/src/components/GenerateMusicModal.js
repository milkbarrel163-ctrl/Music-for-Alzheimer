import React, { useState } from 'react';
import './GenerateMusicModal.css';
import { generateMusic } from '../api';

const GenerateMusicModal = ({ onClose, onGenerated }) => {
  const [selectedSong, setSelectedSong] = useState('');
  const [tempo, setTempo] = useState('slow');
  const [style, setStyle] = useState('simplified');
  const [isGenerating, setIsGenerating] = useState(false);

  // Popular songs that might work well simplified
  const availableSongs = [
    "Amazing Grace",
    "You Are My Sunshine",
    "Somewhere Over the Rainbow",
    "What a Wonderful World",
    "Edelweiss",
    "Moon River",
    "Que Sera Sera",
    "Fly Me to the Moon",
    "The Sound of Music",
    "My Way"
  ];

  const handleGenerate = async () => {
    if (!selectedSong) return;

    setIsGenerating(true);
    try {
      const response = await generateMusic({
        base_song: selectedSong,
        tempo: tempo,
        style: style
      });

      if (response.status === 'success') {
        onGenerated();
        onClose();
      }
    } catch (error) {
      console.error('Generation failed:', error);
      alert('Failed to generate music. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-simple" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🎨 Create Simplified Version</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <p className="modal-description">
            Create a simplified, therapeutic version of a familiar song
          </p>

          {/* Song Selection */}
          <div className="form-group">
            <label>Select a song to simplify:</label>
            <select
              value={selectedSong}
              onChange={(e) => setSelectedSong(e.target.value)}
              className="song-select"
            >
              <option value="">-- Choose a song --</option>
              {availableSongs.map(song => (
                <option key={song} value={song}>{song}</option>
              ))}
            </select>
          </div>

          {/* Tempo Selection */}
          <div className="form-group">
            <label>Tempo:</label>
            <div className="radio-group">
              <label className="radio-option">
                <input
                  type="radio"
                  value="slow"
                  checked={tempo === 'slow'}
                  onChange={(e) => setTempo(e.target.value)}
                />
                <span>Slow (Calming)</span>
              </label>
              <label className="radio-option">
                <input
                  type="radio"
                  value="medium"
                  checked={tempo === 'medium'}
                  onChange={(e) => setTempo(e.target.value)}
                />
                <span>Medium (Gentle)</span>
              </label>
            </div>
          </div>

          {/* Style Selection */}
          <div className="form-group">
            <label>Style:</label>
            <div className="radio-group">
              <label className="radio-option">
                <input
                  type="radio"
                  value="simplified"
                  checked={style === 'simplified'}
                  onChange={(e) => setStyle(e.target.value)}
                />
                <span>Simplified (Minimal instruments)</span>
              </label>
              <label className="radio-option">
                <input
                  type="radio"
                  value="instrumental"
                  checked={style === 'instrumental'}
                  onChange={(e) => setStyle(e.target.value)}
                />
                <span>Instrumental (No vocals)</span>
              </label>
            </div>
          </div>

          {/* Preview */}
          {selectedSong && (
            <div className="generation-preview">
              <h4>Preview:</h4>
              <p>
                Creating a <strong>{tempo}</strong>, <strong>{style}</strong> version of
                <br />
                "<strong>{selectedSong}</strong>"
              </p>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button
            className="btn-primary"
            onClick={handleGenerate}
            disabled={!selectedSong || isGenerating}
          >
            {isGenerating ? 'Generating...' : 'Generate'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default GenerateMusicModal;