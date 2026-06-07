"use client";

import { useState } from "react";
import { Shield, CheckCircle, FileCheck, Building } from "lucide-react";

type ComplianceStatus =
  | "compliant"
  | "partial"
  | "non_compliant"
  | "not_applicable";

interface IsmsControl {
  id: string;
  controlId: string;
  name: string;
  category: string;
  status: ComplianceStatus;
  lastAssessedAt: string;
  owner: string;
}

const MOCK_CONTROLS: IsmsControl[] = [
  {
    id: "c01",
    controlId: "A.5.1",
    name: "情報セキュリティのための方針群",
    category: "A5情報セキュリティ方針",
    status: "compliant",
    lastAssessedAt: "2026-04-15",
    owner: "田中 太郎",
  },
  {
    id: "c02",
    controlId: "A.5.2",
    name: "情報セキュリティの役割及び責任",
    category: "A5情報セキュリティ方針",
    status: "compliant",
    lastAssessedAt: "2026-04-15",
    owner: "田中 太郎",
  },
  {
    id: "c03",
    controlId: "A.6.1",
    name: "内部組織",
    category: "A6組織",
    status: "compliant",
    lastAssessedAt: "2026-04-20",
    owner: "佐藤 花子",
  },
  {
    id: "c04",
    controlId: "A.6.2",
    name: "モバイル機器及びテレワーキング",
    category: "A6組織",
    status: "partial",
    lastAssessedAt: "2026-04-20",
    owner: "佐藤 花子",
  },
  {
    id: "c05",
    controlId: "A.8.1",
    name: "資産に対する責任",
    category: "A8資産",
    status: "compliant",
    lastAssessedAt: "2026-04-22",
    owner: "山田 健一",
  },
  {
    id: "c06",
    controlId: "A.8.2",
    name: "情報の分類",
    category: "A8資産",
    status: "partial",
    lastAssessedAt: "2026-04-22",
    owner: "山田 健一",
  },
  {
    id: "c07",
    controlId: "A.9.1",
    name: "アクセス制御に対するビジネス上の要求事項",
    category: "A9アクセス制御",
    status: "compliant",
    lastAssessedAt: "2026-05-01",
    owner: "鈴木 美咲",
  },
  {
    id: "c08",
    controlId: "A.9.2",
    name: "利用者アクセスの管理",
    category: "A9アクセス制御",
    status: "compliant",
    lastAssessedAt: "2026-05-01",
    owner: "鈴木 美咲",
  },
  {
    id: "c09",
    controlId: "A.9.4",
    name: "システム及びアプリケーションのアクセス制御",
    category: "A9アクセス制御",
    status: "non_compliant",
    lastAssessedAt: "2026-05-01",
    owner: "鈴木 美咲",
  },
  {
    id: "c10",
    controlId: "A.10.1",
    name: "暗号化管理策",
    category: "A10暗号化",
    status: "partial",
    lastAssessedAt: "2026-05-05",
    owner: "伊藤 大輔",
  },
  {
    id: "c11",
    controlId: "A.12.1",
    name: "運用手順及び責任",
    category: "A12運用",
    status: "compliant",
    lastAssessedAt: "2026-05-10",
    owner: "高橋 良子",
  },
  {
    id: "c12",
    controlId: "A.12.6",
    name: "技術的ぜい弱性の管理",
    category: "A12運用",
    status: "non_compliant",
    lastAssessedAt: "2026-05-10",
    owner: "高橋 良子",
  },
];

const statusMap: Record<
  ComplianceStatus,
  { label: string; className: string }
> = {
  compliant: { label: "遵守", className: "bg-green-100 text-green-700" },
  partial: { label: "部分遵守", className: "bg-yellow-100 text-yellow-700" },
  non_compliant: { label: "非遵守", className: "bg-red-100 text-red-700" },
  not_applicable: {
    label: "対象外",
    className: "bg-gray-100 text-gray-500",
  },
};

const CATEGORIES = [
  "すべて",
  "A5情報セキュリティ方針",
  "A6組織",
  "A8資産",
  "A9アクセス制御",
  "A10暗号化",
  "A12運用",
];

export default function IsmsPage() {
  const [filterCategory, setFilterCategory] = useState("すべて");

  const compliantCount = MOCK_CONTROLS.filter(
    (c) => c.status === "compliant",
  ).length;
  const partialCount = MOCK_CONTROLS.filter(
    (c) => c.status === "partial",
  ).length;
  const nonCompliantCount = MOCK_CONTROLS.filter(
    (c) => c.status === "non_compliant",
  ).length;
  const applicableCount = MOCK_CONTROLS.filter(
    (c) => c.status !== "not_applicable",
  ).length;
  const complianceRate =
    applicableCount > 0
      ? Math.round((compliantCount / applicableCount) * 100)
      : 0;

  const filtered = MOCK_CONTROLS.filter(
    (c) => filterCategory === "すべて" || c.category === filterCategory,
  );

  const stats = [
    {
      label: "遵守率",
      value: `${complianceRate}%`,
      icon: Shield,
      colorBg: "bg-blue-50",
      colorIcon: "text-blue-500",
    },
    {
      label: "完全遵守",
      value: compliantCount,
      icon: CheckCircle,
      colorBg: "bg-green-50",
      colorIcon: "text-green-500",
    },
    {
      label: "部分遵守",
      value: partialCount,
      icon: FileCheck,
      colorBg: "bg-yellow-50",
      colorIcon: "text-yellow-500",
    },
    {
      label: "非遵守",
      value: nonCompliantCount,
      icon: Building,
      colorBg: "bg-red-50",
      colorIcon: "text-red-500",
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">ISMS管理</h1>
          <p className="mt-1 text-sm text-gray-500">
            ISO 27001 情報セキュリティマネジメントシステム遵守状況
          </p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
          <FileCheck className="h-4 w-4" />
          評価レポート出力
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

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setFilterCategory(cat)}
            className={`rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${
              filterCategory === cat
                ? "bg-blue-600 text-white"
                : "bg-white border border-gray-200 text-gray-600 hover:bg-gray-50"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
        <div className="flex items-center gap-2 px-5 py-4 border-b border-gray-100">
          <Shield className="h-4 w-4 text-blue-500" />
          <h2 className="font-bold text-gray-900">ISMSコントロール遵守状況</h2>
          <span className="ml-auto text-xs text-gray-500">
            {filtered.length} 件
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50/50">
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  コントロールID
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  管理策名
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  カテゴリ
                </th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  実施状況
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  最終評価日
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  担当者
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((ctrl) => {
                const st = statusMap[ctrl.status];
                return (
                  <tr
                    key={ctrl.id}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-4 py-3 font-mono text-xs font-semibold text-gray-700">
                      {ctrl.controlId}
                    </td>
                    <td className="px-4 py-3 font-medium text-gray-900">
                      {ctrl.name}
                    </td>
                    <td className="px-4 py-3 text-gray-600 text-xs">
                      {ctrl.category}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${st.className}`}
                      >
                        {st.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-500">
                      {ctrl.lastAssessedAt}
                    </td>
                    <td className="px-4 py-3 text-gray-600">{ctrl.owner}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
