import React, { useState } from 'react';
import './GenerateMusicModal.css';

const GenerateMusicModal = ({
  isOpen,
  onClose,
  onGenerate,
  currentEmotion = 'calm',
  isGenerating = false
}) => {
  const [formData, setFormData] = useState({
    prompt: '',
    style: 'classical',
    tempo: 'moderate',
    instruments: [],
    duration: '120',
    emotion: currentEmotion,
    useMemory: false,
    memoryPrompt: ''
  });

  const [activeStep, setActiveStep] = useState(0);

  const styles = [
    { id: 'classical', label: 'Classical', icon: '🎻' },
    { id: 'jazz', label: 'Jazz', icon: '🎷' },
    { id: 'ambient', label: 'Ambient', icon: '🌊' },
    { id: 'folk', label: 'Folk', icon: '🎸' },
    { id: 'piano', label: 'Piano', icon: '🎹' },
    { id: 'orchestral', label: 'Orchestral', icon: '🎼' }
  ];

  const tempos = [
    { id: 'slow', label: 'Slow (60-80 BPM)', bpm: '60-80' },
    { id: 'moderate', label: 'Moderate (80-120 BPM)', bpm: '80-120' },
    { id: 'fast', label: 'Fast (120-160 BPM)', bpm: '120-160' }
  ];

  const instruments = [
    { id: 'piano', label: 'Piano' },
    { id: 'guitar', label: 'Guitar' },
    { id: 'violin', label: 'Violin' },
    { id: 'flute', label: 'Flute' },
    { id: 'cello', label: 'Cello' },
    { id: 'drums', label: 'Drums' },
    { id: 'synthesizer', label: 'Synthesizer' },
    { id: 'harp', label: 'Harp' }
  ];

  const promptSuggestions = [
    "A peaceful morning in the countryside",
    "Memories of childhood summers",
    "Walking through a garden in spring",
    "Gentle rain on a quiet evening",
    "Celebration with loved ones",
    "Ocean waves at sunset"
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleInstrumentToggle = (instrumentId) => {
    setFormData(prev => ({
      ...prev,
      instruments: prev.instruments.includes(instrumentId)
        ? prev.instruments.filter(id => id !== instrumentId)
        : [...prev.instruments, instrumentId]
    }));
  };

  const handleSubmit = () => {
    onGenerate(formData);
  };

  const isFormValid = () => {
    return formData.prompt.length > 0 || formData.memoryPrompt.length > 0;
  };

  const steps = ['Theme', 'Style', 'Customize'];

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="generate-music-modal" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <h2 className="modal-title">
            <span className="modal-icon">🎨</span>
            Generate AI Music
          </h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        {/* Progress Steps */}
        <div className="progress-steps">
          {steps.map((step, index) => (
            <div
              key={step}
              className={`step ${index === activeStep ? 'active' : ''} ${index < activeStep ? 'completed' : ''}`}
              onClick={() => setActiveStep(index)}
            >
              <div className="step-number">{index + 1}</div>
              <div className="step-label">{step}</div>
            </div>
          ))}
        </div>

        {/* Modal Content */}
        <div className="modal-content">
          {/* Step 0: Theme */}
          {activeStep === 0 && (
            <div className="step-content">
              <h3>What theme would you like for your music?</h3>

              <div className="form-group">
                <label htmlFor="prompt">Describe your music vision</label>
                <textarea
                  id="prompt"
                  value={formData.prompt}
                  onChange={(e) => handleInputChange('prompt', e.target.value)}
                  placeholder="E.g., A peaceful walk through autumn leaves..."
                  rows="4"
                  className="prompt-input"
                />
              </div>

              <div className="suggestions">
                <p className="suggestions-label">Need inspiration? Try these:</p>
                <div className="suggestion-chips">
                  {promptSuggestions.map(suggestion => (
                    <button
                      key={suggestion}
                      className="suggestion-chip"
                      onClick={() => handleInputChange('prompt', suggestion)}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>

              <div className="memory-option">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={formData.useMemory}
                    onChange={(e) => handleInputChange('useMemory', e.target.checked)}
                  />
                  <span>Create music based on a memory</span>
                </label>

                {formData.useMemory && (
                  <textarea
                    value={formData.memoryPrompt}
                    onChange={(e) => handleInputChange('memoryPrompt', e.target.value)}
                    placeholder="Describe a cherished memory..."
                    rows="3"
                    className="memory-input"
                  />
                )}
              </div>
            </div>
          )}

          {/* Step 1: Style */}
          {activeStep === 1 && (
            <div className="step-content">
              <h3>Choose a musical style</h3>

              <div className="style-grid">
                {styles.map(style => (
                  <button
                    key={style.id}
                    className={`style-card ${formData.style === style.id ? 'selected' : ''}`}
                    onClick={() => handleInputChange('style', style.id)}
                  >
                    <span className="style-icon">{style.icon}</span>
                    <span className="style-label">{style.label}</span>
                  </button>
                ))}
              </div>

              <div className="form-group">
                <label>Select tempo</label>
                <div className="tempo-options">
                  {tempos.map(tempo => (
                    <label key={tempo.id} className="radio-label">
                      <input
                        type="radio"
                        name="tempo"
                        value={tempo.id}
                        checked={formData.tempo === tempo.id}
                        onChange={(e) => handleInputChange('tempo', e.target.value)}
                      />
                      <span className="radio-text">
                        {tempo.label}
                        <small>{tempo.bpm}</small>
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Customize */}
          {activeStep === 2 && (
            <div className="step-content">
              <h3>Customize your music</h3>

              <div className="form-group">
                <label>Select instruments (optional)</label>
                <div className="instruments-grid">
                  {instruments.map(instrument => (
                    <button
                      key={instrument.id}
                      className={`instrument-chip ${formData.instruments.includes(instrument.id) ? 'selected' : ''}`}
                      onClick={() => handleInstrumentToggle(instrument.id)}
                    >
                      {instrument.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="duration">Duration (seconds)</label>
                <div className="duration-control">
                  <input
                    type="range"
                    id="duration"
                    min="30"
                    max="300"
                    step="30"
                    value={formData.duration}
                    onChange={(e) => handleInputChange('duration', e.target.value)}
                  />
                  <span className="duration-value">{formData.duration}s</span>
                </div>
              </div>

              <div className="generation-summary">
                <h4>Generation Summary</h4>
                <div className="summary-items">
                  <div className="summary-item">
                    <span className="summary-label">Theme:</span>
                    <span className="summary-value">
                      {formData.prompt || formData.memoryPrompt || 'Not specified'}
                    </span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Style:</span>
                    <span className="summary-value">{formData.style}</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Tempo:</span>
                    <span className="summary-value">{formData.tempo}</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Duration:</span>
                    <span className="summary-value">{formData.duration}s</span>
                  </div>
                  {formData.instruments.length > 0 && (
                    <div className="summary-item">
                      <span className="summary-label">Instruments:</span>
                      <span className="summary-value">
                        {formData.instruments.join(', ')}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <button
            className="btn-secondary"
            onClick={() => setActiveStep(Math.max(0, activeStep - 1))}
            disabled={activeStep === 0}
          >
            Previous
          </button>

          {activeStep < steps.length - 1 ? (
            <button
              className="btn-primary"
              onClick={() => setActiveStep(activeStep + 1)}
              disabled={activeStep === 0 && !isFormValid()}
            >
              Next
            </button>
          ) : (
            <button
              className="btn-primary generate-btn"
              onClick={handleSubmit}
              disabled={!isFormValid() || isGenerating}
            >
              {isGenerating ? (
                <>
                  <span className="spinner"></span>
                  Generating...
                </>
              ) : (
                <>
                  <span>🎵</span>
                  Generate Music
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default GenerateMusicModal;