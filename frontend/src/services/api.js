/**
 * API Client Service for AI-Based Disease Prediction System
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

export async function checkHealth() {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) throw new Error('Health check failed');
  return response.json();
}

export async function fetchSymptoms() {
  const response = await fetch(`${API_BASE}/symptoms`);
  if (!response.ok) throw new Error('Failed to fetch symptoms catalog');
  const json = await response.json();
  if (!json.success) throw new Error(json.error || 'Failed to fetch symptoms');
  return json.data;
}

export async function predictDisease(symptoms) {
  const response = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symptoms }),
  });
  const json = await response.json();
  if (!response.ok || !json.success) {
    throw new Error(json.error || 'Failed to complete prediction analysis');
  }
  return json.data;
}

export async function fetchModelMetrics() {
  const response = await fetch(`${API_BASE}/metrics`);
  if (!response.ok) throw new Error('Failed to fetch model evaluation metrics');
  const json = await response.json();
  if (!json.success) throw new Error(json.error || 'Failed to fetch metrics');
  return json.data;
}

export async function fetchDashboardStats() {
  const response = await fetch(`${API_BASE}/dashboard/stats`);
  if (!response.ok) throw new Error('Failed to fetch dashboard stats');
  const json = await response.json();
  if (!json.success) throw new Error(json.error || 'Failed to fetch stats');
  return json.data;
}

export async function fetchAssessmentHistory(limit = 25) {
  const response = await fetch(`${API_BASE}/history?limit=${limit}`);
  if (!response.ok) throw new Error('Failed to fetch assessment history');
  const json = await response.json();
  if (!json.success) throw new Error(json.error || 'Failed to fetch history');
  return json.data;
}

export async function clearAssessmentHistory() {
  const response = await fetch(`${API_BASE}/history/clear`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to clear assessment history');
  const json = await response.json();
  return json;
}
