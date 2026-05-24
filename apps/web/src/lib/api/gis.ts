import { get } from "../api-client";

export interface GisSite {
  id: string;
  name: string;
  site_type?: string;
  status?: string;
  latitude: number;
  longitude: number;
  address?: string;
  project_id?: string;
}

interface SiteListResponse {
  success: boolean;
  data: {
    items: GisSite[];
    total: number;
  };
}

export function listSites(params?: { page?: number; per_page?: number }) {
  const query = new URLSearchParams();
  if (params?.page) query.set("page", String(params.page));
  if (params?.per_page) query.set("per_page", String(params.per_page));
  const qs = query.toString();
  return get<SiteListResponse>(`/gis/sites${qs ? `?${qs}` : ""}`);
}
