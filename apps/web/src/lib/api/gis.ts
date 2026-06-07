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

interface GeoJSONGeometry {
  type: string;
  coordinates: [number, number];
}

interface GeoJSONFeature {
  type: "Feature";
  geometry: GeoJSONGeometry | null;
  properties: Record<string, unknown>;
}

interface SiteListResponse {
  success: boolean;
  data: {
    type: "FeatureCollection";
    features: GeoJSONFeature[];
  };
  meta?: {
    total: number;
    page: number;
    per_page: number;
  };
}

export function listSites(params?: { page?: number; per_page?: number }) {
  const query = new URLSearchParams();
  if (params?.page) query.set("page", String(params.page));
  if (params?.per_page) query.set("per_page", String(params.per_page));
  const qs = query.toString();
  return get<SiteListResponse>(`/gis/sites${qs ? `?${qs}` : ""}`);
}

export function sitesFromGeoJSON(response: SiteListResponse): GisSite[] {
  if (!response?.success || !response?.data?.features) return [];
  return response.data.features.map((f) => {
    const props = f.properties ?? {};
    const coords = f.geometry?.type === "Point" ? f.geometry.coordinates : null;
    return {
      id: String(props.id ?? ""),
      name: String(props.name ?? ""),
      site_type: props.site_type ? String(props.site_type) : undefined,
      status: props.status ? String(props.status) : undefined,
      latitude: coords ? coords[1] : 0,
      longitude: coords ? coords[0] : 0,
      address: props.address ? String(props.address) : undefined,
      project_id: props.project_id ? String(props.project_id) : undefined,
    };
  });
}
