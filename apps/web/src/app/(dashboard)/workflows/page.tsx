"use client";

import { useState, useEffect, useCallback } from "react";
import {
  GitBranch,
  CheckCircle,
  Clock,
  XCircle,
  AlertCircle,
  Plus,
  Search,
  Filter,
  ChevronRight,
  User,
  Calendar,
  FileText,
} from "lucide-react";

// Mock data (fallback)
const MOCK_WORKFLOWS = [
  {
    id: "WF-2024-089",
    title: "品川タワー 施工計画書 Rev3 承認",
    type: "document_approval",
    status: "in_progress",
    priority: "high",
    createdAt: "2024-11-20",
    dueDate: "2024-11-22",
    requester: "田中 健一",
    project: "品川タワー新築工事",
    currentStep: 2,
    steps: [
      {
        label: "申請",
        status: "done",
        assignee: "田中 健一",
        completedAt: "2024-11-20 09:00",
      },
      {
        label: "一次確認",
        status: "active",
        assignee: "鈴木 次郎",
        completedAt: null,
      },
      {
        label: "最終承認",
        status: "pending",
        assignee: "山田 部長",
        completedAt: null,
      },
      { label: "完了", status: "pending", assignee: null, completedAt: null },
    ],
  },
  {
    id: "WF-2024-088",
    title: "横浜マンション 配筋検査 承認依頼",
    type: "inspection",
    status: "pending_approval",
    priority: "high",
    createdAt: "2024-11-20",
    dueDate: "2024-11-21",
    requester: "鈴木 次郎",
    project: "横浜分譲マンション建設",
    currentStep: 1,
    steps: [
      {
        label: "申請",
        status: "done",
        assignee: "鈴木 次郎",
        completedAt: "2024-11-20 11:00",
      },
      {
        label: "検査担当確認",
        status: "active",
        assignee: "伊藤 五郎",
        completedAt: null,
      },
      {
        label: "品質管理承認",
        status: "pending",
        assignee: "佐藤 三郎",
        completedAt: null,
      },
      { label: "完了", status: "pending", assignee: null, completedAt: null },
    ],
  },
  {
    id: "WF-2024-087",
    title: "川崎物流センター 重機点検報告",
    type: "safety",
    status: "approved",
    priority: "critical",
    createdAt: "2024-11-19",
    dueDate: "2024-11-19",
    requester: "加藤 二郎",
    project: "川崎物流センター建設",
    currentStep: 3,
    steps: [
      {
        label: "報告",
        status: "done",
        assignee: "加藤 二郎",
        completedAt: "2024-11-19 14:00",
      },
      {
        label: "現場確認",
        status: "done",
        assignee: "伊藤 五郎",
        completedAt: "2024-11-19 15:30",
      },
      {
        label: "安全管理承認",
        status: "done",
        assignee: "山田 部長",
        completedAt: "2024-11-19 17:00",
      },
      {
        label: "完了",
        status: "done",
        assignee: null,
        completedAt: "2024-11-19 17:00",
      },
    ],
  },
  {
    id: "WF-2024-086",
    title: "大田区道路 完成検査申請",
    type: "inspection",
    status: "rejected",
    priority: "medium",
    createdAt: "2024-11-18",
    dueDate: "2024-11-20",
    requester: "佐藤 三郎",
    project: "大田区道路改良工事",
    currentStep: 1,
    steps: [
      {
        label: "申請",
        status: "done",
        assignee: "佐藤 三郎",
        completedAt: "2024-11-18 10:00",
      },
      {
        label: "書類確認",
        status: "rejected",
        assignee: "山田 部長",
        completedAt: "2024-11-18 16:00",
      },
      {
        label: "最終承認",
        status: "pending",
        assignee: "渡辺 六郎",
        completedAt: null,
      },
      { label: "完了", status: "pending", assignee: null, completedAt: null },
    ],
  },
  {
    id: "WF-2024-085",
    title: "新宿再開発 着工前安全計画書",
    type: "safety",
    status: "draft",
    priority: "medium",
    createdAt: "2024-11-17",
    dueDate: "2024-12-01",
    requester: "山田 四郎",
    project: "新宿再開発ビル工事",
    currentStep: 0,
    steps: [
      {
        label: "作成",
        status: "active",
        assignee: "山田 四郎",
        completedAt: null,
      },
      {
        label: "社内レビュー",
        status: "pending",
        assignee: "田中 健一",
        completedAt: null,
      },
      {
        label: "所長承認",
        status: "pending",
        assignee: "山田 部長",
        completedAt: null,
      },
      { label: "完了", status: "pending", assignee: null, completedAt: null },
    ],
  },
];

interface WorkflowStep {
  label: string;
  status: string;
  assignee: string | null;
  completedAt: string | null;
}

interface Workflow {
  id: string;
  title: string;
  type: string;
  status: string;
  priority: string;
  createdAt: string;
  dueDate: string;
  requester: string;
  project: string;
  currentStep: number;
  steps: WorkflowStep[];
}

