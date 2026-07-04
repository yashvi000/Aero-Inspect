import zoneData from "../../shared/zone_definitions.json";

// Zone helpers from zone_definitions.json
export const ZONES = zoneData.zones.map(
  (z) => `${z.code} - ${z.zone_label}`
);
export const INSPECTION_TYPES = [
  "GVI — General Visual",
  "DVI — Detailed Visual",
  "SDI — Special Detailed",
];
export const DEFECT_TYPES = ["Crack", "Corrosion", "Scratch", "Dent", "Paint"];
export const ZONE_DEFINITIONS = zoneData.zones;

// API endpoints
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  LOGIN: `${API_BASE_URL}/api/auth/login`,
  REGISTER: `${API_BASE_URL}/api/auth/register`,
  ME: `${API_BASE_URL}/api/auth/me`,
  START_INSPECTION: `${API_BASE_URL}/api/inspections/start`,
  LIST_INSPECTIONS: `${API_BASE_URL}/api/inspections/list`,
  RUN_DETECTION: `${API_BASE_URL}/api/detections/run`,
  APPROVE_DETECTION: (id: string) => `${API_BASE_URL}/api/detections/${id}/approve`,
  ANNOTATED_IMAGE: (id: string) => `${API_BASE_URL}/api/detections/${id}/annotated-image`,
  GET_ZONES: `${API_BASE_URL}/api/zones`,
  ZONE_HISTORY: (id: string) => `${API_BASE_URL}/api/zones/${id}/history`,
  UPDATE_ZONE: (id: string) => `${API_BASE_URL}/api/zones/${id}`,
  START_INVESTIGATION: `${API_BASE_URL}/api/investigations/start`,
  APPROVE_AIRWORTHINESS: (id: string) => `${API_BASE_URL}/api/investigations/${id}/approve-airworthiness`,
  APPROVE_FINAL: (id: string) => `${API_BASE_URL}/api/investigations/${id}/approve-final`,
  INVESTIGATION_STATE: (id: string) => `${API_BASE_URL}/api/investigations/${id}/state`,
  GENERATE_REPORTS: `${API_BASE_URL}/api/reports/generate`,
  DEFECT_REPORT: (id: string) => `${API_BASE_URL}/api/reports/${id}/defect-report`,
  WORK_ORDER: (id: string) => `${API_BASE_URL}/api/reports/${id}/work-order`,
  HEALTH: `${API_BASE_URL}/health`,
} as const;