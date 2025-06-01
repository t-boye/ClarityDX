// frontend/src/utils/apiConfig.js (or .jsx)

const BASE_API_URL = import.meta.env.VITE_API_BASE_URL;

if (!BASE_API_URL) {
  console.warn("VITE_API_BASE_URL is not defined. API calls might fail.");
}

export { BASE_API_URL };
