import { API_ENDPOINTS } from './constants';

/**
 * Generic fetch wrapper
 */
export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: { "content-type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) throw new Error(`API ${path} failed: ${res.status}`);
  return (await res.json()) as T;
}

const getAuthHeaders = () => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

export const login = async (email: string, password: string) => {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  const res = await fetch(API_ENDPOINTS.LOGIN, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData,
  });
  return res.json();
};

export const startInspection = async (data: {
  zone: string;
  inspection_type: string;
  description?: string;
}) => {
  const res = await fetch(API_ENDPOINTS.START_INSPECTION, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });
  return res.json();
};

export const runDetection = async (inspectionId: string, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  const res = await fetch(`${API_ENDPOINTS.RUN_DETECTION}?inspection_id=${inspectionId}`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });
  return res.json();
};

export const approveDetection = async (inspectionId: string) => {
  const res = await fetch(API_ENDPOINTS.APPROVE_DETECTION(inspectionId), {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  return res.json();
};

export const getZones = async () => {
  const res = await fetch(API_ENDPOINTS.GET_ZONES, { headers: getAuthHeaders() });
  return res.json();
};

export const updateZone = async (zoneId: string, status: string) => {
  const res = await fetch(API_ENDPOINTS.UPDATE_ZONE(zoneId), {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify({ status }),
  });
  return res.json();
};

export const startInvestigation = async (data: object) => {
  const res = await fetch(API_ENDPOINTS.START_INVESTIGATION, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });
  return res.json();
};

export const approveAirworthiness = async (threadId: string, approved: boolean, modifiedStatus?: string) => {
  const res = await fetch(API_ENDPOINTS.APPROVE_AIRWORTHINESS(threadId), {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ approved, modified_status: modifiedStatus }),
  });
  return res.json();
};

export const approveFinal = async (threadId: string, approved: boolean) => {
  const res = await fetch(API_ENDPOINTS.APPROVE_FINAL(threadId), {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ approved }),
  });
  return res.json();
};

export const getInvestigationState = async (threadId: string) => {
  const res = await fetch(API_ENDPOINTS.INVESTIGATION_STATE(threadId), { headers: getAuthHeaders() });
  return res.json();
};

export const generateReports = async (data: object) => {
  const res = await fetch(API_ENDPOINTS.GENERATE_REPORTS, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });
  return res.json();
};