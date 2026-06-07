"use client";

import { useState, useEffect, useCallback } from "react";
import {
  ClipboardCheck,
  AlertCircle,
  Users,
  Clock,
  CheckCircle2,
  Circle,
  Plus,
  RefreshCw,
} from "lucide-react";

interface WorkInstruction {
  id: string;
  number: string;
  title: string;
  zone: string;
  priority: "critical" | "high" | "normal" | "low";
  deadline: string;
  status: "pending" | "in_progress" | "completed" | "cancelled";
  assignee: string;
  created_at: string;
}

const MOCK_INSTRUCTIONS: WorkInstruction[] = [
  {
    id: "wi1",
    number: "WI-2026-001",
    title: "D工区 排水管埋設工事の遅延挽回計画策定",
    zone: "D工区",
    priority: "critical",
    deadline: "2026-05-25",
    status: "in_progress",
    assignee: "山田 浩二",
    created_at: "2026-05-24T08:00:00Z",
  },
  {
    id: "wi2",
    number: "WI-2026-002",
    title: "B工区 3Fスラブ養生期間管理・脱型判定",
    zone: "B工区",
    priority: "high",
    deadline: "2026-05-28",
    status: "in_progress",
    assignee: "鈴木 健太",
    created_at: "2026-05-24T09:00:00Z",
  },
  {
    id: "wi3",
    number: "WI-2026-003",
    title: "C工区 内装仕上げ材発注確認（クロス・床材）",
    zone: "C工区",
    priority: "high",
    deadline: "2026-05-26",
    status: "pending",
    assignee: "佐藤 誠",
    created_at: "2026-05-23T14:00:00Z",
  },
  {
    id: "wi4",
    number: "WI-2026-004",
    title: "全工区 週次安全パトロール実施",
    zone: "全工区",
    priority: "normal",
    deadline: "2026-05-24",
    status: "completed",
    assignee: "田中 一郎",
    created_at: "2026-05-22T10:00:00Z",
  },
  {
    id: "wi5",
    number: "WI-2026-005",
    title: "B工区 4F 鉄筋配筋検査立会い手配",
    zone: "B工区",
    priority: "high",
    deadline: "2026-05-27",
    status: "pending",
    assignee: "渡辺 大輔",
    created_at: "2026-05-23T11:00:00Z",
  },
  {
    id: "wi6",
    number: "WI-2026-006",
    title: "D工区 設計変更協議資料作成",
    zone: "D工区",
    priority: "critical",
    deadline: "2026-05-25",
    status: "pending",
    assignee: "中村 修",
    created_at: "2026-05-24T07:30:00Z",
  },
  {
    id: "wi7",
    number: "WI-2026-007",
    title: "A工区 完成検査書類整備",
    zone: "A工区",
    priority: "normal",
    deadline: "2026-05-30",
    status: "in_progress",
    assignee: "伊藤 隆",
    created_at: "2026-05-21T09:00:00Z",
  },
  {
    id: "wi8",
    number: "WI-2026-008",
    title: "C工区 防水検査前清掃・整理",
    zone: "C工区",
    priority: "low",
    deadline: "2026-05-31",
    status: "pending",
    assignee: "佐藤 誠",
    created_at: "2026-05-23T16:00:00Z",
  },
];

const priorityStyle: Record<string, { label: string; className: string }> = {
  critical: {
    label: "最優先",
    className: "bg-red-100 text-red-700 border border-red-200",
  },
  high: {
    label: "高",
    className: "bg-orange-100 text-orange-700 border border-orange-200",
  },
  normal: {
    label: "通常",
    className: "bg-blue-100 text-blue-700 border border-blue-200",
  },
  low: {
    label: "低",
    className: "bg-gray-100 text-gray-600 border border-gray-200",
  },
};

const statusStyle: Record<
  string,
  { label: string; className: string; icon: React.ElementType }
> = {
  pending: {
    label: "未着手",
    className: "bg-gray-100 text-gray-600",
    icon: Circle,
  },
  in_progress: {
    label: "進行中",
    className: "bg-blue-50 text-blue-700",
    icon: Clock,
  },
  completed: {
    label: "完了",
    className: "bg-green-50 text-green-700",
    icon: CheckCircle2,
  },
  cancelled: {
    label: "中止",
    className: "bg-red-50 text-red-500",
    icon: AlertCircle,
  },
};

