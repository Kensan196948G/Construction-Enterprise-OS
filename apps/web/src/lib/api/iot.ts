import { get, post } from "../api-client";

export interface IotDevice {
  id: string;
  name: string;
  device_type: string;
  status: "online" | "offline" | "warning" | "alert";
  location?: string;
  project_id?: string;
  battery_level?: number;
  last_seen?: string;
}

export interface IotAlert {
  id: string;
  device_id: string;
  device_name?: string;
  alert_type: string;
  severity: "warning" | "critical";
  message: string;
  is_acknowledged: boolean;
  created_at: string;
}

interface DeviceListResponse {
  success: boolean;
  data: {
    items: IotDevice[];
    total: number;
  };
}

interface AlertListResponse {
  success: boolean;
  data: {
    items: IotAlert[];
    total: number;
  };
}

export function listDevices(params?: { page?: number; per_page?: number }) {
  const query = new URLSearchParams();
  if (params?.page) query.set("page", String(params.page));
  if (params?.per_page) query.set("per_page", String(params.per_page));
  const qs = query.toString();
  return get<DeviceListResponse>(`/iot/devices${qs ? `?${qs}` : ""}`);
}

export function listAlerts(params?: { page?: number }) {
  const query = new URLSearchParams();
  if (params?.page) query.set("page", String(params.page));
  const qs = query.toString();
  return get<AlertListResponse>(`/iot/alerts${qs ? `?${qs}` : ""}`);
}

export function acknowledgeAlert(alertId: string) {
  return post<{ success: boolean }>(`/iot/alerts/${alertId}/acknowledge`, {});
}
