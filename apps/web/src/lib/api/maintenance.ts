import { get, post, put } from "../api-client";

export interface MaintenanceRecord {
  id: string;
  organization_id: string;
  asset_id?: string;
  asset_type?: string;
  title: string;
  description?: string;
  maintenance_type: string;
  status: "scheduled" | "in_progress" | "completed" | "overdue";
  scheduled_at?: string;
  completed_at?: string;
  technician_id?: string;
  cost?: number;
  notes?: string;
  next_maintenance_at?: string;
  created_at?: string;
  updated_at?: string;
}

export interface MaintenanceInspection {
  id: string;
  organization_id: string;
  asset_id?: string;
  inspector_id?: string;
  inspection_type: string;
  status: "scheduled" | "in_progress" | "completed" | "failed";
  scheduled_at?: string;
  completed_at?: string;
  result?: string;
  findings?: string;
  next_inspection_at?: string;
  created_at?: string;
  updated_at?: string;
}

export interface DisasterRecord {
  id: string;
  organization_id: string;
  site_id?: string;
  disaster_type: string;
  title: string;
  description?: string;
  severity: "minor" | "moderate" | "major" | "catastrophic";
  status: "active" | "contained" | "recovering" | "resolved";
  occurred_at?: string;
  resolved_at?: string;
  created_at?: string;
  updated_at?: string;
}

export interface RecoveryPlan {
  id: string;
  disaster_id: string;
  title: string;
  description?: string;
  status: "draft" | "active" | "completed";
  priority: number;
  estimated_duration_days?: number;
  estimated_cost?: number;
  start_date?: string;
  end_date?: string;
  created_at?: string;
  updated_at?: string;
}

interface ListResponse<T> {
  items: T[];
  total: number;
}

export function listMaintenanceRecords(params?: {
  organization_id?: string;
  status?: string;
  asset_id?: string;
}) {
  const q = new URLSearchParams();
  if (params?.organization_id) q.set("organization_id", params.organization_id);
  if (params?.status) q.set("status", params.status);
  if (params?.asset_id) q.set("asset_id", params.asset_id);
  return get<ListResponse<MaintenanceRecord>>(
    `/maintenance/records${q.toString() ? `?${q}` : ""}`,
  );
}

export function getOverdueRecords() {
  return get<MaintenanceRecord[]>("/maintenance/records/overdue");
}

export function getMaintenanceRecord(id: string) {
  return get<MaintenanceRecord>(`/maintenance/records/${id}`);
}

export function createMaintenanceRecord(
  body: Omit<MaintenanceRecord, "id" | "created_at" | "updated_at">,
) {
  return post<MaintenanceRecord>("/maintenance/records", body);
}

export function updateMaintenanceRecord(
  id: string,
  body: Partial<MaintenanceRecord>,
) {
  return put<MaintenanceRecord>(`/maintenance/records/${id}`, body);
}

export function listInspections(params?: {
  organization_id?: string;
  status?: string;
}) {
  const q = new URLSearchParams();
  if (params?.organization_id) q.set("organization_id", params.organization_id);
  if (params?.status) q.set("status", params.status);
  return get<ListResponse<MaintenanceInspection>>(
    `/maintenance/inspections${q.toString() ? `?${q}` : ""}`,
  );
}

export function getUpcomingInspections() {
  return get<MaintenanceInspection[]>("/maintenance/inspections/upcoming");
}

export function getOverdueInspections() {
  return get<MaintenanceInspection[]>("/maintenance/inspections/overdue");
}

export function getInspection(id: string) {
  return get<MaintenanceInspection>(`/maintenance/inspections/${id}`);
}

export function createInspection(
  body: Omit<MaintenanceInspection, "id" | "created_at" | "updated_at">,
) {
  return post<MaintenanceInspection>("/maintenance/inspections", body);
}

export function updateInspection(
  id: string,
  body: Partial<MaintenanceInspection>,
) {
  return put<MaintenanceInspection>(`/maintenance/inspections/${id}`, body);
}

export function listDisasters(params?: {
  organization_id?: string;
  status?: string;
  disaster_type?: string;
}) {
  const q = new URLSearchParams();
  if (params?.organization_id) q.set("organization_id", params.organization_id);
  if (params?.status) q.set("status", params.status);
  if (params?.disaster_type) q.set("disaster_type", params.disaster_type);
  return get<ListResponse<DisasterRecord>>(
    `/maintenance/disasters${q.toString() ? `?${q}` : ""}`,
  );
}

export function getDisaster(id: string) {
  return get<DisasterRecord>(`/maintenance/disasters/${id}`);
}

export function createDisaster(
  body: Omit<DisasterRecord, "id" | "created_at" | "updated_at">,
) {
  return post<DisasterRecord>("/maintenance/disasters", body);
}

export function updateDisaster(id: string, body: Partial<DisasterRecord>) {
  return put<DisasterRecord>(`/maintenance/disasters/${id}`, body);
}

export function createRecoveryPlan(
  disasterId: string,
  body: Omit<RecoveryPlan, "id" | "disaster_id" | "created_at" | "updated_at">,
) {
  return post<RecoveryPlan>(
    `/maintenance/disasters/${disasterId}/recovery-plans`,
    body,
  );
}

export function getRecoveryPlan(planId: string) {
  return get<RecoveryPlan>(`/maintenance/recovery-plans/${planId}`);
}

export function updateRecoveryPlan(
  planId: string,
  body: Partial<RecoveryPlan>,
) {
  return put<RecoveryPlan>(`/maintenance/recovery-plans/${planId}`, body);
}
