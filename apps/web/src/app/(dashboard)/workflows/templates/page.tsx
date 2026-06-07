"use client";

import { useState } from "react";
import { Copy, Users, CheckSquare, FileText } from "lucide-react";

interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  stepCount: number;
  usageCount: number;
  lastUpdated: string;
  approvers: string[];
}

const MOCK_TEMPLATES: WorkflowTemplate[] = [
  {
    id: "t01",
    name: "購買承認フロー",
    description:
      "材料・備品の購入申請を担当者→課長→部長の3段階で承認するフローです。50万円超は役員承認が追加されます。",
    category: "購買承認",
    stepCount: 3,
    usageCount: 124,
    lastUpdated: "2026-05-01",
    approvers: ["担当者", "課長", "部長"],
  },
  {
    id: "t02",
    name: "工事変更承認フロー",
    description:
      "施工中の工事内容変更申請。設計担当→工事部長→発注者確認の流れで進め、変更内容の記録を自動生成します。",
    category: "工事変更",
    stepCount: 4,
    usageCount: 87,
    lastUpdated: "2026-04-20",
    approvers: ["設計担当", "工事部長", "品質管理", "発注者"],
  },
  {
    id: "t03",
    name: "経費精算フロー",
    description:
      "交通費・出張費・備品購入費などの経費精算申請。領収書添付必須。上長承認後に経理処理へ自動連携されます。",
    category: "経費精算",
    stepCount: 2,
    usageCount: 210,
    lastUpdated: "2026-05-10",
    approvers: ["直属上長", "経理部"],
  },
  {
    id: "t04",
    name: "設計変更承認フロー",
    description:
      "図面・仕様書の変更申請。設計責任者→品質管理→工事監理の順で承認し、変更履歴を自動記録します。",
    category: "設計変更",
    stepCount: 3,
    usageCount: 56,
    lastUpdated: "2026-04-15",
    approvers: ["設計責任者", "品質管理", "工事監理"],
  },
  {
    id: "t05",
    name: "採用申請フロー",
    description:
      "新規採用・契約社員・パートタイム採用の申請。部門長→人事部→役員の承認後、採用手続きへ移行します。",
    category: "採用申請",
    stepCount: 4,
    usageCount: 33,
    lastUpdated: "2026-03-28",
    approvers: ["部門長", "人事部長", "管理部", "役員"],
  },
  {
    id: "t06",
    name: "外注発注承認フロー",
    description:
      "専門工事業者への外注発注申請。見積書添付必須。工事部→調達部→部長の承認後、発注書を自動発行します。",
    category: "外注承認",
    stepCount: 3,
    usageCount: 72,
    lastUpdated: "2026-05-05",
    approvers: ["工事担当", "調達部", "工事部長"],
  },
];

const categoryColors: Record<string, string> = {
  購買承認: "bg-blue-100 text-blue-700",
  工事変更: "bg-orange-100 text-orange-700",
  経費精算: "bg-green-100 text-green-700",
  設計変更: "bg-purple-100 text-purple-700",
  採用申請: "bg-pink-100 text-pink-700",
  外注承認: "bg-yellow-100 text-yellow-700",
};

