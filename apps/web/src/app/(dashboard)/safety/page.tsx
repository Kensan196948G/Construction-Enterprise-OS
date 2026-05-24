"use client";

import { useState, useEffect, useCallback } from "react";
import {
  ShieldAlert,
  AlertTriangle,
  ClipboardCheck,
  FileWarning,
  CheckCircle2,
  XCircle,
  Clock,
  Plus,
} from "lucide-react";

interface InspectionStats {
  total: number;
  passed: number;
  failed: number;
  pending: number;
  pass_rate: number;
}

interface Hazard {
  id: string;
  title: string;
  hazard_type: string;
  risk_level: string;
  severity: string;
  status: string;
  location: string | null;
  created_at: string | null;
}

interface Incident {
  id: string;
  title: string;
  incident_type: string;
  severity: string;
  status: string;
  occurred_at: string | null;
  created_at: string | null;
}

interface Inspection {
  id: string;
  title: string;
  inspection_type: string;
  status: string;
  score: number | null;
  is_safe: boolean | null;
  inspection_date: string | null;
}

const MOCK_STATS: InspectionStats = {
  total: 48,
  passed: 41,
  failed: 4,
  pending: 3,
  pass_rate: 91.1,
};

const MOCK_HAZARDS: Hazard[] = [
  {
    id: "h1",
    title: "足場の手すり不備（第3工区）",
    hazard_type: "fall",
    risk_level: "high",
    severity: "serious",
    status: "open",
    location: "品川タワー新築工事 3F",
    created_at: "2026-05-24T08:00:00Z",
  },
  {
    id: "h2",
    title: "クレーン旋回範囲内への作業員立入",
    hazard_type: "equipment",
    risk_level: "critical",
    severity: "critical",
    status: "open",
    location: "川崎物流センター建設",
    created_at: "2026-05-23T14:30:00Z",
  },
  {
    id: "h3",
    title: "掘削箇所の土砂崩れリスク",
    hazard_type: "ground",
    risk_level: "medium",
    severity: "moderate",
    status: "in_progress",
    location: "大田区道路改良工事",
    created_at: "2026-05-22T10:00:00Z",
  },
];

const MOCK_INCIDENTS: Incident[] = [
  {
    id: "i1",
    title: "作業員 軽傷（転倒）",
    incident_type: "injury",
    severity: "minor",
    status: "investigating",
    occurred_at: "2026-05-23T09:15:00Z",
    created_at: "2026-05-23T09:30:00Z",
  },
  {
    id: "i2",
    title: "資材落下ヒヤリハット",
    incident_type: "near_miss",
    severity: "moderate",
    status: "resolved",
    occurred_at: "2026-05-22T15:00:00Z",
    created_at: "2026-05-22T15:20:00Z",
  },
  {
    id: "i3",
    title: "熱中症疑い（軽症）",
    incident_type: "illness",
    severity: "minor",
    status: "resolved",
    occurred_at: "2026-05-21T13:45:00Z",
    created_at: "2026-05-21T14:00:00Z",
  },
];

const MOCK_INSPECTIONS: Inspection[] = [
  {
    id: "insp1",
    title: "週次安全パトロール",
    inspection_type: "patrol",
    status: "passed",
    score: 94,
    is_safe: true,
    inspection_date: "2026-05-23",
  },
  {
    id: "insp2",
    title: "足場設備点検",
    inspection_type: "equipment",
    status: "failed",
    score: 62,
    is_safe: false,
    inspection_date: "2026-05-22",
  },
  {
    id: "insp3",
    title: "消火設備定期点検",
    inspection_type: "fire_safety",
    status: "passed",
    score: 100,
    is_safe: true,
    inspection_date: "2026-05-20",
  },
];

const riskLevelStyle: Record<string, { label: string; className: string }> = {
  critical: { label: "最高リスク", className: "bg-red-100 text-red-700 border-red-200" },
  high: { label: "高リスク", className: "bg-orange-100 text-orange-700 border-orange-200" },
  medium: { label: "中リスク", className: "bg-yellow-100 text-yellow-700 border-yellow-200" },
  low: { label: "低リスク", className: "bg-green-100 text-green-700 border-green-200" },
};

const incidentSeverityStyle: Record<string, { label: string; className: string }> = {
  critical: { label: "重大", className: "bg-red-100 text-red-700" },
  serious: { label: "深刻", className: "bg-orange-100 text-orange-700" },
  moderate: { label: "中程度", className: "bg-yellow-100 text-yellow-700" },
  minor: { label: "軽微", className: "bg-green-100 text-green-700" },
};

