"use client";

import { Link, RefreshCw, CheckCircle, AlertCircle, Settings } from "lucide-react";

interface IntegrationSystem {
  id: string;
  name: string;
  category: string;
  iconBg: string;
  iconText: string;
  status: "connected" | "disconnected" | "error";
  lastSync: string | null;
  syncCount: number;
}

interface IntegrationLog {
  id: string;
  timestamp: string;
  systemName: string;
  event: string;
  result: "success" | "error" | "warning";
}

const MOCK_SYSTEMS: IntegrationSystem[] = [
  {
    id: "sys-kintone",
    name: "kintone",
    category: "業務アプリ",
    iconBg: "bg-blue-600",
    iconText: "K",
    status: "connected",
    lastSync: "2026-05-24 11:30",
    syncCount: 148,
  },
  {
    id: "sys-salesforce",
    name: "Salesforce",
    category: "CRM",
    iconBg: "bg-sky-500",
    iconText: "SF",
    status: "connected",
    lastSync: "2026-05-24 11:15",
    syncCount: 62,
  },
  {
    id: "sys-m365",
    name: "Microsoft 365",
    category: "コラボレーション",
    iconBg: "bg-orange-500",
    iconText: "M",
    status: "connected",
    lastSync: "2026-05-24 11:28",
    syncCount: 312,
  },
  {
    id: "sys-bim360",
    name: "Autodesk BIM 360",
    category: "BIM/CAD",
    iconBg: "bg-red-600",
    iconText: "BIM",
    status: "connected",
    lastSync: "2026-05-24 10:00",
    syncCount: 24,
  },
  {
    id: "sys-arcgis",
    name: "Esri ArcGIS",
    category: "GIS",
    iconBg: "bg-green-600",
    iconText: "GIS",
    status: "error",
    lastSync: "2026-05-23 18:00",
    syncCount: 0,
  },
  {
    id: "sys-sap",
    name: "SAP",
    category: "ERP",
    iconBg: "bg-indigo-600",
    iconText: "SAP",
    status: "disconnected",
    lastSync: null,
    syncCount: 0,
  },
  {
    id: "sys-lineworks",
    name: "LINE Works",
    category: "コミュニケーション",
    iconBg: "bg-teal-500",
    iconText: "LW",
    status: "connected",
    lastSync: "2026-05-24 11:29",
    syncCount: 89,
  },
  {
    id: "sys-slack",
    name: "Slack",
    category: "コミュニケーション",
    iconBg: "bg-purple-600",
    iconText: "SL",
    status: "connected",
    lastSync: "2026-05-24 11:30",
    syncCount: 204,
  },
];

const MOCK_LOGS: IntegrationLog[] = [
  {
    id: "log-001",
    timestamp: "2026-05-24 11:30:12",
    systemName: "kintone",
    event: "工事台帳データ同期完了",
    result: "success",
  },
  {
    id: "log-002",
    timestamp: "2026-05-24 11:29:45",
    systemName: "Slack",
    event: "安全アラート通知送信",
    result: "success",
  },
  {
    id: "log-003",
    timestamp: "2026-05-24 11:28:33",
    systemName: "Microsoft 365",
    event: "承認ワークフロー連携",
    result: "success",
  },
  {
    id: "log-004",
    timestamp: "2026-05-24 11:15:22",
    systemName: "Salesforce",
    event: "取引先情報更新",
    result: "success",
  },
  {
    id: "log-005",
    timestamp: "2026-05-24 10:45:18",
    systemName: "Esri ArcGIS",
    event: "GISデータ同期失敗",
    result: "error",
  },
  {
    id: "log-006",
    timestamp: "2026-05-24 10:00:05",
    systemName: "Autodesk BIM 360",
    event: "BIMモデルデータ取得",
    result: "success",
  },
  {
    id: "log-007",
    timestamp: "2026-05-24 09:55:40",
    systemName: "Esri ArcGIS",
    event: "認証トークン期限切れ",
    result: "error",
  },
  {
    id: "log-008",
    timestamp: "2026-05-24 09:30:10",
    systemName: "LINE Works",
    event: "日報通知送信",
    result: "success",
  },
];

const statusStyle: Record<IntegrationSystem["status"], { label: string; dot: string; badge: string }> = {
  connected: {
    label: "連携中",
    dot: "bg-green-500",
    badge: "bg-green-100 text-green-700",
  },
  disconnected: {
    label: "未接続",
    dot: "bg-gray-400",
    badge: "bg-gray-100 text-gray-600",
  },
  error: {
    label: "エラー",
    dot: "bg-red-500",
    badge: "bg-red-100 text-red-700",
  },
};

