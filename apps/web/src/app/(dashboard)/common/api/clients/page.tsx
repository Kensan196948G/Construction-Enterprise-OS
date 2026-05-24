"use client";

import { Key, Webhook, Activity, Shield } from "lucide-react";

const API_CLIENTS = [
  { id: 1, name: "建設現場IoTゲートウェイ", type: "IoTシステム", apiKey: "ck_live_****...****a1b2", scopes: ["iot:read", "iot:write"], lastUsed: "2024-11-30 09:05", status: "active" },
  { id: 2, name: "会計システム連携", type: "ERPシステム", apiKey: "ck_live_****...****c3d4", scopes: ["erp:read", "erp:write"], lastUsed: "2024-11-30 08:30", status: "active" },
  { id: 3, name: "GISマッピングAPI", type: "GISシステム", apiKey: "ck_live_****...****e5f6", scopes: ["gis:read"], lastUsed: "2024-11-29 17:45", status: "active" },
  { id: 4, name: "工事写真管理システム", type: "文書管理", apiKey: "ck_live_****...****g7h8", scopes: ["documents:read", "documents:write"], lastUsed: "2024-11-29 14:00", status: "active" },
  { id: 5, name: "安全管理モバイルApp", type: "モバイルアプリ", apiKey: "ck_live_****...****i9j0", scopes: ["safety:read", "safety:write"], lastUsed: "2024-11-30 07:22", status: "active" },
  { id: 6, name: "レポート自動生成Bot", type: "自動化Bot", apiKey: "ck_live_****...****k1l2", scopes: ["projects:read", "reports:write"], lastUsed: "2024-11-30 06:00", status: "active" },
  { id: 7, name: "旧システム連携（廃止予定）", type: "レガシーシステム", apiKey: "ck_live_****...****m3n4", scopes: ["projects:read"], lastUsed: "2024-10-15 10:00", status: "inactive" },
  { id: 8, name: "テスト用クライアント", type: "開発・テスト", apiKey: "ck_test_****...****o5p6", scopes: ["*"], lastUsed: "2024-11-28 11:30", status: "active" },
];

const STATUS_STYLES: Record<string, string> = {
  active: "bg-green-100 text-green-800",
  inactive: "bg-gray-100 text-gray-700",
};

const STATUS_LABELS: Record<string, string> = {
  active: "アクティブ",
  inactive: "非アクティブ",
};

export default function ApiClientsPage() {
  const total = API_CLIENTS.length;
  const active = API_CLIENTS.filter((c) => c.status === "active").length;
  const todayCalls = 12847;

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">APIクライアント管理</h1>
          <p className="text-sm text-gray-500 mt-1">外部システム連携APIキーの発行・管理</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
          <Key className="w-4 h-4" />
          新規クライアント登録
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-blue-50 rounded-lg">
            <Webhook className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">総クライアント数</p>
            <p className="text-2xl font-bold text-gray-900">{total}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-green-50 rounded-lg">
            <Shield className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">アクティブ</p>
            <p className="text-2xl font-bold text-gray-900">{active}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-purple-50 rounded-lg">
            <Activity className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">今日のAPIコール</p>
            <p className="text-2xl font-bold text-gray-900">{todayCalls.toLocaleString()}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left font-semibold text-gray-600">クライアント名</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">システム種別</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">APIキー</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">権限スコープ</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">最終利用</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">ステータス</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {API_CLIENTS.map((client) => (
                <tr key={client.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{client.name}</td>
                  <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{client.type}</td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className="font-mono text-xs text-gray-600 bg-gray-100 px-2 py-0.5 rounded">
                      {client.apiKey}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {client.scopes.map((scope) => (
                        <span key={scope} className="px-1.5 py-0.5 bg-blue-50 text-blue-700 rounded text-xs font-mono">
                          {scope}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-500 whitespace-nowrap text-xs">{client.lastUsed}</td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_STYLES[client.status]}`}>
                      {STATUS_LABELS[client.status]}
                    </span>
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
