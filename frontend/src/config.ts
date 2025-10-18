// Configuration for Mini SQL Playground Frontend

export const config = {
  // API Base URL - Change this to match your backend URL
  API_BASE_URL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
  
  // Default query to show in editor
  DEFAULT_QUERY: 'SELECT * FROM users;',
  
  // History settings
  MAX_HISTORY_ITEMS: 20,
  
  // Editor settings
  EDITOR_HEIGHT: '300px',
  EDITOR_THEME: 'vs-dark',
  EDITOR_LANGUAGE: 'sql'
};

export default config;
