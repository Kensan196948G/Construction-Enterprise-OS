"use client";

import { useState } from "react";
import { FilePlus, ClipboardList, CheckCircle, XCircle } from "lucide-react";

type RequestStatus =
  | "draft"
  | "pending"
  | "approved"
  | "rejected"
  | "completed";

interface MyRequest {
  id: string;
  requestNo: string;
  requestType: string;
  requestedAt: string;
  status: RequestStatus;
  currentApprover: string;
  dueDate: string;
}

const MOCK_REQUESTS: MyRequest[] = [
  {
    id: "r01",
    requestNo: "REQ-2026-0480",
    requestType: "材料購入",
    requestedAt: "2026-05-01",
    status: "completed",
    currentApprover: "—",
    dueDate: "2026-05-10",
  },
  {
    id: "r02",
    requestNo: "REQ-2026-0492",
    requestType: "経費",
    requestedAt: "2026-05-05",
    status: "approved",
    currentApprover: "—",
    dueDate: "2026-05-15",
  },
  {
    id: "r03",
    requestNo: "REQ-2026-0503",
    requestType: "外注",
    requestedAt: "2026-05-08",
    status: "rejected",
    currentApprover: "—",
    dueDate: "2026-05-20",
  },
  {
    id: "r04",
    requestNo: "REQ-2026-0515",
    requestType: "工事変更",
    requestedAt: "2026-05-12",
    status: "pending",
    currentApprover: "部長 鈴木",
    dueDate: "2026-05-26",
  },
  {
    id: "r05",
    requestNo: "REQ-2026-0522",
    requestType: "設計変更",
    requestedAt: "2026-05-14",
    status: "pending",
    currentApprover: "課長 山田",
    dueDate: "2026-05-28",
  },
  {
    id: "r06",
    requestNo: "REQ-2026-0531",
    requestType: "材料購入",
    requestedAt: "2026-05-16",
    status: "completed",
    currentApprover: "—",
    dueDate: "2026-05-22",
  },
  {
    id: "r07",
    requestNo: "REQ-2026-0539",
    requestType: "経費",
    requestedAt: "2026-05-18",
    status: "approved",
    currentApprover: "—",
    dueDate: "2026-05-30",
  },
  {
    id: "r08",
    requestNo: "REQ-2026-0545",
    requestType: "外注",
    requestedAt: "2026-05-19",
    status: "pending",
    currentApprover: "部長 田中",
    dueDate: "2026-06-01",
  },
  {
    id: "r09",
    requestNo: "REQ-2026-0550",
    requestType: "工事変更",
    requestedAt: "2026-05-20",
    status: "draft",
    currentApprover: "—",
    dueDate: "2026-06-03",
  },
  {
    id: "r10",
    requestNo: "REQ-2026-0556",
    requestType: "採用申請",
    requestedAt: "2026-05-21",
    status: "pending",
    currentApprover: "人事部長 伊藤",
    dueDate: "2026-06-05",
  },
  {
    id: "r11",
    requestNo: "REQ-2026-0559",
    requestType: "材料購入",
    requestedAt: "2026-05-22",
    status: "rejected",
    currentApprover: "—",
    dueDate: "2026-06-01",
  },
  {
    id: "r12",
    requestNo: "REQ-2026-0563",
    requestType: "経費",
    requestedAt: "2026-05-23",
    status: "draft",
    currentApprover: "—",
    dueDate: "2026-06-07",
  },
];

const statusMap: Record<RequestStatus, { label: string; className: string }> = {
  draft: { label: "下書き", className: "bg-gray-100 text-gray-600" },
  pending: { label: "承認待ち", className: "bg-blue-100 text-blue-700" },
  approved: { label: "承認済み", className: "bg-green-100 text-green-700" },
  rejected: { label: "差戻し", className: "bg-red-100 text-red-700" },
  completed: {
    label: "完了",
    className: "bg-purple-100 text-purple-700",
  },
};

