import { get, post } from "../api-client";

export interface WorkflowStep {
  label: string;
  status: "done" | "active" | "pending";
  assignee?: string | null;
  completed_at?: string | null;
}

export interface WorkflowInstance {
  id: string;
  title?: string;
  workflow_type?: string;
  status:
    | "in_progress"
    | "pending_approval"
    | "approved"
    | "rejected"
    | "cancelled";
  priority?: "low" | "medium" | "high" | "critical";
  created_at: string;
  due_date?: string | null;
  requester_id?: string;
  project_id?: string;
  current_step?: number;
  steps?: WorkflowStep[];
}

// Workflow service returns data as an array directly (no items wrapper)
interface WorkflowListResponse {
  success: boolean;
  data: WorkflowInstance[];
}

export function listWorkflowInstances(params?: {
  page?: number;
  per_page?: number;
}) {
  const query = new URLSearchParams();
  if (params?.page) query.set("page", String(params.page));
  if (params?.per_page) query.set("per_page", String(params.per_page));
  const qs = query.toString();
  return get<WorkflowListResponse>(`/workflow/instances${qs ? `?${qs}` : ""}`);
}

export function getPendingWorkflows() {
  return get<WorkflowListResponse>("/workflow/instances/pending");
}

export function approveWorkflow(instanceId: string, comment?: string) {
  return post<{ success: boolean }>(
    `/workflow/instances/${instanceId}/approve`,
    { comment },
  );
}

export function rejectWorkflow(instanceId: string, comment?: string) {
  return post<{ success: boolean }>(
    `/workflow/instances/${instanceId}/reject`,
    { comment },
  );
}
