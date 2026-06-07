import { get, post, put } from "../api-client";

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  body?: string;
  notification_type: string;
  priority: "low" | "normal" | "high" | "urgent";
  status: "unread" | "read" | "archived";
  action_url?: string;
  metadata?: Record<string, unknown>;
  created_at?: string;
  read_at?: string;
}

export interface NotificationTemplate {
  id: string;
  code: string;
  name: string;
  template_type: string;
  subject_template?: string;
  body_template?: string;
  variables?: string[];
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface NotificationPolicy {
  id: string;
  organization_id: string;
  name: string;
  event_type: string;
  channels: string[];
  recipient_roles?: string[];
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

interface ListResponse<T> {
  items: T[];
  total: number;
}

export function listNotifications(params?: {
  user_id?: string;
  status?: string;
  page?: number;
}) {
  const q = new URLSearchParams();
  if (params?.user_id) q.set("user_id", params.user_id);
  if (params?.status) q.set("status", params.status);
  if (params?.page) q.set("page", String(params.page));
  return get<ListResponse<Notification>>(
    `/notification${q.toString() ? `?${q}` : ""}`,
  );
}

export function getUnreadCount() {
  return get<{ count: number }>("/notification/unread-count");
}

export function markAsRead(id: string) {
  return put<Notification>(`/notification/${id}/read`, {});
}

export function markAllAsRead() {
  return post<{ updated: number }>("/notification/read-all", {});
}

export function listTemplates(params?: { template_type?: string }) {
  const q = new URLSearchParams();
  if (params?.template_type) q.set("template_type", params.template_type);
  return get<ListResponse<NotificationTemplate>>(
    `/notification/templates${q.toString() ? `?${q}` : ""}`,
  );
}

export function getTemplate(code: string) {
  return get<NotificationTemplate>(`/notification/templates/${code}`);
}

export function createTemplate(
  body: Omit<NotificationTemplate, "id" | "created_at" | "updated_at">,
) {
  return post<NotificationTemplate>("/notification/templates", body);
}

export function updateTemplate(
  id: string,
  body: Partial<NotificationTemplate>,
) {
  return put<NotificationTemplate>(`/notification/templates/${id}`, body);
}

export function listPolicies(params?: { organization_id?: string }) {
  const q = new URLSearchParams();
  if (params?.organization_id) q.set("organization_id", params.organization_id);
  return get<ListResponse<NotificationPolicy>>(
    `/notification/policies${q.toString() ? `?${q}` : ""}`,
  );
}

export function createPolicy(
  body: Omit<NotificationPolicy, "id" | "created_at" | "updated_at">,
) {
  return post<NotificationPolicy>("/notification/policies", body);
}

export function updatePolicy(id: string, body: Partial<NotificationPolicy>) {
  return put<NotificationPolicy>(`/notification/policies/${id}`, body);
}