export default function RequestsPage() {
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [showNewModal, setShowNewModal] = useState(false);

  const pendingCount = MOCK_REQUESTS.filter(
    (r) => r.status === "pending",
  ).length;
  const approvedCount = MOCK_REQUESTS.filter(
    (r) => r.status === "approved",
  ).length;
  const rejectedCount = MOCK_REQUESTS.filter(
    (r) => r.status === "rejected",
  ).length;
  const completedCount = MOCK_REQUESTS.filter(
    (r) => r.status === "completed",
  ).length;

  const filtered = MOCK_REQUESTS.filter(
    (r) => filterStatus === "all" || r.status === filterStatus,
  );

  const stats = [
    {
      label: "申請中",
      value: pendingCount,
      icon: ClipboardList,
      colorBg: "bg-blue-50",
      colorIcon: "text-blue-500",
    },
    {
      label: "承認済み",
      value: approvedCount,
      icon: CheckCircle,
      colorBg: "bg-green-50",
      colorIcon: "text-green-500",
    },
    {
      label: "差戻し",
      value: rejectedCount,
      icon: XCircle,
      colorBg: "bg-red-50",
      colorIcon: "text-red-500",
    },
    {
      label: "完了",
      value: completedCount,
      icon: CheckCircle,
      colorBg: "bg-purple-50",
      colorIcon: "text-purple-500",
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">申請一覧</h1>
          <p className="mt-1 text-sm text-gray-500">
            自分が提出した申請の進捗状況を管理
          </p>
        </div>
        <button
          onClick={() => setShowNewModal(true)}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 transition-colors"
        >
          <FilePlus className="h-4 w-4" />
          新規申請
        </button>
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

      {/* Filter */}
      <div className="flex flex-wrap gap-3">
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-300"
        >
          <option value="all">すべてのステータス</option>
          <option value="draft">下書き</option>
          <option value="pending">承認待ち</option>
          <option value="approved">承認済み</option>
          <option value="rejected">差戻し</option>
          <option value="completed">完了</option>
        </select>
        <span className="self-center text-sm text-gray-500">
          {filtered.length} 件表示
        </span>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
        <div className="flex items-center gap-2 px-5 py-4 border-b border-gray-100">
          <ClipboardList className="h-4 w-4 text-blue-500" />
          <h2 className="font-bold text-gray-900">申請一覧</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50/50">
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  申請番号
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  種別
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  申請日
                </th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  ステータス
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  現在の承認者
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  完了予定日
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((req) => {
                const st = statusMap[req.status];
                return (
                  <tr
                    key={req.id}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-4 py-3 font-mono text-xs font-semibold text-gray-700">
                      {req.requestNo}
                    </td>
                    <td className="px-4 py-3 text-gray-700">
                      {req.requestType}
                    </td>
                    <td className="px-4 py-3 text-gray-500">
                      {req.requestedAt}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${st.className}`}
                      >
                        {st.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {req.currentApprover}
                    </td>
                    <td className="px-4 py-3 text-gray-500">{req.dueDate}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* New Request Modal */}
      {showNewModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
            <h3 className="text-lg font-bold text-gray-900 mb-4">新規申請</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  申請種別
                </label>
                <select className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300">
                  <option>工事変更</option>
                  <option>材料購入</option>
                  <option>外注</option>
                  <option>設計変更</option>
                  <option>経費</option>
                  <option>採用申請</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  件名
                </label>
                <input
                  type="text"
                  placeholder="申請の件名を入力"
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  詳細
                </label>
                <textarea
                  rows={3}
                  placeholder="申請内容の詳細"
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
                />
              </div>
            </div>
            <div className="mt-5 flex justify-end gap-3">
              <button
                onClick={() => setShowNewModal(false)}
                className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              >
                キャンセル
              </button>
              <button
                onClick={() => setShowNewModal(false)}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 transition-colors"
              >
                申請する
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
