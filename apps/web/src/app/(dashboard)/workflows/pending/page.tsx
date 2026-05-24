"use client";

import { useState } from "react";
import { Clock, CheckCircle, XCircle, AlertCircle } from "lucide-react";

type Urgency = "urgent" | "normal";
type RequestType = "工事変更" | "材料購入" | "外注" | "設計変更" | "経費";

interface PendingRequest {
  id: string;
  requestNo: string;
  requestType: RequestType;
  requester: string;
  requestedAt: string;
  urgency: Urgency;
  summary: string;
  deadline: string;
}

const TODAY = "2026-05-24";

const MOCK_PENDING: PendingRequest[] = [
  {
    id: "p01",
    requestNo: "REQ-2026-0521",
    requestType: "工事変更",
    requester: "田中 太郎",
    requestedAt: "2026-05-20",
    urgency: "urgent",
    summary: "品川タワー3F配管ルート変更（設備干渉回避）",
    deadline: "2026-05-22",
  },
  {
    id: "p02",
    requestNo: "REQ-2026-0534",
    requestType: "材料購入",
    requester: "佐藤 花子",
    requestedAt: "2026-05-21",
    urgency: "normal",
    summary: "コンクリート型枠材 追加発注（川崎物流センター）",
    deadline: "2026-05-28",
  },
  {
    id: "p03",
    requestNo: "REQ-2026-0542",
    requestType: "外注",
    requester: "山田 健一",
    requestedAt: "2026-05-22",
    urgency: "urgent",
    summary: "電気設備工事 専門業者への外注（大田区道路改良）",
    deadline: "2026-05-24",
  },
  {
    id: "p04",
    requestNo: "REQ-2026-0548",
    requestType: "設計変更",
    requester: "鈴木 美咲",
    requestedAt: "2026-05-22",
    urgency: "normal",
    summary: "横浜分譲マンション 外壁仕上げ材変更申請",
    deadline: "2026-05-30",
  },
  {
    id: "p05",
    requestNo: "REQ-2026-0553",
    requestType: "経費",
    requester: "伊藤 大輔",
    requestedAt: "2026-05-23",
    urgency: "normal",
    summary: "現場安全用品購入費 精算申請（5月分）",
    deadline: "2026-05-31",
  },
  {
    id: "p06",
    requestNo: "REQ-2026-0557",
    requestType: "材料購入",
    requester: "高橋 良子",
    requestedAt: "2026-05-23",
    urgency: "urgent",
    summary: "鉄筋材緊急追加発注（新宿再開発 工程遅延防止）",
    deadline: "2026-05-23",
  },
  {
    id: "p07",
    requestNo: "REQ-2026-0561",
    requestType: "工事変更",
    requester: "渡辺 浩二",
    requestedAt: "2026-05-24",
    urgency: "normal",
    summary: "基礎杭打ち工法変更（地盤調査結果に基づく）",
    deadline: "2026-06-02",
  },
  {
    id: "p08",
    requestNo: "REQ-2026-0564",
    requestType: "外注",
    requester: "中村 恵子",
    requestedAt: "2026-05-24",
    urgency: "normal",
    summary: "測量業務 外注発注（品川第2工区）",
    deadline: "2026-06-05",
  },
];

const urgencyMap: Record<Urgency, { label: string; className: string }> = {
  urgent: { label: "緊急", className: "bg-red-100 text-red-700" },
  normal: { label: "通常", className: "bg-blue-100 text-blue-700" },
};

function isOverdue(deadline: string): boolean {
  return deadline < TODAY;
}

function isDueToday(deadline: string): boolean {
  return deadline === TODAY;
}

function calcWaitDays(requestedAt: string): number {
  const diff = new Date(TODAY).getTime() - new Date(requestedAt).getTime();
  return Math.max(0, Math.floor(diff / (1000 * 60 * 60 * 24)));
}

