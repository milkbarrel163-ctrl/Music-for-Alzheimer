import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Session Management
export const startSession = async (sessionData) => {
  const response = await api.post('/session/start', sessionData);
  return response.data;
};

export const logSession = async (logData) => {
  const response = await api.post('/session/log', logData);
  return response.data;
};

// Music Management
export const getMusicCategories = async () => {
  const response = await api.get('/music/categories');
  return response.data;
};

export const getMusicByCategory = async (category) => {
  const response = await api.get(`/music/${category}`);
  return response.data;
};

export const generateMusic = async (requestData) => {
  const response = await api.post('/music/generate', requestData);
  return response.data;
};

// GPT Suggestions
export const getGPTSuggestions = async (requestData) => {
  const response = await api.post('/gpt/suggestions', requestData);
  return response.data.suggestions;
};

// Analytics
export const getSessionAnalytics = async (days = 7) => {
  const response = await api.get(`/sessions/analytics?days=${days}`);
  return response.data;
};

export const getRecentSessions = async (limit = 10) => {
  const response = await api.get(`/sessions/recent?limit=${limit}`);
  return response.data.sessions;
};

export default api;