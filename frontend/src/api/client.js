import axios from 'axios';

// Get backend URL from environment or use relative for proxy
const baseURL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:7860';
const apiKey = import.meta.env.VITE_API_KEY || 'your-secret-key-here';

const client = axios.create({
  baseURL,
  headers: {
    'X-API-Key': apiKey,
    'Content-Type': 'application/json'
  }
});

export default client;
