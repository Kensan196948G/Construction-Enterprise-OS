import { get, post, put, del } from "../api-client";

export interface BimModel {
  id: string;
  organization_id: string;
  name: string;
  file_path: string;
  file_size?: number;
  format?: string;
  status: string;
  element_count?: number;
  created_at?: string;
  updated_at?: string;
}

export interface BimElement {
  id: string;
  model_id: string;
  element_id: string;
  category: string;
  level?: string;
  properties: Record<string, unknown>;
  geometry?: Record<string, unknown>;
}

export interface PointCloud {
  id: string;
  organization_id: string;
  name: string;
  file_path: string;
  point_count?: number;
  status: string;
  created_at?: string;
  updated_at?: string;
}

interface ListResponse<T> {
  items: T[];
  total: number;
}

export function listBimModels(params?: {
  organization_id?: string;
  page?: number;
}) {
  const q = new URLSearchParams();
  if (params?.organization_id) q.set("organization_id", params.organization_id);
  if (params?.page) q.set("page", String(params.page));
  return get<ListResponse<BimModel>>(
    `/bim/models${q.toString() ? `?${q}` : ""}`,
  );
}

export function getBimModel(modelId: string) {
  return get<BimModel>(`/bim/models/${modelId}`);
}

export function createBimModel(
  body: Omit<BimModel, "id" | "created_at" | "updated_at">,
) {
  return post<BimModel>("/bim/models", body);
}

export function updateBimModel(modelId: string, body: Partial<BimModel>) {
  return put<BimModel>(`/bim/models/${modelId}`, body);
}

export function deleteBimModel(modelId: string) {
  return del<void>(`/bim/models/${modelId}`);
}

export function getModelElements(
  modelId: string,
  params?: { category?: string; level?: string },
) {
  const q = new URLSearchParams();
  if (params?.category) q.set("category", params.category);
  if (params?.level) q.set("level", params.level);
  return get<BimElement[]>(
    `/bim/${modelId}/elements${q.toString() ? `?${q}` : ""}`,
  );
}

export function searchElements(query: string, modelId?: string) {
  const q = new URLSearchParams({ query });
  if (modelId) q.set("model_id", modelId);
  return get<BimElement[]>(`/bim/elements/search?${q}`);
}

export function listPointClouds(params?: { organization_id?: string }) {
  const q = new URLSearchParams();
  if (params?.organization_id) q.set("organization_id", params.organization_id);
  return get<ListResponse<PointCloud>>(
    `/bim/pointclouds${q.toString() ? `?${q}` : ""}`,
  );
}

export function createPointCloud(
  body: Omit<PointCloud, "id" | "created_at" | "updated_at">,
) {
  return post<PointCloud>("/bim/pointclouds", body);
}

export function getPointCloud(id: string) {
  return get<PointCloud>(`/bim/pointclouds/${id}`);
}

export function updatePointCloud(id: string, body: Partial<PointCloud>) {
  return put<PointCloud>(`/bim/pointclouds/${id}`, body);
}

export function deletePointCloud(id: string) {
  return del<void>(`/bim/pointclouds/${id}`);
}
