export interface PatientSuggestion {
  patient_name: string;
  score: number;
  visit_count: number;
}

export interface PatientStats {
  patient_name: string;
  total_records: number;
  total_visits: number;
  first_visit: string | null;
  last_visit: string | null;
  hospitals_visited: string[];
  doctors_consulted: string[];
  cities_visited: string[];
  average_claim: number | null;
  highest_claim: number | null;
  lowest_claim: number | null;
  total_claimed_amount: number | null;
}

export interface CountItem {
  label: string;
  count: number;
  percentage: number;
}

export interface DiseaseBreakdown {
  frequencies: CountItem[];
  top_diseases: string[];
  recurring_diseases: string[];
}

export interface TimelineCard {
  record_id: string;
  visit_date: string | null;
  hospital: string | null;
  doctor: string | null;
  city: string | null;
  diseases: string[];
  claim_amount: number | null;
  notes: string | null;
}

export interface PatientRecord {
  record_id: string;
  patient_name: string;
  visit_date: string | null;
  hospital: string | null;
  doctor: string | null;
  city: string | null;
  diseases: string[];
  claim_amount: number | null;
  notes: string | null;
  source_file: string | null;
}

export interface AISummaryResponse {
  enabled: boolean;
  summary: string | null;
  message: string | null;
}

export interface PeriodCount {
  period: string;
  count: number;
}

export interface PeriodClaim {
  period: string;
  total_claim: number;
}

export interface HospitalClaim {
  hospital: string;
  total_claim: number;
}

export interface DatasetOverview {
  total_records: number;
  unique_patients: number;
  total_hospitals: number;
  total_doctors: number;
  total_cities: number;
  total_claimed_amount: number;
  hospital_breakdown: CountItem[];
  doctor_breakdown: CountItem[];
  city_breakdown: CountItem[];
  disease_breakdown: DiseaseBreakdown;
  visits_per_month: PeriodCount[];
  visits_per_year: PeriodCount[];
}

export interface DatabaseStatus {
  connected: boolean;
  driver: string;
  database_name: string;
  host: string | null;
  ssl_mode: string | null;
  total_records: number;
  unique_patients: number;
  message: string;
}

export interface CorsOriginInfo {
  origin: string;
  is_active: boolean;
  note: string | null;
  created_at: string;
}

export interface TopPatient {
  patient_name: string;
  visit_count: number;
}
