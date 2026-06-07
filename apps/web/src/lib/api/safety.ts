import { get, post, put } from "../api-client";

export interface Hazard {
  id: string;
  organization_id: string;
  site_id?: string;
  title: string;
  description?: string;
  severity: "low" | "medium" | "high" | "critical";
  status: "open" | "in_progress" | "resolved";
  reported_by?: string;
  reported_at?: string;
  resolved_at?: string;
  created_at?: string;
  updated_at?: string;
}

export interface SafetyIncident {
  id: string;
  organization_id: string;
  site_id?: string;
  title: string;
  description?: string;
  incident_type: string;
  severity: "minor" | "moderate" | "serious" | "critical";
  status: string;
  occurred_at?: string;
  created_at?: string;
  updated_at?: string;
}

export interface SafetyInspection {
  id: string;
  organization_id: string;
  site_id?: string;
  inspector_id?: string;
  inspection_type: string;
  status: "scheduled" | "in_progress" | "completed" | "failed";
  scheduled_at?: string;
  completed_at?: string;
  score?: number;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

interface ListResponse<T> {
  items: T[];
  total: number;
}

export function listHazards(params?: {
  organization_id?: string;
  status?: string;
  severity?: string;
}) {
  const q = new URLSearchParams();
  if (params?.organization_id) q.set("organization_id", params.organization_id);
  if (params?.status) q.set("status", params.status);
  if (params?.severity) q.set("severity", params.severity);
  return get<ListResponse<Hazard>>(
    `/safety/hazards${q.toString() ? `?${q}` : ""}`,
  );
}

export function getOpenHazards() {
  return get<Hazard[]>("/safety/hazards/open");
}

export function createHazard(
  body: Omit<Hazard, "id" | "created_at" | "updated_at">,
) {
  return post<Hazard>("/safety/hazards", body);
}

export function updateHazard(id: string, body: Partial<Hazard>) {
  return put<Hazard>(`/safety/hazards/${id}`, body);
}

export function listIncidents(params?: {
  organization_id?: string;
  status?: string;
}) {
  const q = new URLSearchParams();
  if (params?.organization_id) q.set("organization_id", params.organization_id);
  if (params?.status) q.set("status", params.status);
  return get<ListResponse<SafetyIncident>>(
    `/safety/incidents${q.toString() ? `?${q}` : ""}`,
  );
}

export function getIncident(id: string) {
  return get<SafetyIncident>(`/safety/incidents/${id}`);
}

export function createIncident(
  body: Omit<SafetyIncident, "id" | "created_at" | "updated_at">,
) {
  return post<SafetyIncident>("/safety/incidents", body);
}

export function updateIncident(id: string, body: Partial<SafetyIncident>) {
  return put<SafetyIncident>(`/safety/incidents/${id}`, body);
}

export function listInspections(params?: {
  organization_id?: string;
  status?: string;
}) {
  const q = new URLSearchParams();
  if (params?.organization_id) q.set("organization_id", params.organization_id);
  if (params?.status) q.set("status", params.status);
  return get<ListResponse<SafetyInspection>>(
    `/safety/inspections${q.toString() ? `?${q}` : ""}`,
  );
}

export function getInspectionStats() {
  return get<Record<string, number>>("/safety/inspections/stats");
}

export function getInspection(id: string) {
  return get<SafetyInspection>(`/safety/inspections/${id}`);
}

export function createInspection(
  body: Omit<SafetyInspection, "id" | "created_at" | "updated_at">,
) {
  return post<SafetyInspection>("/safety/inspections", body);
}

export function updateInspection(id: string, body: Partial<SafetyInspection>) {
  return put<SafetyInspection>(`/safety/inspections/${id}`, body);
}

export function completeInspection(
  id: string,
  body: { score?: number; notes?: string },
) {
  return post<SafetyInspection>(`/safety/inspections/${id}/complete`, body);
}
