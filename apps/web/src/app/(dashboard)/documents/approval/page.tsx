"use client";

import { useState } from "react";
import {
  FileCheck,
  Clock,
  CheckCircle,
  XCircle,
  MessageSquare,
} from "lucide-react";

type ApprovalStatus = "pending" | "approved" | "rejected" | "expired";

interface ApprovalDocument {
  id: string;
  docNumber: string;
  docName: string;
  docType: string;
  submitter: string;
  submittedDate: string;
  approvalStage: string;
  deadline: string;
  status: ApprovalStatus;
}

const MOCK_DOCUMENTS: ApprovalDocument[] = [
  {
    id: "1",
    docNumber: "DOC-2026-001",
    docName: "施工計画書 第3工区",
    docType: "施工計画",
    submitter: "田中 一郎",
    submittedDate: "2026-05-20",
    approvalStage: "現場所長 承認待ち",
    deadline: "2026-05-27",
    status: "pending",
  },
  {
    id: "2",
    docNumber: "DOC-2026-002",
    docName: "品質管理計画書 R2",
    docType: "品質管理",
    submitter: "鈴木 花子",
    submittedDate: "2026-05-18",
    approvalStage: "品質管理部 承認待ち",
    deadline: "2026-05-25",
    status: "pending",
  },
  {
    id: "3",
    docNumber: "DOC-2026-003",
    docName: "安全衛生管理計画書",
    docType: "安全管理",
    submitter: "山田 太郎",
    submittedDate: "2026-05-15",
    approvalStage: "全承認完了",
    deadline: "2026-05-22",
    status: "approved",
  },
  {
    id: "4",
    docNumber: "DOC-2026-004",
    docName: "設計変更申請書 #12",
    docType: "設計変更",
    submitter: "佐藤 次郎",
    submittedDate: "2026-05-14",
    approvalStage: "設計部 差戻し",
    deadline: "2026-05-21",
    status: "rejected",
  },
  {
    id: "5",
    docNumber: "DOC-2026-005",
    docName: "工事写真台帳 5月分",
    docType: "報告書",
    submitter: "伊藤 三郎",
    submittedDate: "2026-05-10",
    approvalStage: "監督員 承認待ち",
    deadline: "2026-05-17",
    status: "expired",
  },
  {
    id: "6",
    docNumber: "DOC-2026-006",
    docName: "材料承認申請書 コンクリート",
    docType: "材料承認",
    submitter: "高橋 四郎",
    submittedDate: "2026-05-22",
    approvalStage: "材料管理部 承認待ち",
    deadline: "2026-05-29",
    status: "pending",
  },
  {
    id: "7",
    docNumber: "DOC-2026-007",
    docName: "掘削工事計画書",
    docType: "施工計画",
    submitter: "渡辺 五郎",
    submittedDate: "2026-05-19",
    approvalStage: "全承認完了",
    deadline: "2026-05-26",
    status: "approved",
  },
  {
    id: "8",
    docNumber: "DOC-2026-008",
    docName: "環境保全計画書",
    docType: "環境管理",
    submitter: "中村 六郎",
    submittedDate: "2026-05-21",
    approvalStage: "環境担当 承認待ち",
    deadline: "2026-05-28",
    status: "pending",
  },
];

const STATUS_CONFIG: Record<
  ApprovalStatus,
  { label: string; className: string }
> = {
  pending: { label: "承認待ち", className: "bg-yellow-100 text-yellow-800" },
  approved: { label: "承認済み", className: "bg-green-100 text-green-800" },
  rejected: { label: "差戻し", className: "bg-red-100 text-red-800" },
  expired: { label: "期限超過", className: "bg-gray-100 text-gray-800" },
};

