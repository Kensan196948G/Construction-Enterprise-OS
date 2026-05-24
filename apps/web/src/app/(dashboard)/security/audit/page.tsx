"use client";

import { useState } from "react";
import { Shield, Eye, Activity, AlertTriangle } from "lucide-react";

type EventType =
  | "login"
  | "logout"
  | "data_access"
  | "config_change"
  | "permission_change";
type ResultType = "success" | "failure" | "warning";

interface AuditLog {
  id: string;
  datetime: string;
  user: string;
  eventType: EventType;
  resource: string;
  ipAddress: string;
  result: ResultType;
}

const MOCK_LOGS: AuditLog[] = [
  {
    id: "al001",
    datetime: "2026-05-24T09:12:00Z",
    user: "田中 太郎",
    eventType: "login",
    resource: "認証システム",
    ipAddress: "192.168.1.10",
    result: "success",
  },
  {
    id: "al002",
    datetime: "2026-05-24T09:15:33Z",
    user: "佐藤 花子",
    eventType: "data_access",
    resource: "工事台帳DB",
    ipAddress: "192.168.1.22",
    result: "success",
  },
  {
    id: "al003",
    datetime: "2026-05-24T09:30:11Z",
    user: "不明",
    eventType: "login",
    resource: "認証システム",
    ipAddress: "203.0.113.45",
    result: "failure",
  },
  {
    id: "al004",
    datetime: "2026-05-24T09:45:00Z",
    user: "山田 健一",
    eventType: "config_change",
    resource: "メール通知設定",
    ipAddress: "192.168.1.31",
    result: "success",
  },
  {
    id: "al005",
    datetime: "2026-05-24T10:02:44Z",
    user: "鈴木 美咲",
    eventType: "permission_change",
    resource: "ユーザー権限管理",
    ipAddress: "192.168.1.15",
    result: "warning",
  },
  {
    id: "al006",
    datetime: "2026-05-24T10:18:09Z",
    user: "不明",
    eventType: "login",
    resource: "認証システム",
    ipAddress: "198.51.100.77",
    result: "failure",
  },
  {
    id: "al007",
    datetime: "2026-05-24T10:33:22Z",
    user: "伊藤 大輔",
    eventType: "data_access",
    resource: "財務レポート",
    ipAddress: "192.168.1.40",
    result: "success",
  },
  {
    id: "al008",
    datetime: "2026-05-24T10:50:55Z",
    user: "高橋 良子",
    eventType: "logout",
    resource: "認証システム",
    ipAddress: "192.168.1.22",
    result: "success",
  },
  {
    id: "al009",
    datetime: "2026-05-24T11:05:30Z",
    user: "渡辺 浩二",
    eventType: "config_change",
    resource: "セキュリティポリシー",
    ipAddress: "192.168.1.50",
    result: "warning",
  },
  {
    id: "al010",
    datetime: "2026-05-24T11:20:17Z",
    user: "不明",
    eventType: "login",
    resource: "認証システム",
    ipAddress: "203.0.113.99",
    result: "failure",
  },
  {
    id: "al011",
    datetime: "2026-05-24T11:35:48Z",
    user: "中村 恵子",
    eventType: "data_access",
    resource: "個人情報DB",
    ipAddress: "192.168.1.28",
    result: "success",
  },
  {
    id: "al012",
    datetime: "2026-05-24T11:50:03Z",
    user: "小林 誠",
    eventType: "permission_change",
    resource: "API アクセス権限",
    ipAddress: "192.168.1.33",
    result: "success",
  },
  {
    id: "al013",
    datetime: "2026-05-24T12:10:21Z",
    user: "加藤 裕子",
    eventType: "data_access",
    resource: "契約書類ストレージ",
    ipAddress: "192.168.1.19",
    result: "success",
  },
  {
    id: "al014",
    datetime: "2026-05-24T12:25:38Z",
    user: "松本 一郎",
    eventType: "config_change",
    resource: "バックアップ設定",
    ipAddress: "192.168.1.55",
    result: "success",
  },
  {
    id: "al015",
    datetime: "2026-05-24T12:40:59Z",
    user: "林 明美",
    eventType: "login",
    resource: "認証システム",
    ipAddress: "192.168.1.62",
    result: "success",
  },
];

