import { get } from "../api-client";

export interface ConstructionSchedule {
  id: string;
  name: string;
  project_id?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
  progress?: number;
  responsible_user_id?: string;
}

interface ScheduleListResponse {
  success: boolean;
  data: {
    items: ConstructionSchedule[];
    total: number;
  };
}

export function listSchedules(params?: { page?: number; per_page?: number }) {
  const query = new URLSearchParams();
  if (params?.page) query.set("page", String(params.page));
  if (params?.per_page) query.set("per_page", String(params.per_page));
  const qs = query.toString();
  return get<ScheduleListResponse>(
    `/construction/schedules${qs ? `?${qs}` : ""}`,
  );
}