export default function ApprovalPage() {
  const [documents, setDocuments] =
    useState<ApprovalDocument[]>(MOCK_DOCUMENTS);
  const [filterStatus, setFilterStatus] = useState<string>("all");

  const stats = {
    pending: documents.filter((d) => d.status === "pending").length,
    approvedThisWeek: documents.filter((d) => d.status === "approved").length,
    rejected: documents.filter((d) => d.status === "rejected").length,
    expired: documents.filter((d) => d.status === "expired").length,
  };

  const filtered =
    filterStatus === "all"
      ? documents
      : documents.filter((d) => d.status === filterStatus);

  const handleApprove = (id: string) => {
    setDocuments((prev) =>
      prev.map((d) =>
        d.id === id
          ? {
              ...d,
              status: "approved" as ApprovalStatus,
              approvalStage: "全承認完了",
            }
          : d,
      ),
    );
  };

  const handleReject = (id: string) => {
    setDocuments((prev) =>
      prev.map((d) =>
        d.id === id
          ? {
              ...d,
              status: "rejected" as ApprovalStatus,
              approvalStage: "差戻し",
            }
          : d,
      ),
    );
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">承認文書管理</h1>
          <p className="text-sm text-gray-500 mt-1">
            文書・図面管理 — 承認フロー処理
          </p>
        </div>
        <FileCheck className="w-8 h-8 text-blue-600" />
      </div>

      {/* 統計カード */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Clock className="w-8 h-8 text-yellow-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">承認待ち</p>
            <p className="text-2xl font-bold text-yellow-600">
              {stats.pending}
            </p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <CheckCircle className="w-8 h-8 text-green-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">今週承認済み</p>
            <p className="text-2xl font-bold text-green-600">
              {stats.approvedThisWeek}
            </p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <XCircle className="w-8 h-8 text-red-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">差戻し数</p>
            <p className="text-2xl font-bold text-red-600">{stats.rejected}</p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Clock className="w-8 h-8 text-gray-400 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">期限超過</p>
            <p className="text-2xl font-bold text-gray-600">{stats.expired}</p>
          </div>
        </div>
      </div>

      {/* フィルタ */}
      <div className="bg-white rounded-lg border p-4">
        <div className="flex gap-2 flex-wrap">
          {(["all", "pending", "approved", "rejected", "expired"] as const).map(
            (s) => (
              <button
                key={s}
                onClick={() => setFilterStatus(s)}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  filterStatus === s
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {s === "all" ? "すべて" : STATUS_CONFIG[s].label}
              </button>
            ),
          )}
        </div>
      </div>

      {/* 文書テーブル */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  文書番号
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  文書名
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  種別
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  提出者
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  提出日
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  承認フロー
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  期限
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  ステータス
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filtered.map((doc) => (
                <tr key={doc.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs text-gray-600">
                    {doc.docNumber}
                  </td>
                  <td className="px-4 py-3 font-medium text-gray-900">
                    {doc.docName}
                  </td>
                  <td className="px-4 py-3 text-gray-600">{doc.docType}</td>
                  <td className="px-4 py-3 text-gray-600">{doc.submitter}</td>
                  <td className="px-4 py-3 text-gray-600">
                    {doc.submittedDate}
                  </td>
                  <td className="px-4 py-3 text-gray-600 text-xs">
                    {doc.approvalStage}
                  </td>
                  <td className="px-4 py-3 text-gray-600">{doc.deadline}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_CONFIG[doc.status].className}`}
                    >
                      {STATUS_CONFIG[doc.status].label}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {doc.status === "pending" && (
                      <div className="flex gap-1">
                        <button
                          onClick={() => handleApprove(doc.id)}
                          className="px-2 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700"
                        >
                          承認
                        </button>
                        <button
                          onClick={() => handleReject(doc.id)}
                          className="px-2 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700"
                        >
                          差戻
                        </button>
                        <button className="px-2 py-1 bg-gray-200 text-gray-700 text-xs rounded hover:bg-gray-300 flex items-center gap-1">
                          <MessageSquare className="w-3 h-3" />
                          コメント
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