const eventTypeMap: Record<EventType, { label: string; className: string }> = {
  login: { label: "ログイン", className: "bg-blue-100 text-blue-700" },
  logout: { label: "ログアウト", className: "bg-gray-100 text-gray-600" },
  data_access: {
    label: "データアクセス",
    className: "bg-purple-100 text-purple-700",
  },
  config_change: {
    label: "設定変更",
    className: "bg-orange-100 text-orange-700",
  },
  permission_change: {
    label: "権限変更",
    className: "bg-yellow-100 text-yellow-700",
  },
};

const resultMap: Record<ResultType, { label: string; className: string }> = {
  success: { label: "成功", className: "bg-green-100 text-green-700" },
  failure: { label: "失敗", className: "bg-red-100 text-red-700" },
  warning: { label: "警告", className: "bg-yellow-100 text-yellow-700" },
};

function formatDatetime(iso: string): string {
  const d = new Date(iso);
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, "0")}/${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}:${String(d.getSeconds()).padStart(2, "0")}`;
}

export default function AuditLogPage() {
  const [filterType, setFilterType] = useState<string>("all");
  const [filterResult, setFilterResult] = useState<string>("all");

  const todayLogins = MOCK_LOGS.filter(
    (l) => l.eventType === "login" && l.result === "success",
  ).length;
  const failedLogins = MOCK_LOGS.filter(
    (l) => l.eventType === "login" && l.result === "failure",
  ).length;
  const configChanges = MOCK_LOGS.filter(
    (l) => l.eventType === "config_change",
  ).length;
  const warnings = MOCK_LOGS.filter((l) => l.result === "warning").length;

  const filtered = MOCK_LOGS.filter((log) => {
    if (filterType !== "all" && log.eventType !== filterType) return false;
    if (filterResult !== "all" && log.result !== filterResult) return false;
    return true;
  });

  const stats = [
    {
      label: "今日のログイン数",
      value: todayLogins,
      icon: Eye,
      colorBg: "bg-blue-50",
      colorIcon: "text-blue-500",
    },
    {
      label: "失敗ログイン",
      value: failedLogins,
      icon: AlertTriangle,
      colorBg: "bg-red-50",
      colorIcon: "text-red-500",
    },
    {
      label: "設定変更数",
      value: configChanges,
      icon: Activity,
      colorBg: "bg-orange-50",
      colorIcon: "text-orange-500",
    },
    {
      label: "警告数",
      value: warnings,
      icon: Shield,
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
            セキュリティ監査ログ
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            システムへのアクセス・操作履歴の記録と監視
          </p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
          <Shield className="h-4 w-4" />
          ログエクスポート
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
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-300"
        >
          <option value="all">すべての種別</option>
          <option value="login">ログイン</option>
          <option value="logout">ログアウト</option>
          <option value="data_access">データアクセス</option>
          <option value="config_change">設定変更</option>
          <option value="permission_change">権限変更</option>
        </select>
        <select
          value={filterResult}
          onChange={(e) => setFilterResult(e.target.value)}
          className="rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-300"
        >
          <option value="all">すべての結果</option>
          <option value="success">成功</option>
          <option value="failure">失敗</option>
          <option value="warning">警告</option>
        </select>
        <span className="self-center text-sm text-gray-500">
          {filtered.length} 件表示
        </span>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
        <div className="flex items-center gap-2 px-5 py-4 border-b border-gray-100">
          <Activity className="h-4 w-4 text-blue-500" />
          <h2 className="font-bold text-gray-900">監査ログ一覧</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50/50">
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  日時
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  ユーザー
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  イベント種別
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  対象リソース
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  IPアドレス
                </th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  結果
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((log) => {
                const evStyle = eventTypeMap[log.eventType];
                const resStyle = resultMap[log.result];
                return (
                  <tr
                    key={log.id}
                    className={`hover:bg-gray-50 transition-colors ${log.result === "failure" ? "bg-red-50/30" : ""}`}
                  >
                    <td className="px-4 py-3 text-gray-600 whitespace-nowrap font-mono text-xs">
                      {formatDatetime(log.datetime)}
                    </td>
                    <td className="px-4 py-3 font-medium text-gray-900">
                      {log.user}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${evStyle.className}`}
                      >
                        {evStyle.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-600">{log.resource}</td>
                    <td className="px-4 py-3 text-gray-500 font-mono text-xs">
                      {log.ipAddress}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${resStyle.className}`}
                      >
                        {resStyle.label}
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