export default function PendingApprovalsPage() {
  const [approvedIds, setApprovedIds] = useState<Set<string>>(new Set());
  const [rejectedIds, setRejectedIds] = useState<Set<string>>(new Set());

  const visible = MOCK_PENDING.filter(
    (r) => !approvedIds.has(r.id) && !rejectedIds.has(r.id),
  );

  const overdueCount = visible.filter((r) => isOverdue(r.deadline)).length;
  const dueTodayCount = visible.filter((r) => isDueToday(r.deadline)).length;
  const avgWait =
    visible.length > 0
      ? Math.round(
          visible.reduce((sum, r) => sum + calcWaitDays(r.requestedAt), 0) /
            visible.length,
        )
      : 0;

  const stats = [
    {
      label: "承認待ち件数",
      value: visible.length,
      icon: Clock,
      colorBg: "bg-blue-50",
      colorIcon: "text-blue-500",
    },
    {
      label: "期限超過",
      value: overdueCount,
      icon: AlertCircle,
      colorBg: "bg-red-50",
      colorIcon: "text-red-500",
    },
    {
      label: "今日期限",
      value: dueTodayCount,
      icon: Clock,
      colorBg: "bg-yellow-50",
      colorIcon: "text-yellow-500",
    },
    {
      label: "平均待機日数",
      value: `${avgWait}日`,
      icon: CheckCircle,
      colorBg: "bg-green-50",
      colorIcon: "text-green-500",
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">承認待ち一覧</h1>
          <p className="mt-1 text-sm text-gray-500">
            承認が必要な申請の一覧と対応状況
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s) => {
          const Icon = s.icon;
          return (
            <div
              key={s.label}
              className="rounded-xl border border-gray-200 bg-white p-5 hover:shadow-md transition-shadow"
            >
              <div className={`inline-flex rounded-lg p-2.5 ${s.colorBg}`}>
                <Icon className={`h-5 w-5 ${s.colorIcon}`} />
              </div>
              <p className="mt-4 text-3xl font-bold text-gray-900">{s.value}</p>
              <p className="mt-1 text-sm font-medium text-gray-600">
                {s.label}
              </p>
            </div>
          );
        })}
      </div>

      {/* Table */}
      <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
        <div className="flex items-center gap-2 px-5 py-4 border-b border-gray-100">
          <Clock className="h-4 w-4 text-blue-500" />
          <h2 className="font-bold text-gray-900">承認待ち申請</h2>
          <span className="ml-auto text-xs text-gray-500">
            {visible.length} 件
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50/50">
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  申請番号
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  申請種別
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  申請者
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  申請日
                </th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  緊急度
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  概要
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  承認期限
                </th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {visible.map((req) => {
                const urg = urgencyMap[req.urgency];
                const overdue = isOverdue(req.deadline);
                const dueToday = isDueToday(req.deadline);
                return (
                  <tr
                    key={req.id}
                    className={`hover:bg-gray-50 transition-colors ${
                      overdue
                        ? "bg-red-50/40"
                        : dueToday
                          ? "bg-yellow-50/40"
                          : ""
                    }`}
                  >
                    <td className="px-4 py-3 font-mono text-xs font-semibold text-gray-700">
                      {req.requestNo}
                    </td>
                    <td className="px-4 py-3 text-gray-700">
                      {req.requestType}
                    </td>
                    <td className="px-4 py-3 font-medium text-gray-900">
                      {req.requester}
                    </td>
                    <td className="px-4 py-3 text-gray-500">
                      {req.requestedAt}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${urg.className}`}
                      >
                        {urg.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-700 max-w-xs truncate">
                      {req.summary}
                    </td>
                    <td
                      className={`px-4 py-3 font-medium ${
                        overdue
                          ? "text-red-600"
                          : dueToday
                            ? "text-yellow-600"
                            : "text-gray-600"
                      }`}
                    >
                      {req.deadline}
                      {overdue && (
                        <span className="ml-1 text-xs text-red-500">
                          (超過)
                        </span>
                      )}
                      {dueToday && (
                        <span className="ml-1 text-xs text-yellow-600">
                          (本日)
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-center gap-2">
                        <button
                          onClick={() =>
                            setApprovedIds((prev) => new Set([...prev, req.id]))
                          }
                          className="inline-flex items-center gap-1 rounded-lg bg-green-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-green-700 transition-colors"
                        >
                          <CheckCircle className="h-3.5 w-3.5" />
                          承認
                        </button>
                        <button
                          onClick={() =>
                            setRejectedIds((prev) => new Set([...prev, req.id]))
                          }
                          className="inline-flex items-center gap-1 rounded-lg bg-red-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-red-700 transition-colors"
                        >
                          <XCircle className="h-3.5 w-3.5" />
                          差戻
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
              {visible.length === 0 && (
                <tr>
                  <td
                    colSpan={8}
                    className="px-4 py-10 text-center text-sm text-gray-400"
                  >
                    承認待ちの申請はありません
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
