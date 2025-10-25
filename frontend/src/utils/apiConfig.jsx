// frontend/src/utils/apiConfig.js (or .jsx)

// API Configuration for ClarityDx
// Supports both local development and Netlify production deployment

const BASE_API_URL = import.meta.env.VITE_API_BASE_URL ||
                     (import.meta.env.MODE === 'production'
                       ? '/.netlify/functions'
                       : 'http://localhost:8888/.netlify/functions');

if (!BASE_API_URL) {
  console.warn("VITE_API_BASE_URL is not defined. Using default Netlify Functions URL.");
}

console.info(`API Base URL: ${BASE_API_URL}`);

export { BASE_API_URL };