const incidentStatusStyle: Record<string, { label: string; className: string }> = {
  open: { label: "未対応", className: "bg-red-50 text-red-700" },
  investigating: { label: "調査中", className: "bg-yellow-50 text-yellow-700" },
  resolved: { label: "解決済", className: "bg-green-50 text-green-700" },
  closed: { label: "クローズ", className: "bg-gray-100 text-gray-600" },
};

function formatDate(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, "0")}/${String(d.getDate()).padStart(2, "0")}`;
}

export default function SafetyPage() {
  const [stats, setStats] = useState<InspectionStats>(MOCK_STATS);
  const [hazards, setHazards] = useState<Hazard[]>(MOCK_HAZARDS);
  const [incidents, setIncidents] = useState<Incident[]>(MOCK_INCIDENTS);
  const [inspections, setInspections] = useState<Inspection[]>(MOCK_INSPECTIONS);

  const loadSafetyData = useCallback(async () => {
    const [statsRes, hazardsRes, incidentsRes, inspectionsRes] =
      await Promise.allSettled([
        fetch("/api/v1/safety/inspections/stats").then((r) =>
          r.ok ? r.json() : null,
        ),
        fetch("/api/v1/safety/hazards/open").then((r) =>
          r.ok ? r.json() : null,
        ),
        fetch("/api/v1/safety/incidents?limit=10").then((r) =>
          r.ok ? r.json() : null,
        ),
        fetch("/api/v1/safety/inspections?limit=5").then((r) =>
          r.ok ? r.json() : null,
        ),
      ]);

    if (
      statsRes.status === "fulfilled" &&
      statsRes.value?.data &&
      typeof statsRes.value.data.total === "number"
    ) {
      setStats(statsRes.value.data as InspectionStats);
    }

    if (
      hazardsRes.status === "fulfilled" &&
      Array.isArray(hazardsRes.value?.data)
    ) {
      setHazards(hazardsRes.value.data as Hazard[]);
    }

    if (
      incidentsRes.status === "fulfilled" &&
      Array.isArray(incidentsRes.value?.data)
    ) {
      setIncidents(incidentsRes.value.data as Incident[]);
    }

    if (
      inspectionsRes.status === "fulfilled" &&
      Array.isArray(inspectionsRes.value?.data)
    ) {
      setInspections(inspectionsRes.value.data as Inspection[]);
    }
  }, []);

  useEffect(() => {
    loadSafetyData();
  }, [loadSafetyData]);

  const statCards = [
    {
      label: "未解決ヒヤリハット",
      value: hazards.filter((h) => h.status === "open" || h.status === "in_progress").length,
      icon: FileWarning,
      color: "danger",
      note: "要対応",
    },
    {
      label: "直近インシデント",
      value: incidents.filter((i) => i.status !== "closed").length,
      icon: AlertTriangle,
      color: "safety",
      note: "今月",
    },
    {
      label: "点検合格率",
      value: `${stats.pass_rate.toFixed(1)}%`,
      icon: ClipboardCheck,
      color: "approve",
      note: `${stats.passed}/${stats.total} 合格`,
    },
    {
      label: "安全パトロール",
      value: stats.pending,
      icon: ShieldAlert,
      color: "primary",
      note: "未実施",
    },
  ];

  const colorMap: Record<string, { bg: string; icon: string }> = {
    primary: { bg: "bg-primary-50", icon: "text-primary-500" },
    safety: { bg: "bg-safety-50", icon: "text-safety-500" },
    danger: { bg: "bg-danger-50", icon: "text-danger-500" },
    approve: { bg: "bg-approve-50", icon: "text-approve-500" },
  };

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">安全管理</h1>
          <p className="mt-1 text-gray-500 text-sm">
            ヒヤリハット・インシデント・安全点検の一元管理
          </p>
        </div>
        <div className="flex gap-2">
          <button className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
            <ClipboardCheck className="h-4 w-4" />
            点検記録
          </button>
          <button className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-700 transition-colors">
            <Plus className="h-4 w-4" />
            報告登録
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card) => {
          const Icon = card.icon;
          const colors = colorMap[card.color];
          return (
            <div
              key={card.label}
              className="rounded-xl border border-gray-200 bg-white p-5 hover:shadow-md transition-shadow"
            >
              <div className={`inline-flex rounded-lg p-2.5 ${colors.bg}`}>
                <Icon className={`h-5 w-5 ${colors.icon}`} />
              </div>
              <p className="mt-4 text-3xl font-bold text-gray-900">
                {card.value}
              </p>
              <p className="mt-1 text-sm font-medium text-gray-600">
                {card.label}
              </p>
              <p className="mt-2 text-xs text-gray-400">{card.note}</p>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hazard Reports */}
        <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
          <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
            <h2 className="font-bold text-gray-900 flex items-center gap-2">
              <FileWarning className="h-4 w-4 text-danger-500" />
              ヒヤリハット報告
            </h2>
            <span className="text-xs text-gray-500">未解決 {hazards.filter(h => h.status !== "resolved" && h.status !== "closed").length}件</span>
          </div>
          <div className="divide-y divide-gray-100">
            {hazards.length === 0 ? (
              <div className="px-5 py-8 text-center text-sm text-gray-400">
                未解決の報告はありません
              </div>
            ) : (
              hazards.map((hazard) => {
                const risk = riskLevelStyle[hazard.risk_level] ?? riskLevelStyle.medium;
                return (
                  <div
                    key={hazard.id}
                    className="px-5 py-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-900 truncate">
                          {hazard.title}
                        </p>
                        {hazard.location && (
                          <p className="text-xs text-gray-500 mt-0.5">
                            📍 {hazard.location}
                          </p>
                        )}
                        <p className="text-xs text-gray-400 mt-0.5">
                          {formatDate(hazard.created_at)}
                        </p>
                      </div>
                      <span
                        className={`flex-shrink-0 rounded-full border px-2.5 py-0.5 text-xs font-medium ${risk.className}`}
                      >
                        {risk.label}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Incident Reports */}
        <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
          <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
            <h2 className="font-bold text-gray-900 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-safety-500" />
              インシデント報告
            </h2>
            <span className="text-xs text-gray-500">直近 {incidents.length}件</span>
          </div>
          <div className="divide-y divide-gray-100">
            {incidents.length === 0 ? (
              <div className="px-5 py-8 text-center text-sm text-gray-400">
                インシデント報告はありません
              </div>
            ) : (
              incidents.map((incident) => {
                const severity =
                  incidentSeverityStyle[incident.severity] ??
                  incidentSeverityStyle.minor;
                const statusInfo =
                  incidentStatusStyle[incident.status] ??
                  incidentStatusStyle.open;
                return (
                  <div
                    key={incident.id}
                    className="px-5 py-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-900 truncate">
                          {incident.title}
                        </p>
                        <p className="text-xs text-gray-400 mt-0.5">
                          {formatDate(incident.occurred_at)}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <span
                            className={`rounded px-1.5 py-0.5 text-xs font-medium ${severity.className}`}
                          >
                            {severity.label}
                          </span>
                          <span
                            className={`rounded px-1.5 py-0.5 text-xs font-medium ${statusInfo.className}`}
                          >
                            {statusInfo.label}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* Inspections */}
      <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <h2 className="font-bold text-gray-900 flex items-center gap-2">
            <ClipboardCheck className="h-4 w-4 text-approve-500" />
            安全点検記録
          </h2>
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <CheckCircle2 className="h-3.5 w-3.5 text-approve-500" />
              合格 {stats.passed}
            </span>
            <span className="flex items-center gap-1">
              <XCircle className="h-3.5 w-3.5 text-danger-500" />
              不合格 {stats.failed}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="h-3.5 w-3.5 text-gray-400" />
              未実施 {stats.pending}
            </span>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50/50">
                <th className="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  点検名
                </th>
                <th className="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  種別
                </th>
                <th className="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  点検日
                </th>
                <th className="px-5 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  スコア
                </th>
                <th className="px-5 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  結果
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {inspections.map((insp) => (
                <tr key={insp.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-5 py-3.5 font-medium text-gray-900">
                    {insp.title}
                  </td>
                  <td className="px-5 py-3.5 text-gray-600">
                    {insp.inspection_type}
                  </td>
                  <td className="px-5 py-3.5 text-gray-500">
                    {formatDate(insp.inspection_date)}
                  </td>
                  <td className="px-5 py-3.5 text-center">
                    {insp.score != null ? (
                      <span
                        className={`font-semibold ${
                          insp.score >= 80
                            ? "text-approve-600"
                            : insp.score >= 60
                              ? "text-safety-600"
                              : "text-danger-600"
                        }`}
                      >
                        {insp.score}
                      </span>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>
                  <td className="px-5 py-3.5 text-center">
                    {insp.status === "passed" || insp.is_safe === true ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-approve-50 px-2.5 py-0.5 text-xs font-medium text-approve-700">
                        <CheckCircle2 className="h-3 w-3" />
                        合格
                      </span>
                    ) : insp.status === "failed" || insp.is_safe === false ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-danger-50 px-2.5 py-0.5 text-xs font-medium text-danger-700">
                        <XCircle className="h-3 w-3" />
                        不合格
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600">
                        <Clock className="h-3 w-3" />
                        未実施
                      </span>
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
