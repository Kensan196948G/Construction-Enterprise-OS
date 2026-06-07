import { get, post, put, del } from "../api-client";

export interface DataSource {
  id: string;
  organization_id: string;
  name: string;
  source_type: string;
  connection_config: Record<string, unknown>;
  status: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

export interface DataPipeline {
  id: string;
  organization_id: string;
  name: string;
  source_id: string;
  target_id: string;
  transform_logic: Record<string, unknown>;
  schedule?: string;
  status: string;
  last_run?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AnalyticsReport {
  id: string;
  organization_id: string;
  name: string;
  report_type: string;
  query_config: Record<string, unknown>;
  schedule?: string;
  status: string;
  created_at?: string;
  updated_at?: string;
}

interface ListResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}

export function listDataSources(params?: {
  organization_id?: string;
  page?: number;
}) {
  const q = new URLSearchParams();
  if (params?.organization_id) q.set("organization_id", params.organization_id);
  if (params?.page) q.set("page", String(params.page));
  return get<ListResponse<DataSource>>(
    `/analytics/datasources${q.toString() ? `?${q}` : ""}`,
  );
}

export function createDataSource(
  body: Omit<DataSource, "id" | "created_at" | "updated_at">,
) {
  return post<DataSource>("/analytics/datasources", body);
}

export function getDataSource(id: string) {
  return get<DataSource>(`/analytics/datasources/${id}`);
}

export function updateDataSource(id: string, body: Partial<DataSource>) {
  return put<DataSource>(`/analytics/datasources/${id}`, body);
}

export function deleteDataSource(id: string) {
  return del<void>(`/analytics/datasources/${id}`);
}

export function testDataSourceConnection(id: string) {
  return post<{ success: boolean; message: string; source_type: string }>(
    `/analytics/datasources/${id}/test`,
    {},
  );
}

export function listPipelines(params?: { organization_id?: string }) {
  const q = new URLSearchParams();
  if (params?.organization_id) q.set("organization_id", params.organization_id);
  return get<ListResponse<DataPipeline>>(
    `/analytics/pipelines${q.toString() ? `?${q}` : ""}`,
  );
}

export function runPipeline(id: string) {
  return post<{ pipeline_id: string; status: string; started_at: string }>(
    `/analytics/pipelines/${id}/run`,
    {},
  );
}

export function listReports(params?: { organization_id?: string }) {
  const q = new URLSearchParams();
  if (params?.organization_id) q.set("organization_id", params.organization_id);
  return get<ListResponse<AnalyticsReport>>(
    `/analytics/reports${q.toString() ? `?${q}` : ""}`,
  );
}

export function generateReport(id: string) {
  return post<{
    report_id: string;
    data: unknown[];
    summary: Record<string, unknown>;
  }>(`/analytics/reports/${id}/generate`, {});
}

export function exportReport(id: string, format: "json" | "csv" = "json") {
  return post<{ report_id: string; format: string; content: string }>(
    `/analytics/reports/${id}/export?format=${format}`,
    {},
  );
}
