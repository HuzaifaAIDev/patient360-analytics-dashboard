import axios from "axios";
import type {
  AISummaryResponse,
  CorsOriginInfo,
  DatabaseStatus,
  DatasetOverview,
  DiseaseBreakdown,
  CountItem,
  PatientRecord,
  PatientStats,
  PatientSuggestion,
  PeriodClaim,
  PeriodCount,
  HospitalClaim,
  TimelineCard,
  TopPatient,
} from "@/types";

export const api = axios.create({
  baseURL: "/api",
  timeout: 30000,
});

export const searchPatients = async (query: string, limit = 10): Promise<PatientSuggestion[]> => {
  if (!query.trim()) return [];
  const { data } = await api.get<PatientSuggestion[]>("/search", { params: { q: query, limit } });
  return data;
};

export const getPatientStats = async (name: string): Promise<PatientStats> => {
  const { data } = await api.get<PatientStats>(`/patient/${encodeURIComponent(name)}/stats`);
  return data;
};

export const getPatientHospitals = async (name: string): Promise<CountItem[]> => {
  const { data } = await api.get<CountItem[]>(`/patient/${encodeURIComponent(name)}/hospitals`);
  return data;
};

export const getPatientDoctors = async (name: string): Promise<CountItem[]> => {
  const { data } = await api.get<CountItem[]>(`/patient/${encodeURIComponent(name)}/doctors`);
  return data;
};

export const getPatientCities = async (name: string): Promise<CountItem[]> => {
  const { data } = await api.get<CountItem[]>(`/patient/${encodeURIComponent(name)}/cities`);
  return data;
};

export const getPatientDiseases = async (name: string): Promise<DiseaseBreakdown> => {
  const { data } = await api.get<DiseaseBreakdown>(`/patient/${encodeURIComponent(name)}/diseases`);
  return data;
};

export const getPatientTimeline = async (name: string, order: "asc" | "desc" = "desc"): Promise<TimelineCard[]> => {
  const { data } = await api.get<TimelineCard[]>(`/patient/${encodeURIComponent(name)}/timeline`, {
    params: { order },
  });
  return data;
};

export const getPatientRecords = async (name: string): Promise<PatientRecord[]> => {
  const { data } = await api.get<PatientRecord[]>(`/patient/${encodeURIComponent(name)}/records`);
  return data;
};

export const getAISummary = async (name: string): Promise<AISummaryResponse> => {
  const { data } = await api.get<AISummaryResponse>(`/patient/${encodeURIComponent(name)}/ai-summary`);
  return data;
};

export const getVisitsPerMonth = async (name: string): Promise<PeriodCount[]> => {
  const { data } = await api.get<PeriodCount[]>(`/patient/${encodeURIComponent(name)}/charts/visits-per-month`);
  return data;
};

export const getVisitsPerYear = async (name: string): Promise<PeriodCount[]> => {
  const { data } = await api.get<PeriodCount[]>(`/patient/${encodeURIComponent(name)}/charts/visits-per-year`);
  return data;
};

export const getClaimsPerYear = async (name: string): Promise<PeriodClaim[]> => {
  const { data } = await api.get<PeriodClaim[]>(`/patient/${encodeURIComponent(name)}/charts/claims-per-year`);
  return data;
};

export const getClaimsPerHospital = async (name: string): Promise<HospitalClaim[]> => {
  const { data } = await api.get<HospitalClaim[]>(`/patient/${encodeURIComponent(name)}/charts/claims-per-hospital`);
  return data;
};

export const getOverview = async (): Promise<DatasetOverview> => {
  const { data } = await api.get<DatasetOverview>("/analytics/overview");
  return data;
};

export const getTopPatients = async (limit = 10): Promise<TopPatient[]> => {
  const { data } = await api.get<TopPatient[]>("/analytics/top-patients", { params: { limit } });
  return data;
};

export const getDatabaseStatus = async (): Promise<DatabaseStatus> => {
  const { data } = await api.get<DatabaseStatus>("/database/status");
  return data;
};

export const getCorsOrigins = async (): Promise<CorsOriginInfo[]> => {
  const { data } = await api.get<CorsOriginInfo[]>("/database/cors-origins");
  return data;
};

export const exportUrl = (
  format: "csv" | "excel" | "json" | "pdf",
  patient?: string
): string => {
  const params = new URLSearchParams();
  if (patient) params.set("patient", patient);
  return `/api/export/${format}${params.toString() ? `?${params.toString()}` : ""}`;
};

export const getHealth = async () => {
  const { data } = await api.get("/health");
  return data as { status: string };
};
