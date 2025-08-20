import React from 'react';

function MemoryResponseControls({ memoryResponse, onChange, disabled }) {
  const responses = [
    { value: 'None', label: 'No Response', icon: '😶', description: 'Just listening' },
    { value: 'Some', label: 'Recognition', icon: '🙂', description: 'Shows familiarity' },
    { value: 'Good', label: 'Active Recall', icon: '😊', description: 'Sharing memories' }
  ];

  return (
    <div className="memory-response-controls">
      <h3>Memory Response Level</h3>
      <div className="response-buttons">
        {responses.map(response => (
          <button
            key={response.value}
            className={`response-btn ${memoryResponse === response.value ? 'active' : ''}`}
            onClick={() => onChange(response.value)}
            disabled={disabled}
          >
            <span className="response-icon">{response.icon}</span>
            <span className="response-label">{response.label}</span>
            <span className="response-desc">{response.description}</span>
          </button>
        ))}
      </div>

      <div className="response-indicators">
        <p className="current-response">
          Current Response: <strong>{memoryResponse}</strong>
        </p>

        {memoryResponse === 'Good' && (
          <div className="response-tip">
            💡 Great! Consider recording these memories for future sessions.
          </div>
        )}

        {memoryResponse === 'Some' && (
          <div className="response-tip">
            💡 Try gentle prompts to encourage more recall.
          </div>
        )}

        {memoryResponse === 'None' && (
          <div className="response-tip">
            💡 Try different songs or just enjoy listening together.
          </div>
        )}
      </div>
    </div>
  );
}

export default MemoryResponseControls;