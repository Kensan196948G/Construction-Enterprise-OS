import { get, post } from "../api-client";

export interface Document {
  id: string;
  name: string;
  project_id?: string;
  project_name?: string;
  file_type: string;
  file_size: number;
  status: "approved" | "pending" | "review";
  created_by?: string;
  updated_at: string;
}

interface DocumentListResponse {
  success: boolean;
  data: {
    documents: Document[];
    pagination: {
      page: number;
      per_page: number;
      total: number;
      total_pages: number;
    };
  };
}

export function listDocuments(params?: { page?: number; per_page?: number }) {
  const query = new URLSearchParams();
  if (params?.page) query.set("page", String(params.page));
  if (params?.per_page) query.set("per_page", String(params.per_page));
  const qs = query.toString();
  return get<DocumentListResponse>(`/documents${qs ? `?${qs}` : ""}`);
}
