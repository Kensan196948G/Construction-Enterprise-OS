"use client";

import { useState } from "react";
import { Shield, Key, CheckCircle, RefreshCw } from "lucide-react";

const IDP_CONFIGS = [
  {
    id: "azure",
    name: "Azure AD",
    logo: "Az",
    color: "bg-blue-600",
    connected: true,
    clientId: "a1b2c3d4-****-****-****-e5f6g7h8i9j0",
    tenantId: "tenant-****-construction",
    lastSync: "2024-11-30 08:00",
    users: 42,
  },
  {
    id: "google",
    name: "Google Workspace",
    logo: "G",
    color: "bg-red-500",
    connected: false,
    clientId: "1234567890-****.apps.googleusercontent.com",
    tenantId: "construction-os.jp",
    lastSync: null,
    users: 0,
  },
  {
    id: "okta",
    name: "Okta",
    logo: "Ok",
    color: "bg-blue-500",
    connected: false,
    clientId: "0oa****construction",
    tenantId: "construction-os.okta.com",
    lastSync: null,
    users: 0,
  },
];

export default function SsoPage() {
  const [ssoEnabled, setSsoEnabled] = useState(true);

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">SSO設定</h1>
          <p className="text-sm text-gray-500 mt-1">シングルサインオン (IdP) の設定管理</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-600">SSO有効</span>
          <button
            onClick={() => setSsoEnabled(!ssoEnabled)}
            className={`relative w-12 h-6 rounded-full transition-colors ${ssoEnabled ? "bg-blue-600" : "bg-gray-300"}`}
          >
            <span
              className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                ssoEnabled ? "translate-x-7" : "translate-x-1"
              }`}
            />
          </button>
        </div>
      </div>

      {!ssoEnabled && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 flex items-center gap-2 text-yellow-800 text-sm">
          <Shield className="w-5 h-5 text-yellow-600 flex-shrink-0" />
          SSOが無効になっています。ローカル認証のみ有効です。
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {IDP_CONFIGS.map((idp) => (
          <div key={idp.id} className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-xl ${idp.color} text-white flex items-center justify-center text-sm font-bold`}>
                  {idp.logo}
                </div>
                <h3 className="font-semibold text-gray-900">{idp.name}</h3>
              </div>
              {idp.connected ? (
                <span className="flex items-center gap-1 text-green-700 text-xs font-medium bg-green-50 px-2 py-0.5 rounded-full">
                  <CheckCircle className="w-3.5 h-3.5" /> 接続済み
                </span>
              ) : (
                <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">未接続</span>
              )}
            </div>

            <div className="space-y-2 text-sm">
              <div>
                <p className="text-xs text-gray-400">Client ID</p>
                <p className="text-gray-700 font-mono text-xs truncate">{idp.clientId}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400">テナント ID</p>
                <p className="text-gray-700 font-mono text-xs truncate">{idp.tenantId}</p>
              </div>
              {idp.lastSync && (
                <div>
                  <p className="text-xs text-gray-400">最終同期</p>
                  <p className="text-gray-600 text-xs">{idp.lastSync}</p>
                </div>
              )}
              {idp.connected && (
                <div>
                  <p className="text-xs text-gray-400">同期ユーザー数</p>
                  <p className="text-gray-900 font-medium">{idp.users}名</p>
                </div>
              )}
            </div>

            <div className="flex gap-2 pt-1">
              <button className="flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50">
                <Key className="w-3.5 h-3.5" />
                設定編集
              </button>
              <button className="flex items-center justify-center gap-1.5 px-3 py-1.5 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50">
                <RefreshCw className="w-3.5 h-3.5" />
                テスト
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
