import { create } from "zustand";
import type {
  AnalysisResult,
  Airworthiness,
  AirworthinessOverride,
  DetectionResult,
  ReportApproval,
  ReportArtifact,
} from "../types";

interface WorkflowState {
  inspectionId: string | null;
  detection: DetectionResult | null;
  analysis: AnalysisResult | null;
  airworthinessOverride: AirworthinessOverride | null;
  reports: ReportArtifact[];
  reportApproval: ReportApproval;
  approvedDetection: boolean;
  approvedAnalysis: boolean;
  setDetection: (d: DetectionResult, backendInspectionId?: string) => void;
  approveDetection: () => void;
  rejectDetection: () => void;
  setAnalysis: (a: AnalysisResult) => void;
  overrideAirworthiness: (status: Airworthiness, reason: string) => void;
  clearAirworthinessOverride: () => void;
  approveAnalysis: () => void;
  generateReports: () => void;
  approveReports: (notes?: string) => void;
  flagReports: (reason: string) => void;
  resetReportApproval: () => void;
  reset: () => void;
}

const INITIAL_APPROVAL: ReportApproval = { status: "pending" };

export const useWorkflow = create<WorkflowState>((set, get) => ({
  inspectionId: null,
  detection: null,
  analysis: null,
  airworthinessOverride: null,
  reports: [],
  reportApproval: INITIAL_APPROVAL,
  approvedDetection: false,
  approvedAnalysis: false,
  setDetection: (d, backendInspectionId?: string) =>
    set({
      detection: d,
      inspectionId: backendInspectionId || `INS-${Date.now().toString(36).toUpperCase()}`,
      approvedDetection: false,
      analysis: null,
      airworthinessOverride: null,
      approvedAnalysis: false,
      reports: [],
      reportApproval: INITIAL_APPROVAL,
    }),
  approveDetection: () => set({ approvedDetection: true }),
  rejectDetection: () =>
    set({ detection: null, inspectionId: null, approvedDetection: false }),
  setAnalysis: (a) => set({ analysis: a, airworthinessOverride: null }),
  overrideAirworthiness: (status, reason) => {
    const { analysis, airworthinessOverride } = get();
    if (!analysis) return;
    const original = airworthinessOverride?.original ?? analysis.airworthiness;
    set({
      analysis: { ...analysis, airworthiness: status },
      airworthinessOverride: {
        original,
        overridden: status,
        reason,
        by: "Inspector",
        at: new Date().toISOString(),
      },
    });
  },
  clearAirworthinessOverride: () => {
    const { analysis, airworthinessOverride } = get();
    if (!analysis || !airworthinessOverride) return;
    set({
      analysis: { ...analysis, airworthiness: airworthinessOverride.original },
      airworthinessOverride: null,
    });
  },
  approveAnalysis: () => {
    set({ approvedAnalysis: true });
    get().generateReports();
  },
  generateReports: () => {
    const id = get().inspectionId ?? "INS";
    set({
      reports: [
        {
          id: `DAR-${id}`,
          type: "defect_analysis",
          name: "Defect Analysis Report",
          createdAt: new Date().toISOString(),
        },
        {
          id: `WO-${id}`,
          type: "work_order",
          name: "Work Order",
          createdAt: new Date().toISOString(),
        },
      ],
      reportApproval: INITIAL_APPROVAL,
    });
  },
  approveReports: (notes) =>
    set({
      reportApproval: {
        status: "approved",
        notes,
        by: "Inspector",
        at: new Date().toISOString(),
      },
    }),
  flagReports: (reason) =>
    set({
      reportApproval: {
        status: "flagged",
        notes: reason,
        by: "Inspector",
        at: new Date().toISOString(),
      },
    }),
  resetReportApproval: () => set({ reportApproval: INITIAL_APPROVAL }),
  reset: () =>
    set({
      inspectionId: null,
      detection: null,
      analysis: null,
      airworthinessOverride: null,
      reports: [],
      reportApproval: INITIAL_APPROVAL,
      approvedDetection: false,
      approvedAnalysis: false,
    }),
}));
