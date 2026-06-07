"use client";

import { useState } from "react";
import { Bug, AlertCircle, Shield, CheckCircle } from "lucide-react";

type Severity = "critical" | "high" | "medium" | "low";
type VulnStatus = "open" | "in_progress" | "resolved" | "accepted";

interface Vulnerability {
  id: string;
  cveId: string;
  name: string;
  affectedSystem: string;
  severity: Severity;
  detectedAt: string;
  status: VulnStatus;
  resolvedAt: string | null;
}

const MOCK_VULNS: Vulnerability[] = [
  {
    id: "v01",
    cveId: "CVE-2026-1234",
    name: "OpenSSL バッファオーバーフロー",
    affectedSystem: "Webサーバー (nginx)",
    severity: "critical",
    detectedAt: "2026-05-01",
    status: "in_progress",
    resolvedAt: null,
  },
  {
    id: "v02",
    cveId: "CVE-2026-2345",
    name: "Node.js パストラバーサル脆弱性",
    affectedSystem: "APIサーバー",
    severity: "high",
    detectedAt: "2026-05-03",
    status: "open",
    resolvedAt: null,
  },
  {
    id: "v03",
    cveId: "CVE-2025-9876",
    name: "PostgreSQL 権限昇格",
    affectedSystem: "データベースサーバー",
    severity: "critical",
    detectedAt: "2026-04-28",
    status: "open",
    resolvedAt: null,
  },
  {
    id: "v04",
    cveId: "CVE-2026-3456",
    name: "React XSS 脆弱性",
    affectedSystem: "Webフロントエンド",
    severity: "high",
    detectedAt: "2026-05-10",
    status: "in_progress",
    resolvedAt: null,
  },
  {
    id: "v05",
    cveId: "CVE-2026-4567",
    name: "JWT 署名検証不備",
    affectedSystem: "認証システム",
    severity: "high",
    detectedAt: "2026-05-12",
    status: "open",
    resolvedAt: null,
  },
  {
    id: "v06",
    cveId: "CVE-2026-5678",
    name: "Redis 情報漏洩",
    affectedSystem: "キャッシュサーバー",
    severity: "medium",
    detectedAt: "2026-05-08",
    status: "resolved",
    resolvedAt: "2026-05-15",
  },
  {
    id: "v07",
    cveId: "CVE-2025-8765",
    name: "Docker 権限昇格",
    affectedSystem: "コンテナ基盤",
    severity: "medium",
    detectedAt: "2026-04-20",
    status: "resolved",
    resolvedAt: "2026-05-02",
  },
  {
    id: "v08",
    cveId: "CVE-2026-6789",
    name: "Apache Log4j 設定不備",
    affectedSystem: "ログ収集サーバー",
    severity: "medium",
    detectedAt: "2026-05-14",
    status: "accepted",
    resolvedAt: null,
  },
  {
    id: "v09",
    cveId: "CVE-2026-7890",
    name: "Linux カーネル情報漏洩",
    affectedSystem: "アプリケーションサーバー",
    severity: "low",
    detectedAt: "2026-05-16",
    status: "open",
    resolvedAt: null,
  },
  {
    id: "v10",
    cveId: "CVE-2026-8901",
    name: "curl SSRF 脆弱性",
    affectedSystem: "外部API連携モジュール",
    severity: "low",
    detectedAt: "2026-05-18",
    status: "resolved",
    resolvedAt: "2026-05-22",
  },
];

const severityMap: Record<Severity, { label: string; className: string }> = {
  critical: { label: "重大", className: "bg-red-100 text-red-700" },
  high: { label: "高", className: "bg-orange-100 text-orange-700" },
  medium: { label: "中", className: "bg-yellow-100 text-yellow-700" },
  low: { label: "低", className: "bg-green-100 text-green-700" },
};

const vulnStatusMap: Record<VulnStatus, { label: string; className: string }> =
  {
    open: { label: "未対応", className: "bg-red-50 text-red-700" },
    in_progress: {
      label: "対応中",
      className: "bg-blue-50 text-blue-700",
    },
    resolved: { label: "解決済", className: "bg-green-50 text-green-700" },
    accepted: {
      label: "受容済",
      className: "bg-gray-100 text-gray-600",
    },
  };

