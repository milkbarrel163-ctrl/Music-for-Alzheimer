import React, { useState, useEffect } from 'react';
import './SuggestionPanel.css';

const SuggestionPanel = ({
  currentEmotion,
  sessionData,
  onSuggestionAccept,
  onSuggestionDismiss,
  isVisible = true
}) => {
  const [suggestions, setSuggestions] = useState([]);
  const [dismissedSuggestions, setDismissedSuggestions] = useState([]);
  const [expandedSuggestion, setExpandedSuggestion] = useState(null);
  const [filterCategory, setFilterCategory] = useState('all');

  // Generate suggestions based on current context
  useEffect(() => {
    generateSuggestions();
  }, [currentEmotion, sessionData]);

  const generateSuggestions = () => {
    const newSuggestions = [];

    // Emotion-based suggestions
    if (currentEmotion === 'calm') {
      newSuggestions.push({
        id: 'sug1',
        type: 'music',
        priority: 'high',
        title: 'Try Peaceful Piano',
        description: 'Based on the calm mood, gentle piano music might enhance relaxation.',
        action: 'Play peaceful piano playlist',
        category: 'music',
        icon: '🎹'
      });
    } else if (currentEmotion === 'happy') {
      newSuggestions.push({
        id: 'sug2',
        type: 'activity',
        priority: 'medium',
        title: 'Encourage Movement',
        description: 'The positive mood is perfect for light movement or dancing.',
        action: 'Start movement activity',
        category: 'activity',
        icon: '💃'
      });
    } else if (currentEmotion === 'nostalgic') {
      newSuggestions.push({
        id: 'sug3',
        type: 'memory',
        priority: 'high',
        title: 'Memory Sharing Time',
        description: 'This nostalgic mood is ideal for sharing memories. Consider asking about favorite childhood songs.',
        action: 'Start memory prompts',
        category: 'memory',
        icon: '📸'
      });
    }

    // Session-based suggestions
    if (sessionData?.responses?.length > 3) {
      newSuggestions.push({
        id: 'sug4',
        type: 'break',
        priority: 'low',
        title: 'Consider a Short Break',
        description: 'The patient has been engaged for a while. A brief pause might be beneficial.',
        action: 'Take 5-minute break',
        category: 'wellness',
        icon: '☕'
      });
    }

    // Time-based suggestions
    const hour = new Date().getHours();
    if (hour < 12) {
      newSuggestions.push({
        id: 'sug5',
        type: 'music',
        priority: 'medium',
        title: 'Morning Energy Boost',
        description: 'Start the day with uplifting music to energize the patient.',
        action: 'Play morning playlist',
        category: 'music',
        icon: '🌅'
      });
    } else if (hour > 16) {
      newSuggestions.push({
        id: 'sug6',
        type: 'music',
        priority: 'medium',
        title: 'Evening Wind Down',
        description: 'Transition to calming music as the day ends.',
        action: 'Play evening playlist',
        category: 'music',
        icon: '🌆'
      });
    }

    // AI-generated insights
    newSuggestions.push({
      id: 'sug7',
      type: 'insight',
      priority: 'low',
      title: 'Pattern Detected',
      description: 'The patient responds well to classical music during morning sessions.',
      action: 'View insights',
      category: 'insight',
      icon: '💡',
      details: {
        pattern: 'Musical preference',
        confidence: '85%',
        basedOn: '15 sessions'
      }
    });

    // Filter out dismissed suggestions
    const activeSuggestions = newSuggestions.filter(
      sug => !dismissedSuggestions.includes(sug.id)
    );

    setSuggestions(activeSuggestions);
  };

  const handleAccept = (suggestion) => {
    onSuggestionAccept(suggestion);
    setDismissedSuggestions([...dismissedSuggestions, suggestion.id]);
  };

  const handleDismiss = (suggestionId) => {
    setDismissedSuggestions([...dismissedSuggestions, suggestionId]);
    if (onSuggestionDismiss) {
      onSuggestionDismiss(suggestionId);
    }
  };

  const toggleExpand = (suggestionId) => {
    setExpandedSuggestion(expandedSuggestion === suggestionId ? null : suggestionId);
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'var(--error-color)';
      case 'medium': return 'var(--warning-color)';
      case 'low': return 'var(--success-color)';
      default: return 'var(--text-secondary)';
    }
  };

  const getFilteredSuggestions = () => {
    if (filterCategory === 'all') {
      return suggestions;
    }
    return suggestions.filter(sug => sug.category === filterCategory);
  };

  const categories = [
    { id: 'all', label: 'All', icon: '📋' },
    { id: 'music', label: 'Music', icon: '🎵' },
    { id: 'activity', label: 'Activity', icon: '🎯' },
    { id: 'memory', label: 'Memory', icon: '💭' },
    { id: 'wellness', label: 'Wellness', icon: '❤️' },
    { id: 'insight', label: 'Insights', icon: '💡' }
  ];

  if (!isVisible) return null;

  const filteredSuggestions = getFilteredSuggestions();

  return (
    <div className="suggestion-panel">
      {/* Panel Header */}
      <div className="panel-header">
        <h3 className="panel-title">
          <span className="panel-icon">🤖</span>
          AI Suggestions
        </h3>
        <span className="suggestion-count">{filteredSuggestions.length}</span>
      </div>

      {/* Category Filter */}
      <div className="category-filter">
        {categories.map(cat => (
          <button
            key={cat.id}
            className={`filter-btn ${filterCategory === cat.id ? 'active' : ''}`}
            onClick={() => setFilterCategory(cat.id)}
            title={cat.label}
          >
            <span className="filter-icon">{cat.icon}</span>
            <span className="filter-label">{cat.label}</span>
          </button>
        ))}
      </div>

      {/* Suggestions List */}
      <div className="suggestions-list">
        {filteredSuggestions.length === 0 ? (
          <div className="no-suggestions">
            <span className="no-suggestions-icon">🎯</span>
            <p>No suggestions available</p>
            <small>AI suggestions will appear here based on session activity</small>
          </div>
        ) : (
          filteredSuggestions.map(suggestion => (
            <div
              key={suggestion.id}
              className={`suggestion-card ${expandedSuggestion === suggestion.id ? 'expanded' : ''}`}
            >
              <div className="suggestion-header">
                <div className="suggestion-icon-wrapper">
                  {suggestion.icon}
                </div>

                <div className="suggestion-content">
                  <div className="suggestion-title-row">
                    <h4 className="suggestion-title">{suggestion.title}</h4>
                    <span
                      className="priority-indicator"
                      style={{ backgroundColor: getPriorityColor(suggestion.priority) }}
                      title={`${suggestion.priority} priority`}
                    />
                  </div>

                  <p className="suggestion-description">{suggestion.description}</p>

                  {expandedSuggestion === suggestion.id && suggestion.details && (
                    <div className="suggestion-details">
                      {Object.entries(suggestion.details).map(([key, value]) => (
                        <div key={key} className="detail-item">
                          <span className="detail-label">{key}:</span>
                          <span className="detail-value">{value}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <button
                  className="expand-btn"
                  onClick={() => toggleExpand(suggestion.id)}
                  title={expandedSuggestion === suggestion.id ? 'Collapse' : 'Expand'}
                >
                  {expandedSuggestion === suggestion.id ? '−' : '+'}
                </button>
              </div>

              <div className="suggestion-actions">
                <button
                  className="accept-btn"
                  onClick={() => handleAccept(suggestion)}
                >
                  <span>✓</span>
                  {suggestion.action}
                </button>

                <button
                  className="dismiss-btn"
                  onClick={() => handleDismiss(suggestion.id)}
                  title="Dismiss suggestion"
                >
                  ×
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <button className="quick-action-btn">
          <span>🔄</span>
          Refresh
        </button>
        <button className="quick-action-btn">
          <span>⚙️</span>
          Settings
        </button>
        <button
          className="quick-action-btn"
          onClick={() => setDismissedSuggestions([])}
        >
          <span>♻️</span>
          Reset
        </button>
      </div>
    </div>
  );
};

export default SuggestionPanel;