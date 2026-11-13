/**
 * Application configuration
 * 
 * This file contains environment-specific configuration.
 */

// Determine API URL based on environment
export const getApiUrl = (): string => {
  // For local development
  if (import.meta.env.DEV) {
    return 'http://localhost:8001';
  }
  
  // For production (Vercel deployment)
  // Check environment variable first
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  return 'https://sentinelllm-backend.onrender.com';
};

export const config = {
  apiUrl: getApiUrl(),
  tokenKey: 'sentinelloop_auth_token',
};