export default function VulnerabilitiesPage() {
  const [filterSeverity, setFilterSeverity] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");

  const openCritical = MOCK_VULNS.filter(
    (v) =>
      v.severity === "critical" &&
      v.status !== "resolved" &&
      v.status !== "accepted",
  ).length;
  const openHigh = MOCK_VULNS.filter(
    (v) =>
      v.severity === "high" &&
      v.status !== "resolved" &&
      v.status !== "accepted",
  ).length;
  const resolvedThisMonth = MOCK_VULNS.filter(
    (v) => v.resolvedAt && v.resolvedAt.startsWith("2026-05"),
  ).length;

  const totalResolved = MOCK_VULNS.filter((v) => v.status === "resolved");
  const avgDays =
    totalResolved.length > 0
      ? Math.round(
          totalResolved.reduce((sum, v) => {
            const diff =
              new Date(v.resolvedAt!).getTime() -
              new Date(v.detectedAt).getTime();
            return sum + diff / (1000 * 60 * 60 * 24);
          }, 0) / totalResolved.length,
        )
      : 0;

  const filtered = MOCK_VULNS.filter((v) => {
    if (filterSeverity !== "all" && v.severity !== filterSeverity) return false;
    if (filterStatus !== "all" && v.status !== filterStatus) return false;
    return true;
  });

  const stats = [
    {
      label: "未対応 Critical",
      value: openCritical,
      icon: Bug,
      colorBg: "bg-red-50",
      colorIcon: "text-red-500",
    },
    {
      label: "未対応 High",
      value: openHigh,
      icon: AlertCircle,
      colorBg: "bg-orange-50",
      colorIcon: "text-orange-500",
    },
    {
      label: "今月解決数",
      value: resolvedThisMonth,
      icon: CheckCircle,
      colorBg: "bg-green-50",
      colorIcon: "text-green-500",
    },
    {
      label: "平均対応日数",
      value: `${avgDays}日`,
      icon: Shield,
      colorBg: "bg-blue-50",
      colorIcon: "text-blue-500",
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">脆弱性管理</h1>
          <p className="mt-1 text-sm text-gray-500">
            システム脆弱性の検出・追跡・対応状況の管理
          </p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
          <Shield className="h-4 w-4" />
          脆弱性スキャン実行
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

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <select
          value={filterSeverity}
          onChange={(e) => setFilterSeverity(e.target.value)}
          className="rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-300"
        >
          <option value="all">すべての深刻度</option>
          <option value="critical">重大 (Critical)</option>
          <option value="high">高 (High)</option>
          <option value="medium">中 (Medium)</option>
          <option value="low">低 (Low)</option>
        </select>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-300"
        >
          <option value="all">すべての対応状況</option>
          <option value="open">未対応</option>
          <option value="in_progress">対応中</option>
          <option value="resolved">解決済</option>
          <option value="accepted">受容済</option>
        </select>
        <span className="self-center text-sm text-gray-500">
          {filtered.length} 件表示
        </span>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
        <div className="flex items-center gap-2 px-5 py-4 border-b border-gray-100">
          <Bug className="h-4 w-4 text-red-500" />
          <h2 className="font-bold text-gray-900">脆弱性一覧</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50/50">
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  CVE番号
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  脆弱性名
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  影響システム
                </th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  深刻度
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  検出日
                </th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  対応状況
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((vuln) => {
                const sev = severityMap[vuln.severity];
                const st = vulnStatusMap[vuln.status];
                return (
                  <tr
                    key={vuln.id}
                    className={`hover:bg-gray-50 transition-colors ${
                      vuln.severity === "critical" && vuln.status === "open"
                        ? "bg-red-50/30"
                        : ""
                    }`}
                  >
                    <td className="px-4 py-3 font-mono text-xs font-semibold text-gray-700">
                      {vuln.cveId}
                    </td>
                    <td className="px-4 py-3 font-medium text-gray-900">
                      {vuln.name}
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {vuln.affectedSystem}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${sev.className}`}
                      >
                        {sev.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-500">
                      {vuln.detectedAt}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${st.className}`}
                      >
                        {st.label}
                      </span>
                    </td>
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