const logResultStyle: Record<IntegrationLog["result"], { icon: React.ReactNode; className: string }> = {
  success: {
    icon: <CheckCircle className="h-4 w-4 text-green-500" />,
    className: "text-green-700",
  },
  error: {
    icon: <AlertCircle className="h-4 w-4 text-red-500" />,
    className: "text-red-700",
  },
  warning: {
    icon: <AlertCircle className="h-4 w-4 text-yellow-500" />,
    className: "text-yellow-700",
  },
};

export default function IntegrationsPage() {
  const connectedCount = MOCK_SYSTEMS.filter((s) => s.status === "connected").length;
  const totalSyncToday = MOCK_SYSTEMS.reduce((s, sys) => s + sys.syncCount, 0);
  const errorCount = MOCK_SYSTEMS.filter((s) => s.status === "error").length;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">外部連携設定</h1>
        <p className="mt-1 text-sm text-gray-500">
          外部システムとのAPI連携状態を確認・管理します
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">連携中システム</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">
                {connectedCount}
                <span className="ml-1 text-lg font-medium text-gray-500">件</span>
              </p>
            </div>
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-green-50">
              <Link className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <p className="mt-2 text-xs text-gray-400">全{MOCK_SYSTEMS.length}システム中</p>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">今日の同期回数</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">
                {totalSyncToday.toLocaleString()}
                <span className="ml-1 text-lg font-medium text-gray-500">回</span>
              </p>
            </div>
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50">
              <RefreshCw className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <p className="mt-2 text-xs text-gray-400">全システム合計</p>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">エラー数</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">
                {errorCount}
                <span className="ml-1 text-lg font-medium text-gray-500">件</span>
              </p>
            </div>
            <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${errorCount > 0 ? "bg-red-50" : "bg-green-50"}`}>
              <AlertCircle className={`h-6 w-6 ${errorCount > 0 ? "text-red-600" : "text-green-600"}`} />
            </div>
          </div>
          <p className="mt-2 text-xs text-gray-400">接続エラーのシステム</p>
        </div>
      </div>

      {/* System Cards */}
      <div>
        <h2 className="mb-4 text-base font-semibold text-gray-900">連携システム一覧</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {MOCK_SYSTEMS.map((system) => {
            const st = statusStyle[system.status];
            return (
              <div key={system.id} className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`flex h-10 w-10 items-center justify-center rounded-lg text-white text-xs font-bold ${system.iconBg}`}>
                      {system.iconText}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-gray-900">{system.name}</p>
                      <p className="text-xs text-gray-500">{system.category}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className={`h-2 w-2 rounded-full ${st.dot}`} />
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${st.badge}`}>
                      {st.label}
                    </span>
                  </div>
                </div>
                <div className="mt-4 space-y-1.5">
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>最終同期</span>
                    <span className="font-medium text-gray-700">{system.lastSync ?? "—"}</span>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>今日の同期</span>
                    <span className="font-medium text-gray-700">{system.syncCount}回</span>
                  </div>
                </div>
                <div className="mt-4 flex gap-2">
                  <button className="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-gray-300 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50 transition-colors">
                    <Settings className="h-3.5 w-3.5" />
                    設定
                  </button>
                  {system.status === "connected" && (
                    <button className="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-blue-300 py-1.5 text-xs font-medium text-blue-600 hover:bg-blue-50 transition-colors">
                      <RefreshCw className="h-3.5 w-3.5" />
                      今すぐ同期
                    </button>
                  )}
                  {system.status !== "connected" && (
                    <button className="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-green-300 py-1.5 text-xs font-medium text-green-600 hover:bg-green-50 transition-colors">
                      <Link className="h-3.5 w-3.5" />
                      接続
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Integration Log */}
      <div className="rounded-xl border border-gray-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <div className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5 text-gray-500" />
            <h2 className="text-base font-semibold text-gray-900">連携ログ</h2>
          </div>
          <span className="text-sm text-gray-500">直近{MOCK_LOGS.length}件</span>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">日時</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">システム名</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">イベント</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">結果</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
              {MOCK_LOGS.map((log) => {
                const res = logResultStyle[log.result];
                return (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-500 whitespace-nowrap">{log.timestamp}</td>
                    <td className="px-4 py-3">
                      <span className="text-sm font-medium text-gray-900">{log.systemName}</span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">{log.event}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1.5">
                        {res.icon}
                        <span className={`text-xs font-medium ${res.className}`}>
                          {log.result === "success" ? "成功" : log.result === "error" ? "エラー" : "警告"}
                        </span>
                      </div>
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