const workflowTypeConfig: Record<string, { label: string; className: string }> =
  {
    document_approval: {
      label: "書類承認",
      className: "bg-primary-50 text-primary-700",
    },
    inspection: { label: "検査申請", className: "bg-site-50 text-site-700" },
    safety: { label: "安全管理", className: "bg-safety-50 text-safety-700" },
    purchase: {
      label: "購買申請",
      className: "bg-approve-50 text-approve-700",
    },
  };

const statusConfig: Record<
  string,
  { label: string; className: string; icon: React.ElementType }
> = {
  draft: {
    label: "下書き",
    className: "bg-concrete-50 text-concrete-600",
    icon: FileText,
  },
  in_progress: {
    label: "承認中",
    className: "bg-primary-50 text-primary-700",
    icon: Clock,
  },
  pending_approval: {
    label: "承認待ち",
    className: "bg-safety-50 text-safety-700",
    icon: AlertCircle,
  },
  approved: {
    label: "承認済",
    className: "bg-approve-50 text-approve-700",
    icon: CheckCircle,
  },
  rejected: {
    label: "差戻し",
    className: "bg-danger-50 text-danger-700",
    icon: XCircle,
  },
};

const priorityConfig: Record<string, { label: string; className: string }> = {
  critical: { label: "緊急", className: "bg-danger-500 text-white" },
  high: { label: "高", className: "bg-safety-100 text-safety-700" },
  medium: { label: "中", className: "bg-concrete-100 text-concrete-600" },
  low: { label: "低", className: "bg-gray-100 text-gray-500" },
};

