export type Severity = "Low" | "Medium" | "High";
export type Airworthiness =
  | "AIRWORTHY"
  | "AIRWORTHY_WITH_CONDITIONS"
  | "GROUND_AIRCRAFT";

export interface DetectionResult {
  imageUrl: string;
  defectType: string;
  confidence: number;
  severity: Severity;
  zone: string;
  bbox: { x: number; y: number; w: number; h: number };
}

export interface AnalysisResult {
  airworthiness: Airworthiness;
  probableCauses: string[];
  regulations: { id: string; source: string; requirement: string }[];
  conditions: string[];
  similarCases: { ref: string; summary: string }[];
  recommendation: string;
}

export interface AirworthinessOverride {
  original: Airworthiness;
  overridden: Airworthiness;
  reason: string;
  by: string;
  at: string;
}

export interface ReportArtifact {
  id: string;
  type: "defect_analysis" | "work_order";
  name: string;
  createdAt: string;
}

export type ReportApprovalStatus = "pending" | "approved" | "flagged";

export interface ReportApproval {
  status: ReportApprovalStatus;
  notes?: string;
  by?: string;
  at?: string;
}

export type Role = "inspector" | "engineer" | "admin";

export interface User {
  email: string;
  name: string;
  role: Role;
}