export default function TemplatesPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const totalUsage = MOCK_TEMPLATES.reduce((s, t) => s + t.usageCount, 0);
  const avgSteps = Math.round(
    MOCK_TEMPLATES.reduce((s, t) => s + t.stepCount, 0) / MOCK_TEMPLATES.length,
  );

  const stats = [
    {
      label: "テンプレート数",
      value: MOCK_TEMPLATES.length,
      icon: FileText,
      colorBg: "bg-blue-50",
      colorIcon: "text-blue-500",
    },
    {
      label: "総使用回数",
      value: totalUsage,
      icon: Copy,
      colorBg: "bg-green-50",
      colorIcon: "text-green-500",
    },
    {
      label: "平均承認ステップ",
      value: `${avgSteps}段階`,
      icon: CheckSquare,
      colorBg: "bg-purple-50",
      colorIcon: "text-purple-500",
    },
    {
      label: "カテゴリ数",
      value: new Set(MOCK_TEMPLATES.map((t) => t.category)).size,
      icon: Users,
      colorBg: "bg-yellow-50",
      colorIcon: "text-yellow-500",
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            ワークフローテンプレート
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            申請ワークフローのテンプレートを選択して申請を開始できます
          </p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
          <FileText className="h-4 w-4" />
          テンプレート作成
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

      {/* Template Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {MOCK_TEMPLATES.map((tmpl) => {
          const catColor =
            categoryColors[tmpl.category] ?? "bg-gray-100 text-gray-600";
          return (
            <div
              key={tmpl.id}
              className="rounded-xl border border-gray-200 bg-white p-5 hover:shadow-md transition-shadow flex flex-col gap-4"
            >
              {/* Card Header */}
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="font-bold text-gray-900">{tmpl.name}</h3>
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${catColor}`}
                    >
                      {tmpl.category}
                    </span>
                  </div>
                  <p className="mt-1.5 text-sm text-gray-500 leading-relaxed">
                    {tmpl.description}
                  </p>
                </div>
              </div>

              {/* Approver Steps */}
              <div className="flex items-center gap-1 flex-wrap">
                {tmpl.approvers.map((approver, idx) => (
                  <span key={idx} className="flex items-center gap-1">
                    <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-700">
                      {approver}
                    </span>
                    {idx < tmpl.approvers.length - 1 && (
                      <span className="text-gray-300 text-xs">→</span>
                    )}
                  </span>
                ))}
              </div>

              {/* Meta */}
              <div className="flex items-center gap-4 text-xs text-gray-400 border-t border-gray-100 pt-3">
                <span className="flex items-center gap-1">
                  <CheckSquare className="h-3.5 w-3.5" />
                  {tmpl.stepCount} ステップ
                </span>
                <span className="flex items-center gap-1">
                  <Copy className="h-3.5 w-3.5" />
                  使用 {tmpl.usageCount} 回
                </span>
                <span className="ml-auto">最終更新: {tmpl.lastUpdated}</span>
              </div>

              {/* Action */}
              <button
                onClick={() => setSelectedId(tmpl.id)}
                className="w-full rounded-lg bg-blue-600 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 transition-colors"
              >
                このテンプレートで申請
              </button>
            </div>
          );
        })}
      </div>

      {/* Confirmation Modal */}
      {selectedId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
            {(() => {
              const tmpl = MOCK_TEMPLATES.find((t) => t.id === selectedId)!;
              return (
                <>
                  <h3 className="text-lg font-bold text-gray-900 mb-1">
                    申請を開始しますか？
                  </h3>
                  <p className="text-sm text-gray-500 mb-4">
                    テンプレート:{" "}
                    <span className="font-semibold text-gray-700">
                      {tmpl.name}
                    </span>
                  </p>
                  <div className="rounded-lg bg-gray-50 p-4 space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">カテゴリ</span>
                      <span className="font-medium text-gray-700">
                        {tmpl.category}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">承認ステップ数</span>
                      <span className="font-medium text-gray-700">
                        {tmpl.stepCount} 段階
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">承認ルート</span>
                      <span className="font-medium text-gray-700">
                        {tmpl.approvers.join(" → ")}
                      </span>
                    </div>
                  </div>
                  <div className="mt-5 flex justify-end gap-3">
                    <button
                      onClick={() => setSelectedId(null)}
                      className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      キャンセル
                    </button>
                    <button
                      onClick={() => setSelectedId(null)}
                      className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 transition-colors"
                    >
                      申請フォームへ進む
                    </button>
                  </div>
                </>
              );
            })()}
          </div>
        </div>
      )}
    </div>
  );
}
