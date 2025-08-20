import React from 'react';

function EmotionSelector({ emotionalState, onChange, disabled }) {
  const emotions = [
    { value: 'Distressed', icon: '😟', color: '#e74c3c', description: 'Anxious or upset' },
    { value: 'Neutral', icon: '😐', color: '#95a5a6', description: 'Calm, no strong emotion' },
    { value: 'Content', icon: '😌', color: '#3498db', description: 'Peaceful and satisfied' },
    { value: 'Joyful', icon: '😊', color: '#2ecc71', description: 'Happy and engaged' }
  ];

  return (
    <div className="emotion-selector">
      <h3>Current Emotional State</h3>
      <div className="emotion-buttons">
        {emotions.map(emotion => (
          <button
            key={emotion.value}
            className={`emotion-btn ${emotionalState === emotion.value ? 'active' : ''}`}
            onClick={() => onChange(emotion.value)}
            disabled={disabled}
            style={{
              borderColor: emotionalState === emotion.value ? emotion.color : '#ddd',
              backgroundColor: emotionalState === emotion.value ? `${emotion.color}20` : 'white'
            }}
          >
            <span className="emotion-icon">{emotion.icon}</span>
            <span className="emotion-label">{emotion.value}</span>
            <span className="emotion-desc">{emotion.description}</span>
          </button>
        ))}
      </div>

      <div className="emotion-info">
        <p>Selected: <strong>{emotionalState}</strong></p>
        <p className="emotion-guidance">
          {emotionalState === 'Distressed' && '🎵 Playing soothing, familiar music'}
          {emotionalState === 'Neutral' && '🎵 Playing well-known classics'}
          {emotionalState === 'Content' && '🎵 Playing engaging favorites'}
          {emotionalState === 'Joyful' && '🎵 Playing uplifting, celebratory music'}
        </p>
      </div>
    </div>
  );
}

export default EmotionSelector;