/**
 * API Client Service for AI-Based Disease Prediction System
 * Supports secure HttpOnly cookie session authentication,
 * CSRF token injection, role-based requests, and ML inference.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

let memoryCsrfToken = '';

export function setCsrfToken(token) {
  if (token) memoryCsrfToken = token;
}

export function getCsrfToken() {
  if (memoryCsrfToken) return memoryCsrfToken;
  // Fallback to cookie if present
  const match = document.cookie.match(/(?:^|;\s*)healthai_csrf=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : '';
}

/**
 * Common fetch helper ensuring credentials (cookies) and CSRF tokens are attached.
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = { ...(options.headers || {}) };

  const method = (options.method || 'GET').toUpperCase();
  if (['POST', 'PUT', 'DELETE'].includes(method)) {
    const csrf = getCsrfToken();
    if (csrf) {
      headers['X-CSRF-Token'] = csrf;
    }
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include', // Ensures HttpOnly cookies are attached
  });

  return response;
}

// ============================================================================
// Public Diagnostics & Symptoms Catalog
// ============================================================================

export async function checkHealth() {
  const response = await request('/health');
  if (!response.ok) throw new Error('Health check failed');
  return response.json();
}

export async function fetchSymptoms() {
  const response = await request('/symptoms');
  if (!response.ok) throw new Error('Failed to fetch symptoms catalog');
  const json = await response.json();
  if (!json.success) throw new Error(json.error || 'Failed to fetch symptoms');
  return json.data;
}

export async function fetchModelMetrics() {
  const response = await request('/metrics');
  if (!response.ok) throw new Error('Failed to fetch model evaluation metrics');
  const json = await response.json();
  if (!json.success) throw new Error(json.error || 'Failed to fetch metrics');
  return json.data;
}

export async function fetchDashboardStats() {
  const response = await request('/dashboard/stats');
  if (!response.ok) throw new Error('Failed to fetch dashboard stats');
  const json = await response.json();
  if (!json.success) throw new Error(json.error || 'Failed to fetch stats');
  return json.data;
}

// ============================================================================
// Authentication APIs
// ============================================================================

export async function apiRegister(fullName, email, password) {
  const response = await request('/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ full_name: fullName, email, password }),
  });
  const json = await response.json();
  if (!response.ok || !json.success) {
    throw new Error(json.error || 'Registration failed');
  }
  if (json.csrf_token) setCsrfToken(json.csrf_token);
  return json;
}

export async function apiLogin(email, password) {
  const response = await request('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  const json = await response.json();
  if (!response.ok || !json.success) {
    throw new Error(json.error || 'Login failed');
  }
  if (json.csrf_token) setCsrfToken(json.csrf_token);
  return json;
}

export async function apiLogout() {
  const response = await request('/auth/logout', {
    method: 'POST',
  });
  memoryCsrfToken = '';
  if (!response.ok) {
    throw new Error('Logout failed');
  }
  return response.json();
}

export async function apiGetCurrentUser() {
  const response = await request('/auth/me');
  if (!response.ok) {
    return { authenticated: false, user: null };
  }
  const json = await response.json();
  if (json.csrf_token) setCsrfToken(json.csrf_token);
  return json;
}

export async function apiUpdateProfile(payload) {
  const response = await request('/auth/profile', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const json = await response.json();
  if (!response.ok || !json.success) {
    throw new Error(json.error || 'Failed to update profile');
  }
  return json;
}

export async function apiDeleteAccount(password) {
  const response = await request('/auth/account', {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  });
  const json = await response.json();
  if (!response.ok || !json.success) {
    throw new Error(json.error || 'Failed to delete account');
  }
  memoryCsrfToken = '';
  return json;
}

export async function apiForgotPassword(email) {
  const response = await request('/auth/forgot-password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });
  const json = await response.json();
  if (!response.ok || !json.success) {
    throw new Error(json.error || 'Request failed');
  }
  return json;
}

export async function apiResetPassword(token, newPassword) {
  const response = await request('/auth/reset-password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, new_password: newPassword }),
  });
  const json = await response.json();
  if (!response.ok || !json.success) {
    throw new Error(json.error || 'Password reset failed');
  }
  return json;
}

// ============================================================================
// Protected Clinical Prediction & History
// ============================================================================

export async function predictDisease(symptoms) {
  const response = await request('/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symptoms }),
  });
  const json = await response.json();
  if (!response.ok || !json.success) {
    if (response.status === 401) {
      throw new Error('AUTH_REQUIRED');
    }
    throw new Error(json.error || 'Failed to complete prediction analysis');
  }
  return json.data;
}

export async function fetchAssessmentHistory(limit = 25, viewAll = false) {
  const query = viewAll ? `limit=${limit}&view=all` : `limit=${limit}`;
  const response = await request(`/history?${query}`);
  if (!response.ok) {
    if (response.status === 401) return [];
    throw new Error('Failed to fetch assessment history');
  }
  const json = await response.json();
  if (!json.success) throw new Error(json.error || 'Failed to fetch history');
  return json.data;
}

export async function clearAssessmentHistory(scope = 'personal') {
  const response = await request(`/history/clear?scope=${scope}`, {
    method: 'POST',
  });
  const json = await response.json();
  if (!response.ok || !json.success) {
    throw new Error(json.error || 'Failed to clear assessment history');
  }
  return json;
}

// ============================================================================
// Administrator User Management
// ============================================================================

export async function apiFetchAdminUsers() {
  const response = await request('/admin/users');
  const json = await response.json();
  if (!response.ok || !json.success) {
    throw new Error(json.error || 'Failed to fetch users');
  }
  return json.data;
}

export async function apiDeleteAdminUser(userId) {
  const response = await request(`/admin/users/${userId}`, {
    method: 'DELETE',
  });
  const json = await response.json();
  if (!response.ok || !json.success) {
    throw new Error(json.error || 'Failed to delete user');
  }
  return json;
}

export async function apiUpdateAdminUserStatus(userId, payload) {
  const response = await request(`/admin/users/${userId}/status`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const json = await response.json();
  if (!response.ok || !json.success) {
    throw new Error(json.error || 'Failed to update user status');
  }
  return json;
}
