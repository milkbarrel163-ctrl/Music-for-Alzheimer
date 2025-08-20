import React, { useState, useEffect } from 'react';
import './MusicLibraryModal.css';

const MusicLibraryModal = ({
  onClose,
  onSelectTrack,
  onAddToPlaylist,
  currentTrack,
  musicLibrary = {}
}) => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTracks, setSelectedTracks] = useState([]);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [sortBy, setSortBy] = useState('name'); // 'name', 'duration', 'date'
  const [filterEmotion, setFilterEmotion] = useState('all');

  // Check if we have actual music from backend or use sample data
  const hasActualMusic = Object.keys(musicLibrary).some(key =>
    Array.isArray(musicLibrary[key]) && musicLibrary[key].length > 0
  );

  // Sample music library structure if no actual music is loaded
  const defaultLibrary = {
    familiar: [
      { id: 'f1', title: 'Memory Lane', artist: 'Various', duration: '3:45', emotion: 'nostalgic' },
      { id: 'f2', title: 'Golden Days', artist: 'Classical', duration: '4:20', emotion: 'happy' },
      { id: 'f3', title: 'Home Sweet Home', artist: 'Folk', duration: '3:15', emotion: 'calm' }
    ],
    soothing: [
      { id: 's1', title: 'Peaceful Waters', artist: 'Ambient', duration: '5:00', emotion: 'calm' },
      { id: 's2', title: 'Gentle Breeze', artist: 'Nature', duration: '4:30', emotion: 'calm' },
      { id: 's3', title: 'Soft Rain', artist: 'Ambient', duration: '6:00', emotion: 'calm' }
    ],
    uplifting: [
      { id: 'u1', title: 'Morning Joy', artist: 'Orchestra', duration: '3:30', emotion: 'happy' },
      { id: 'u2', title: 'Sunshine Dance', artist: 'Various', duration: '2:45', emotion: 'energetic' },
      { id: 'u3', title: 'Victory March', artist: 'Classical', duration: '4:00', emotion: 'energetic' }
    ]
  };

  // Use actual music if available, otherwise use sample data
  const library = hasActualMusic ? musicLibrary : defaultLibrary;

  // Get all tracks based on selected category
  const getAllTracks = () => {
    if (selectedCategory === 'all') {
      return Object.values(library).flat();
    }
    return library[selectedCategory] || [];
  };

  // Filter tracks based on search and emotion
  const getFilteredTracks = () => {
    let tracks = getAllTracks();

    // Search filter
    if (searchQuery) {
      tracks = tracks.filter(track =>
        track.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        track.artist.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Emotion filter
    if (filterEmotion !== 'all') {
      tracks = tracks.filter(track => track.emotion === filterEmotion);
    }

    // Sort
    tracks.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.title.localeCompare(b.title);
        case 'duration':
          return a.duration.localeCompare(b.duration);
        case 'date':
          return (b.date || '').localeCompare(a.date || '');
        default:
          return 0;
      }
    });

    return tracks;
  };

  const handleTrackSelect = (track) => {
    if (selectedTracks.find(t => t.id === track.id)) {
      setSelectedTracks(selectedTracks.filter(t => t.id !== track.id));
    } else {
      setSelectedTracks([...selectedTracks, track]);
    }
  };

  const handlePlayTrack = (track) => {
    console.log('MusicLibraryModal - Playing track:', track);  // Debug log
    onSelectTrack(track);
    // Don't close modal immediately - let user select more if needed
  };

  const handleAddSelected = () => {
    if (selectedTracks.length > 0) {
      onAddToPlaylist(selectedTracks);
      setSelectedTracks([]);
    }
  };

  const handleSelectAll = () => {
    const tracks = getFilteredTracks();
    setSelectedTracks(tracks);
  };

  const handleClearSelection = () => {
    setSelectedTracks([]);
  };

  // Updated categories to only show categories that have music
  const categories = [
    { id: 'all', label: 'All Music', icon: '🎵' },
    ...(library.familiar && library.familiar.length > 0 ?
      [{ id: 'familiar', label: 'Familiar', icon: '🏠' }] : []),
    ...(library.soothing && library.soothing.length > 0 ?
      [{ id: 'soothing', label: 'Soothing', icon: '🌊' }] : []),
    ...(library.uplifting && library.uplifting.length > 0 ?
      [{ id: 'uplifting', label: 'Uplifting', icon: '🌟' }] : []),
    ...(library.generated && library.generated.length > 0 ?
      [{ id: 'generated', label: 'AI Generated', icon: '🤖' }] : [])
  ];

  const emotions = [
    { id: 'all', label: 'All Moods' },
    { id: 'calm', label: 'Calm' },
    { id: 'happy', label: 'Happy' },
    { id: 'nostalgic', label: 'Nostalgic' },
    { id: 'energetic', label: 'Energetic' }
  ];

  // Debug: Log what we're getting - Must be before any conditional returns
  useEffect(() => {
    console.log('MusicLibraryModal - musicLibrary:', musicLibrary);
    console.log('MusicLibraryModal - hasActualMusic:', hasActualMusic);
    console.log('MusicLibraryModal - library being used:', library);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [musicLibrary]);

  const filteredTracks = getFilteredTracks();

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="music-library-modal" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="library-header">
          <h2 className="library-title">
            <span>📚</span>
            Music Library
            {!hasActualMusic && <small style={{fontSize: '0.7em', marginLeft: '10px'}}>(Sample Data)</small>}
          </h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        {/* Library Controls */}
        <div className="library-controls">
          <div className="search-bar">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              placeholder="Search tracks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="control-buttons">
            <select
              value={filterEmotion}
              onChange={(e) => setFilterEmotion(e.target.value)}
              className="filter-select"
            >
              {emotions.map(emotion => (
                <option key={emotion.id} value={emotion.id}>
                  {emotion.label}
                </option>
              ))}
            </select>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="sort-select"
            >
              <option value="name">Sort by Name</option>
              <option value="duration">Sort by Duration</option>
              <option value="date">Sort by Date</option>
            </select>

            <div className="view-toggle">
              <button
                className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
                onClick={() => setViewMode('grid')}
                title="Grid View"
              >
                ⚏
              </button>
              <button
                className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
                onClick={() => setViewMode('list')}
                title="List View"
              >
                ☰
              </button>
            </div>
          </div>
        </div>

        {/* Category Tabs */}
        <div className="category-tabs">
          {categories.map(category => (
            <button
              key={category.id}
              className={`category-tab ${selectedCategory === category.id ? 'active' : ''}`}
              onClick={() => setSelectedCategory(category.id)}
            >
              <span className="tab-icon">{category.icon}</span>
              <span className="tab-label">{category.label}</span>
              {category.id !== 'all' && library[category.id] && (
                <span className="tab-count">{library[category.id].length}</span>
              )}
            </button>
          ))}
        </div>

        {/* Library Content */}
        <div className="library-content">
          {/* Selection Actions */}
          {selectedTracks.length > 0 && (
            <div className="selection-actions">
              <span className="selection-count">
                {selectedTracks.length} track{selectedTracks.length !== 1 ? 's' : ''} selected
              </span>
              <div className="selection-buttons">
                <button onClick={handleClearSelection} className="btn-clear">
                  Clear
                </button>
                <button onClick={handleAddSelected} className="btn-add">
                  Add to Playlist
                </button>
              </div>
            </div>
          )}

          {/* Tracks Display */}
          {filteredTracks.length === 0 ? (
            <div className="empty-library">
              <span className="empty-icon">🎵</span>
              <p>No tracks found</p>
              <small>
                {!hasActualMusic ?
                  'Please add MP3 files to backend/assets/music/ folders' :
                  'Try adjusting your search or filters'}
              </small>
            </div>
          ) : (
            <div className={`tracks-container ${viewMode}`}>
              {viewMode === 'grid' ? (
                <div className="tracks-grid">
                  {filteredTracks.map(track => (
                    <div
                      key={track.id}
                      className={`track-card ${selectedTracks.find(t => t.id === track.id) ? 'selected' : ''} ${currentTrack?.id === track.id ? 'playing' : ''}`}
                    >
                      <div className="track-card-header">
                        <input
                          type="checkbox"
                          checked={!!selectedTracks.find(t => t.id === track.id)}
                          onChange={() => handleTrackSelect(track)}
                          className="track-checkbox"
                        />
                        <button
                          className="play-btn-card"
                          onClick={() => handlePlayTrack(track)}
                        >
                          {currentTrack?.id === track.id ? '⏸️' : '▶️'}
                        </button>
                      </div>
                      <div className="track-card-body">
                        <h4 className="track-card-title">{track.title}</h4>
                        <p className="track-card-artist">{track.artist}</p>
                        <div className="track-card-meta">
                          <span className="track-duration">{track.duration}</span>
                          <span className="track-emotion">{track.emotion}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="tracks-list">
                  <div className="list-header">
                    <input
                      type="checkbox"
                      checked={selectedTracks.length === filteredTracks.length && filteredTracks.length > 0}
                      onChange={() => selectedTracks.length === filteredTracks.length ? handleClearSelection() : handleSelectAll()}
                      className="select-all-checkbox"
                    />
                    <span>Title</span>
                    <span>Artist</span>
                    <span>Duration</span>
                    <span>Mood</span>
                    <span>Actions</span>
                  </div>
                  {filteredTracks.map(track => (
                    <div
                      key={track.id}
                      className={`list-item ${selectedTracks.find(t => t.id === track.id) ? 'selected' : ''} ${currentTrack?.id === track.id ? 'playing' : ''}`}
                    >
                      <input
                        type="checkbox"
                        checked={!!selectedTracks.find(t => t.id === track.id)}
                        onChange={() => handleTrackSelect(track)}
                        className="track-checkbox"
                      />
                      <span className="list-title">{track.title}</span>
                      <span className="list-artist">{track.artist}</span>
                      <span className="list-duration">{track.duration}</span>
                      <span className="list-emotion">
                        <span className="emotion-badge">{track.emotion}</span>
                      </span>
                      <div className="list-actions">
                        <button
                          className="action-btn-list"
                          onClick={() => handlePlayTrack(track)}
                        >
                          {currentTrack?.id === track.id ? '⏸️' : '▶️'}
                        </button>
                        <button
                          className="action-btn-list"
                          onClick={() => onAddToPlaylist([track])}
                        >
                          ➕
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="library-footer">
          <div className="footer-stats">
            <span>{filteredTracks.length} tracks available</span>
            {!hasActualMusic && (
              <span style={{color: 'orange', marginLeft: '10px'}}>
                ⚠️ Using sample data - Add MP3 files to see real music
              </span>
            )}
          </div>
          <button className="btn-close-modal" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default MusicLibraryModal;