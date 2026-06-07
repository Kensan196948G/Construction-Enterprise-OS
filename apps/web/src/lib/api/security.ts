import { get, post, put } from "../api-client";

export interface SecurityVulnerability {
  id: string;
  organization_id: string;
  title: string;
  description?: string;
  severity: "info" | "low" | "medium" | "high" | "critical";
  cvss_score?: number;
  cve_id?: string;
  affected_component?: string;
  status: "open" | "in_progress" | "resolved" | "accepted";
  discovered_at?: string;
  resolved_at?: string;
  created_at?: string;
  updated_at?: string;
}

export interface SecurityIncident {
  id: string;
  organization_id: string;
  title: string;
  description?: string;
  incident_type: string;
  severity: "low" | "medium" | "high" | "critical";
  status: "active" | "investigating" | "contained" | "resolved";
  detected_at?: string;
  resolved_at?: string;
  affected_systems?: string[];
  created_at?: string;
  updated_at?: string;
}

export interface IncidentUpdate {
  id: string;
  incident_id: string;
  message: string;
  updated_by?: string;
  created_at?: string;
}

export interface SecurityPolicy {
  id: string;
  organization_id: string;
  title: string;
  policy_type: string;
  content?: string;
  version?: string;
  status: "draft" | "active" | "archived";
  effective_date?: string;
  review_date?: string;
  reviewed_by?: string;
  created_at?: string;
  updated_at?: string;
}

export interface SecurityDashboard {
  total_vulnerabilities: number;
  open_vulnerabilities: number;
  critical_vulnerabilities: number;
  active_incidents: number;
  recent_incidents: SecurityIncident[];
  vulnerability_by_severity: Record<string, number>;
  compliance_score?: number;
}

interface ListResponse<T> {
  items: T[];
  total: number;
}

export function getSecurityDashboard() {
  return get<SecurityDashboard>("/security/dashboard");
}

export function listVulnerabilities(params?: {
  organization_id?: string;
  severity?: string;
  status?: string;
}) {
  const q = new URLSearchParams();
  if (params?.organization_id) q.set("organization_id", params.organization_id);
  if (params?.severity) q.set("severity", params.severity);
  if (params?.status) q.set("status", params.status);
  return get<ListResponse<SecurityVulnerability>>(
    `/security/vulnerabilities${q.toString() ? `?${q}` : ""}`,
  );
}

export function getOpenVulnerabilities() {
  return get<SecurityVulnerability[]>("/security/vulnerabilities/open");
}

export function createVulnerability(
  body: Omit<SecurityVulnerability, "id" | "created_at" | "updated_at">,
) {
  return post<SecurityVulnerability>("/security/vulnerabilities", body);
}

export function updateVulnerability(
  id: string,
  body: Partial<SecurityVulnerability>,
) {
  return put<SecurityVulnerability>(`/security/vulnerabilities/${id}`, body);
}

export function listIncidents(params?: {
  organization_id?: string;
  status?: string;
  severity?: string;
}) {
  const q = new URLSearchParams();
  if (params?.organization_id) q.set("organization_id", params.organization_id);
  if (params?.status) q.set("status", params.status);
  if (params?.severity) q.set("severity", params.severity);
  return get<ListResponse<SecurityIncident>>(
    `/security/incidents${q.toString() ? `?${q}` : ""}`,
  );
}

export function getActiveIncidents() {
  return get<SecurityIncident[]>("/security/incidents/active");
}

export function getIncident(id: string) {
  return get<SecurityIncident>(`/security/incidents/${id}`);
}

export function createIncident(
  body: Omit<SecurityIncident, "id" | "created_at" | "updated_at">,
) {
  return post<SecurityIncident>("/security/incidents", body);
}

export function updateIncident(id: string, body: Partial<SecurityIncident>) {
  return put<SecurityIncident>(`/security/incidents/${id}`, body);
}

export function addIncidentUpdate(incidentId: string, message: string) {
  return post<IncidentUpdate>(`/security/incidents/${incidentId}/updates`, {
    message,
  });
}

export function listPolicies(params?: {
  organization_id?: string;
  status?: string;
}) {
  const q = new URLSearchParams();
  if (params?.organization_id) q.set("organization_id", params.organization_id);
  if (params?.status) q.set("status", params.status);
  return get<ListResponse<SecurityPolicy>>(
    `/security/policies${q.toString() ? `?${q}` : ""}`,
  );
}

export function getPolicy(id: string) {
  return get<SecurityPolicy>(`/security/policies/${id}`);
}

export function createPolicy(
  body: Omit<SecurityPolicy, "id" | "created_at" | "updated_at">,
) {
  return post<SecurityPolicy>("/security/policies", body);
}

export function updatePolicy(id: string, body: Partial<SecurityPolicy>) {
  return put<SecurityPolicy>(`/security/policies/${id}`, body);
}

export function reviewPolicy(id: string) {
  return post<SecurityPolicy>(`/security/policies/${id}/review`, {});
}
