"use client";

import { Shield, Cloud, Users, CheckCircle, RefreshCw } from "lucide-react";

const ENTRA_CONFIG = {
  tenantId: "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  clientId: "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  scopes: ["openid", "profile", "email", "User.Read", "Group.Read.All"],
  status: "connected",
  lastSync: "2024-11-30 07:30",
  syncedUsers: 42,
  syncedGroups: 6,
};

const CONDITIONAL_POLICIES = [
  { id: 1, name: "管理者MFA必須", target: "管理者グループ", condition: "全アクセス時", action: "MFA要求", status: "enabled" },
  { id: 2, name: "外部ネットワーク制限", target: "全ユーザー", condition: "社外ネットワークからのアクセス", action: "MFA要求", status: "enabled" },
  { id: 3, name: "レガシー認証ブロック", target: "全ユーザー", condition: "レガシー認証プロトコル使用時", action: "ブロック", status: "enabled" },
  { id: 4, name: "高リスクサインインブロック", target: "全ユーザー", condition: "高リスクサインイン検出時", action: "ブロック", status: "enabled" },
  { id: 5, name: "準拠デバイスのみ", target: "現場担当グループ", condition: "モバイル端末からのアクセス", action: "準拠デバイス要求", status: "disabled" },
];

export default function EntraPage() {
  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Microsoft Entra ID</h1>
          <p className="text-sm text-gray-500 mt-1">Entra ID (旧Azure AD) 連携設定</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50">
          <RefreshCw className="w-4 h-4" />
          今すぐ同期
        </button>
      </div>

      {/* 統計 */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-blue-50 rounded-lg">
            <Users className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">ユーザー同期数</p>
            <p className="text-2xl font-bold text-gray-900">{ENTRA_CONFIG.syncedUsers}名</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-purple-50 rounded-lg">
            <Cloud className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">グループ同期数</p>
            <p className="text-2xl font-bold text-gray-900">{ENTRA_CONFIG.syncedGroups}件</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-green-50 rounded-lg">
            <CheckCircle className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">最終同期</p>
            <p className="text-sm font-bold text-gray-900">{ENTRA_CONFIG.lastSync}</p>
          </div>
        </div>
      </div>

      {/* 接続設定 */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-base font-semibold text-gray-900">Entra ID接続設定</h2>
          <span className="flex items-center gap-1.5 text-green-700 text-xs font-medium bg-green-50 px-3 py-1 rounded-full">
            <span className="w-2 h-2 bg-green-500 rounded-full" />
            接続済み
          </span>
        </div>
        <div className="p-5 space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <p className="text-xs text-gray-400 mb-1">テナント ID</p>
              <p className="text-sm font-mono text-gray-900 bg-gray-50 px-3 py-2 rounded-lg">{ENTRA_CONFIG.tenantId}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400 mb-1">クライアント ID</p>
              <p className="text-sm font-mono text-gray-900 bg-gray-50 px-3 py-2 rounded-lg">{ENTRA_CONFIG.clientId}</p>
            </div>
          </div>
          <div>
            <p className="text-xs text-gray-400 mb-1">スコープ</p>
            <div className="flex flex-wrap gap-2">
              {ENTRA_CONFIG.scopes.map((scope) => (
                <span key={scope} className="px-2 py-0.5 bg-blue-50 text-blue-800 rounded-full text-xs font-mono">
                  {scope}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 条件付きアクセスポリシー */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-200">
          <h2 className="text-base font-semibold text-gray-900">条件付きアクセスポリシー</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left font-semibold text-gray-600">ポリシー名</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">対象</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">条件</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">アクション</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">状態</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {CONDITIONAL_POLICIES.map((policy) => (
                <tr key={policy.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900 whitespace-nowrap">{policy.name}</td>
                  <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{policy.target}</td>
                  <td className="px-4 py-3 text-gray-600">{policy.condition}</td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      policy.action === "ブロック" ? "bg-red-100 text-red-800" :
                      policy.action === "MFA要求" ? "bg-orange-100 text-orange-800" :
                      "bg-blue-100 text-blue-800"
                    }`}>
                      {policy.action}
                    </span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    {policy.status === "enabled" ? (
                      <span className="flex items-center gap-1 text-green-700 text-xs font-medium">
                        <CheckCircle className="w-3.5 h-3.5" /> 有効
                      </span>
                    ) : (
                      <span className="text-gray-400 text-xs">無効</span>
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