const stepStatusConfig: Record<string, string> = {
  done: "bg-approve-500 text-white border-approve-500",
  active: "bg-primary-600 text-white border-primary-600 animate-pulse",
  pending: "bg-white text-gray-400 border-gray-200",
  rejected: "bg-danger-500 text-white border-danger-500",
};

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>(MOCK_WORKFLOWS);
  const [isLoading, setIsLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const loadWorkflows = useCallback(() => {
    setIsLoading(true);
    fetch("/api/v1/workflow/instances?per_page=20")
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (
          data?.success &&
          Array.isArray(data?.data) &&
          data.data.length > 0
        ) {
          const mapped: Workflow[] = (
            data.data as {
              id: string;
              title?: string;
              workflow_type?: string;
              status: string;
              priority?: string;
              created_at: string;
              due_date?: string | null;
              requester_id?: string;
              project_id?: string;
              current_step?: number;
              steps?: WorkflowStep[];
            }[]
          ).map((w) => ({
            id: w.id,
            title: w.title ?? w.id,
            type: w.workflow_type ?? "document_approval",
            status: w.status,
            priority: w.priority ?? "medium",
            createdAt: w.created_at.slice(0, 10),
            dueDate: w.due_date?.slice(0, 10) ?? "—",
            requester: w.requester_id ?? "—",
            project: w.project_id ?? "—",
            currentStep: w.current_step ?? 0,
            steps: w.steps ?? [],
          }));
          setWorkflows(mapped);
        }
      })
      .catch(() => {})
      .finally(() => setIsLoading(false));
  }, []);

  useEffect(() => {
    loadWorkflows();
  }, [loadWorkflows]);

  const handleApprove = async (id: string) => {
    setActionLoading(id);
    try {
      await fetch(`/api/v1/workflow/instances/${id}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
    } catch {
      // ignore network errors; UI will show stale data until next poll
    }
    loadWorkflows();
    setActionLoading(null);
  };

  const handleReject = async (id: string) => {
    setActionLoading(id);
    try {
      await fetch(`/api/v1/workflow/instances/${id}/reject`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
    } catch {
      // ignore network errors
    }
    loadWorkflows();
    setActionLoading(null);
  };

  const summaryStats = [
    {
      label: "承認待ち",
      value: workflows.filter((w) => w.status === "pending_approval").length,
      color: "safety",
    },
    {
      label: "進行中",
      value: workflows.filter((w) => w.status === "in_progress").length,
      color: "primary",
    },
    {
      label: "本日承認済",
      value: workflows.filter((w) => w.status === "approved").length,
      color: "approve",
    },
    {
      label: "差戻し",
      value: workflows.filter((w) => w.status === "rejected").length,
      color: "danger",
    },
  ];

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">ワークフロー</h1>
          <p className="mt-1 text-gray-500 text-sm">
            書類承認・検査申請・安全管理の承認フロー管理
          </p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-700 transition-colors">
          <Plus className="h-4 w-4" />
          新規申請
        </button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {summaryStats.map((stat) => (
          <div
            key={stat.label}
            className={`rounded-xl border p-4 ${
              stat.color === "danger"
                ? "border-danger-200 bg-danger-50"
                : stat.color === "safety"
                  ? "border-safety-200 bg-safety-50"
                  : "border-gray-200 bg-white"
            }`}
          >
            <p
              className={`text-3xl font-bold ${
                stat.color === "danger"
                  ? "text-danger-700"
                  : stat.color === "safety"
                    ? "text-safety-700"
                    : stat.color === "primary"
                      ? "text-primary-700"
                      : "text-approve-700"
              }`}
            >
              {stat.value}
            </p>
            <p className="text-xs text-gray-500 mt-1">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="ワークフロー番号・タイトル・申請者で検索..."
            className="w-full rounded-lg border border-gray-200 bg-white pl-10 pr-4 py-2.5 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          />
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
          <Filter className="h-4 w-4" />
          フィルター
        </button>
      </div>

      {/* Workflow List */}
      <div className="space-y-4">
        {workflows.map((wf) => {
          const status = statusConfig[wf.status];
          const StatusIcon = status.icon;
          const type =
            workflowTypeConfig[wf.type] || workflowTypeConfig.document_approval;
          const priority = priorityConfig[wf.priority];

          return (
            <div
              key={wf.id}
              className="rounded-xl border border-gray-200 bg-white overflow-hidden hover:shadow-sm transition-shadow"
            >
              {/* Header Row */}
              <div className="flex items-start gap-4 p-5 border-b border-gray-100">
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-1.5">
                    <span className="text-xs font-mono text-gray-400">
                      {wf.id}
                    </span>
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${type.className}`}
                    >
                      {type.label}
                    </span>
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${priority.className}`}
                    >
                      {priority.label}
                    </span>
                  </div>
                  <h3 className="font-semibold text-gray-900 text-sm truncate">
                    {wf.title}
                  </h3>
                  <div className="flex flex-wrap items-center gap-4 mt-1.5 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <User className="h-3 w-3" />
                      {wf.requester}
                    </span>
                    <span className="flex items-center gap-1">
                      <GitBranch className="h-3 w-3" />
                      {wf.project}
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      期限: {wf.dueDate}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {(wf.status === "pending_approval" ||
                    wf.status === "in_progress") && (
                    <>
                      <button
                        onClick={() => handleApprove(wf.id)}
                        disabled={actionLoading === wf.id || isLoading}
                        className="inline-flex items-center gap-1 rounded-lg bg-approve-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-approve-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <CheckCircle className="h-3.5 w-3.5" />
                        承認
                      </button>
                      <button
                        onClick={() => handleReject(wf.id)}
                        disabled={actionLoading === wf.id || isLoading}
                        className="inline-flex items-center gap-1 rounded-lg border border-danger-300 px-3 py-1.5 text-xs font-semibold text-danger-700 hover:bg-danger-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <XCircle className="h-3.5 w-3.5" />
                        差戻し
                      </button>
                    </>
                  )}
                  <span
                    className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${status.className}`}
                  >
                    <StatusIcon className="h-3 w-3" />
                    {status.label}
                  </span>
                  <button className="text-gray-400 hover:text-gray-600 transition-colors">
                    <ChevronRight className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Steps */}
              <div className="px-5 py-4 bg-gray-50">
                <div className="flex items-center gap-0">
                  {wf.steps.map((step, idx) => (
                    <div key={idx} className="flex items-center flex-1 min-w-0">
                      <div className="flex flex-col items-center gap-1">
                        <div
                          className={`flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full border-2 text-xs font-bold ${stepStatusConfig[step.status]}`}
                        >
                          {step.status === "done" ? (
                            <CheckCircle className="h-4 w-4" />
                          ) : step.status === "rejected" ? (
                            <XCircle className="h-4 w-4" />
                          ) : (
                            idx + 1
                          )}
                        </div>
                        <p className="text-[10px] text-gray-500 whitespace-nowrap">
                          {step.label}
                        </p>
                        {step.assignee && (
                          <p className="text-[10px] text-gray-400 whitespace-nowrap hidden sm:block">
                            {step.assignee}
                          </p>
                        )}
                      </div>
                      {idx < wf.steps.length - 1 && (
                        <div
                          className={`flex-1 h-0.5 mx-1 mb-5 ${
                            wf.steps[idx + 1].status !== "pending"
                              ? "bg-approve-300"
                              : "bg-gray-200"
                          }`}
                        />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between text-sm text-gray-500">
        <span>全 {workflows.length} 件</span>
        <div className="flex gap-1">
          <button
            className="rounded-lg border border-gray-200 px-3 py-1.5 hover:bg-gray-50 transition-colors disabled:opacity-50"
            disabled
          >
            前へ
          </button>
          <button className="rounded-lg border border-primary-500 bg-primary-50 text-primary-700 px-3 py-1.5 font-medium">
            1
          </button>
          <button className="rounded-lg border border-gray-200 px-3 py-1.5 hover:bg-gray-50 transition-colors">
            次へ
          </button>
        </div>
      </div>
    </div>
  );
}