function formatDate(iso: string): string {
  const d = new Date(iso);
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, "0")}/${String(d.getDate()).padStart(2, "0")}`;
}

function isOverdue(deadline: string, status: string): boolean {
  if (status === "completed" || status === "cancelled") return false;
  return new Date(deadline) < new Date("2026-05-24");
}

export default function FieldInstructionsPage() {
  const [instructions, setInstructions] =
    useState<WorkInstruction[]>(MOCK_INSTRUCTIONS);
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterPriority, setFilterPriority] = useState<string>("all");
  const [loading, setLoading] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    const res = await fetch("/api/v1/field/instructions").catch(() => null);
    if (res?.ok) {
      const json = await res.json().catch(() => null);
      if (Array.isArray(json?.data))
        setInstructions(json.data as WorkInstruction[]);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const filtered = instructions.filter((i) => {
    const statusOk = filterStatus === "all" || i.status === filterStatus;
    const priorityOk =
      filterPriority === "all" || i.priority === filterPriority;
    return statusOk && priorityOk;
  });

  const pendingCount = instructions.filter(
    (i) => i.status === "pending",
  ).length;
  const inProgressCount = instructions.filter(
    (i) => i.status === "in_progress",
  ).length;
  const completedCount = instructions.filter(
    (i) => i.status === "completed",
  ).length;
  const criticalCount = instructions.filter(
    (i) => i.priority === "critical" && i.status !== "completed",
  ).length;

  const statCards = [
    {
      label: "未着手",
      value: pendingCount,
      icon: Circle,
      color: "text-gray-500 bg-gray-50",
    },
    {
      label: "進行中",
      value: inProgressCount,
      icon: Clock,
      color: "text-blue-500 bg-blue-50",
    },
    {
      label: "完了",
      value: completedCount,
      icon: CheckCircle2,
      color: "text-green-500 bg-green-50",
    },
    {
      label: "最優先（未完了）",
      value: criticalCount,
      icon: AlertCircle,
      color:
        criticalCount > 0
          ? "text-red-500 bg-red-50"
          : "text-green-500 bg-green-50",
    },
  ];

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">作業指示</h1>
          <p className="mt-1 text-sm text-gray-500">
            現場作業指示の発行・進捗管理を行います
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={loadData}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            更新
          </button>
          <button className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 transition-colors">
            <Plus className="h-4 w-4" />
            新規指示登録
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card) => {
          const Icon = card.icon;
          const [iconColor, bgColor] = card.color.split(" ");
          return (
            <div
              key={card.label}
              className="rounded-xl border border-gray-200 bg-white p-5 hover:shadow-md transition-shadow"
            >
              <div className={`inline-flex rounded-lg p-2.5 ${bgColor}`}>
                <Icon className={`h-5 w-5 ${iconColor}`} />
              </div>
              <p className="mt-4 text-3xl font-bold text-gray-900">
                {card.value}
              </p>
              <p className="mt-1 text-sm font-medium text-gray-600">
                {card.label}
              </p>
            </div>
          );
        })}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 items-center">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-gray-500">ステータス:</span>
          {(["all", "pending", "in_progress", "completed"] as const).map(
            (s) => (
              <button
                key={s}
                onClick={() => setFilterStatus(s)}
                className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                  filterStatus === s
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {s === "all" ? "すべて" : (statusStyle[s]?.label ?? s)}
              </button>
            ),
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-gray-500">優先度:</span>
          {(["all", "critical", "high", "normal", "low"] as const).map((p) => (
            <button
              key={p}
              onClick={() => setFilterPriority(p)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                filterPriority === p
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {p === "all" ? "すべて" : (priorityStyle[p]?.label ?? p)}
            </button>
          ))}
        </div>
      </div>

      {/* Instructions Table */}
      <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <h2 className="font-bold text-gray-900 flex items-center gap-2">
            <ClipboardCheck className="h-4 w-4 text-blue-500" />
            作業指示一覧
          </h2>
          <span className="text-xs text-gray-500">
            {filtered.length} 件表示
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50/50">
                <th className="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">
                  指示番号
                </th>
                <th className="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  タイトル
                </th>
                <th className="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">
                  対象工区
                </th>
                <th className="px-5 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">
                  優先度
                </th>
                <th className="px-5 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">
                  期限
                </th>
                <th className="px-5 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">
                  ステータス
                </th>
                <th className="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">
                  担当者
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((inst) => {
                const prio = priorityStyle[inst.priority];
                const st = statusStyle[inst.status];
                const StatusIcon = st.icon;
                const overdue = isOverdue(inst.deadline, inst.status);
                return (
                  <tr
                    key={inst.id}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-5 py-3.5 font-mono text-xs text-gray-500 whitespace-nowrap">
                      {inst.number}
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="font-medium text-gray-900">
                        {inst.title}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      <span className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                        {inst.zone}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-center whitespace-nowrap">
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${prio.className}`}
                      >
                        {prio.label}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-center whitespace-nowrap">
                      <span
                        className={`text-xs font-medium ${overdue ? "text-red-600 font-bold" : "text-gray-600"}`}
                      >
                        {formatDate(inst.deadline)}
                        {overdue && (
                          <span className="ml-1 text-red-500">(!)</span>
                        )}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-center whitespace-nowrap">
                      <span
                        className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${st.className}`}
                      >
                        <StatusIcon className="h-3 w-3" />
                        {st.label}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-gray-600 whitespace-nowrap">
                      <span className="inline-flex items-center gap-1.5">
                        <Users className="h-3.5 w-3.5 text-gray-400" />
                        {inst.assignee}
                      </span>
                    </td>
                  </tr>
                );
              })}
              {filtered.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-5 py-10 text-center text-sm text-gray-400"
                  >
                    該当する作業指示はありません
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
