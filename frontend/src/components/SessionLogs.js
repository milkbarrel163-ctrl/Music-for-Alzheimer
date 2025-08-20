import React, { useState } from 'react';
import './SessionLogs.css';

const SessionLogs = ({
  sessions = [],
  currentSession = null,
  onExportSession,
  onDeleteSession,
  onViewDetails
}) => {
  const [selectedSessions, setSelectedSessions] = useState([]);
  const [filterType, setFilterType] = useState('all'); // 'all', 'today', 'week', 'month'
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedSession, setExpandedSession] = useState(null);

  // Sample sessions data if not provided
  const sampleSessions = [
    {
      id: 's1',
      date: '2024-01-16',
      startTime: '10:00 AM',
      endTime: '10:45 AM',
      duration: '45 min',
      patientMood: 'calm',
      engagement: 'high',
      tracksPlayed: 5,
      responses: 8,
      notes: 'Patient responded well to classical music',
      highlights: ['Strong memory recall', 'Positive emotional response'],
      emotionLog: [
        { time: '10:05', emotion: 'calm' },
        { time: '10:20', emotion: 'happy' },
        { time: '10:35', emotion: 'nostalgic' }
      ]
    },
    {
      id: 's2',
      date: '2024-01-15',
      startTime: '2:00 PM',
      endTime: '2:30 PM',
      duration: '30 min',
      patientMood: 'happy',
      engagement: 'medium',
      tracksPlayed: 3,
      responses: 5,
      notes: 'Good session, patient enjoyed uplifting music',
      highlights: ['Smiled frequently', 'Tapped along to rhythm']
    }
  ];

  const displaySessions = sessions.length > 0 ? sessions : sampleSessions;

  // Filter sessions based on date
  const getFilteredSessions = () => {
    let filtered = [...displaySessions];

    // Date filter
    const today = new Date();
    switch (filterType) {
      case 'today':
        filtered = filtered.filter(s => {
          const sessionDate = new Date(s.date);
          return sessionDate.toDateString() === today.toDateString();
        });
        break;
      case 'week':
        const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
        filtered = filtered.filter(s => new Date(s.date) >= weekAgo);
        break;
      case 'month':
        const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
        filtered = filtered.filter(s => new Date(s.date) >= monthAgo);
        break;
      default:
        break;
    }

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(s =>
        s.notes?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.patientMood?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.date.includes(searchQuery)
      );
    }

    return filtered;
  };

  const handleSessionSelect = (sessionId) => {
    if (selectedSessions.includes(sessionId)) {
      setSelectedSessions(selectedSessions.filter(id => id !== sessionId));
    } else {
      setSelectedSessions([...selectedSessions, sessionId]);
    }
  };

  const handleSelectAll = () => {
    const filtered = getFilteredSessions();
    if (selectedSessions.length === filtered.length) {
      setSelectedSessions([]);
    } else {
      setSelectedSessions(filtered.map(s => s.id));
    }
  };

  const handleExportSelected = () => {
    if (selectedSessions.length > 0) {
      onExportSession(selectedSessions);
      setSelectedSessions([]);
    }
  };

  const handleDeleteSelected = () => {
    if (selectedSessions.length > 0 &&
        window.confirm(`Delete ${selectedSessions.length} session(s)?`)) {
      onDeleteSession(selectedSessions);
      setSelectedSessions([]);
    }
  };

  const toggleSessionExpand = (sessionId) => {
    setExpandedSession(expandedSession === sessionId ? null : sessionId);
  };

  const getEngagementColor = (engagement) => {
    switch (engagement) {
      case 'high': return 'var(--success-color)';
      case 'medium': return 'var(--warning-color)';
      case 'low': return 'var(--error-color)';
      default: return 'var(--text-secondary)';
    }
  };

  const filteredSessions = getFilteredSessions();

  // Calculate statistics
  const stats = {
    totalSessions: filteredSessions.length,
    avgDuration: filteredSessions.reduce((acc, s) => {
      const duration = parseInt(s.duration) || 0;
      return acc + duration;
    }, 0) / (filteredSessions.length || 1),
    totalTracks: filteredSessions.reduce((acc, s) => acc + (s.tracksPlayed || 0), 0),
    avgEngagement: filteredSessions.filter(s => s.engagement === 'high').length / (filteredSessions.length || 1) * 100
  };

  return (
    <div className="session-logs">
      {/* Header */}
      <div className="logs-header">
        <h2 className="logs-title">
          <span>📊</span>
          Session History
        </h2>

        {/* Quick Stats */}
        <div className="quick-stats-bar">
          <div className="stat-item-mini">
            <span className="stat-label-mini">Sessions</span>
            <span className="stat-value-mini">{stats.totalSessions}</span>
          </div>
          <div className="stat-item-mini">
            <span className="stat-label-mini">Avg Duration</span>
            <span className="stat-value-mini">{Math.round(stats.avgDuration)} min</span>
          </div>
          <div className="stat-item-mini">
            <span className="stat-label-mini">Total Tracks</span>
            <span className="stat-value-mini">{stats.totalTracks}</span>
          </div>
          <div className="stat-item-mini">
            <span className="stat-label-mini">High Engagement</span>
            <span className="stat-value-mini">{Math.round(stats.avgEngagement)}%</span>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="logs-controls">
        <div className="logs-search">
          <input
            type="text"
            placeholder="Search sessions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="logs-search-input"
          />
        </div>

        <div className="logs-filters">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="filter-dropdown"
          >
            <option value="all">All Sessions</option>
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
          </select>

          {selectedSessions.length > 0 && (
            <div className="bulk-actions">
              <span className="selected-count">
                {selectedSessions.length} selected
              </span>
              <button onClick={handleExportSelected} className="btn-export">
                Export
              </button>
              <button onClick={handleDeleteSelected} className="btn-delete">
                Delete
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Current Session Alert */}
      {currentSession && (
        <div className="current-session-alert">
          <span className="alert-icon">🔴</span>
          <span>Session in progress - Started {currentSession.startTime}</span>
        </div>
      )}

      {/* Sessions List */}
      <div className="sessions-list">
        {filteredSessions.length === 0 ? (
          <div className="no-sessions">
            <span className="no-sessions-icon">📁</span>
            <p>No sessions found</p>
            <small>Sessions will appear here after therapy sessions</small>
          </div>
        ) : (
          <>
            {/* Select All */}
            <div className="list-header-row">
              <input
                type="checkbox"
                checked={selectedSessions.length === filteredSessions.length && filteredSessions.length > 0}
                onChange={handleSelectAll}
                className="select-all"
              />
              <span>Date</span>
              <span>Time</span>
              <span>Duration</span>
              <span>Mood</span>
              <span>Engagement</span>
              <span>Actions</span>
            </div>

            {/* Session Items */}
            {filteredSessions.map(session => (
              <div key={session.id} className="session-item-container">
                <div className={`session-item ${expandedSession === session.id ? 'expanded' : ''}`}>
                  <input
                    type="checkbox"
                    checked={selectedSessions.includes(session.id)}
                    onChange={() => handleSessionSelect(session.id)}
                    className="session-checkbox"
                  />

                  <span className="session-date">{session.date}</span>
                  <span className="session-time">{session.startTime}</span>
                  <span className="session-duration">{session.duration}</span>

                  <span className="session-mood">
                    <span className={`mood-badge mood-${session.patientMood}`}>
                      {session.patientMood}
                    </span>
                  </span>

                  <span className="session-engagement">
                    <span
                      className="engagement-indicator"
                      style={{ color: getEngagementColor(session.engagement) }}
                    >
                      {session.engagement}
                    </span>
                  </span>

                  <div className="session-actions">
                    <button
                      onClick={() => toggleSessionExpand(session.id)}
                      className="btn-expand"
                      title={expandedSession === session.id ? 'Collapse' : 'Expand'}
                    >
                      {expandedSession === session.id ? '▼' : '▶'}
                    </button>
                    <button
                      onClick={() => onViewDetails(session)}
                      className="btn-view"
                      title="View Details"
                    >
                      👁️
                    </button>
                    <button
                      onClick={() => onExportSession([session.id])}
                      className="btn-export-single"
                      title="Export"
                    >
                      📥
                    </button>
                  </div>
                </div>

                {/* Expanded Details */}
                {expandedSession === session.id && (
                  <div className="session-details">
                    <div className="details-grid">
                      <div className="detail-section">
                        <h4>Session Overview</h4>
                        <p><strong>Tracks Played:</strong> {session.tracksPlayed}</p>
                        <p><strong>Responses:</strong> {session.responses}</p>
                        <p><strong>Notes:</strong> {session.notes}</p>
                      </div>

                      {session.highlights && session.highlights.length > 0 && (
                        <div className="detail-section">
                          <h4>Highlights</h4>
                          <ul className="highlights-list">
                            {session.highlights.map((highlight, index) => (
                              <li key={index}>{highlight}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {session.emotionLog && session.emotionLog.length > 0 && (
                        <div className="detail-section">
                          <h4>Emotion Timeline</h4>
                          <div className="emotion-timeline">
                            {session.emotionLog.map((log, index) => (
                              <div key={index} className="timeline-item">
                                <span className="timeline-time">{log.time}</span>
                                <span className={`timeline-emotion mood-${log.emotion}`}>
                                  {log.emotion}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
};

export default SessionLogs;