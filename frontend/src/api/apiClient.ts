/**
 * Axios-based API client with token injection.
 */

import axios from 'axios';

const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

const normalizeApiBaseUrl = (rawBaseUrl?: string): string => {
  const fallback = DEFAULT_API_BASE_URL;
  const value = (rawBaseUrl || fallback).trim().replace(/\/+$/, '');
  return value.endsWith('/api/v1') ? value : `${value}/api/v1`;
};

const apiClient = axios.create({
  baseURL: normalizeApiBaseUrl(import.meta.env.VITE_API_BASE_URL),
  headers: { 'Content-Type': 'application/json' },
});

// ── Request interceptor: attach Bearer token ─────────────────────────────
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Response interceptor: handle errors ──────────────────────────────────
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
    }
    return Promise.reject(error);
  },
);

export default apiClient;
