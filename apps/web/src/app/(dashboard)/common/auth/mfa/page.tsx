"use client";

import { useState } from "react";
import { Smartphone, Shield, Lock, CheckCircle } from "lucide-react";

const MFA_METHODS = [
  { id: "totp", name: "TOTP（認証アプリ）", description: "Google Authenticator / Microsoft Authenticator", icon: Smartphone, enabled: true, users: 28 },
  { id: "sms", name: "SMS認証", description: "登録された携帯電話番号にコードを送信", icon: Smartphone, enabled: true, users: 10 },
  { id: "email", name: "メール認証", description: "登録メールアドレスにコードを送信", icon: Shield, enabled: false, users: 0 },
  { id: "hardware", name: "ハードウェアキー", description: "YubiKey / FIDO2 セキュリティキー", icon: Lock, enabled: false, users: 2 },
];

const FORCED_GROUPS = [
  { role: "管理者", forced: true },
  { role: "プロジェクトマネージャー", forced: true },
  { role: "現場監督", forced: false },
  { role: "安全管理者", forced: true },
  { role: "閲覧のみ", forced: false },
];

export default function MfaPage() {
  const [methods, setMethods] = useState(MFA_METHODS);
  const [groups, setGroups] = useState(FORCED_GROUPS);

  const mfaEnabledUsers = 40;
  const forcedGroups = groups.filter((g) => g.forced).length;
  const notSetUsers = 12 - 40 < 0 ? 0 : 12 - 40;

  const toggleMethod = (id: string) => {
    setMethods((prev) => prev.map((m) => m.id === id ? { ...m, enabled: !m.enabled } : m));
  };

  const toggleGroup = (role: string) => {
    setGroups((prev) => prev.map((g) => g.role === role ? { ...g, forced: !g.forced } : g));
  };

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">MFA設定</h1>
        <p className="text-sm text-gray-500 mt-1">多要素認証の設定・強制ポリシー管理</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-green-50 rounded-lg">
            <CheckCircle className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">MFA有効ユーザー</p>
            <p className="text-2xl font-bold text-gray-900">{mfaEnabledUsers}名</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-blue-50 rounded-lg">
            <Shield className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">強制グループ数</p>
            <p className="text-2xl font-bold text-gray-900">{forcedGroups}グループ</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-orange-50 rounded-lg">
            <Lock className="w-5 h-5 text-orange-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">未設定ユーザー</p>
            <p className="text-2xl font-bold text-gray-900">{notSetUsers}名</p>
          </div>
        </div>
      </div>

      {/* MFA方式 */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-200">
          <h2 className="text-base font-semibold text-gray-900">MFA方式設定</h2>
        </div>
        <div className="divide-y divide-gray-100">
          {methods.map((method) => {
            const Icon = method.icon;
            return (
              <div key={method.id} className="flex items-center justify-between px-5 py-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gray-50 rounded-lg">
                    <Icon className="w-5 h-5 text-gray-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{method.name}</p>
                    <p className="text-xs text-gray-500">{method.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-gray-500">{method.users}名利用中</span>
                  <button
                    onClick={() => toggleMethod(method.id)}
                    className={`relative w-12 h-6 rounded-full transition-colors ${method.enabled ? "bg-blue-600" : "bg-gray-300"}`}
                  >
                    <span
                      className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                        method.enabled ? "translate-x-7" : "translate-x-1"
                      }`}
                    />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 強制グループ設定 */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-200">
          <h2 className="text-base font-semibold text-gray-900">強制有効グループ設定</h2>
          <p className="text-xs text-gray-500 mt-0.5">有効にしたグループは必ずMFAを設定する必要があります</p>
        </div>
        <div className="divide-y divide-gray-100">
          {groups.map((g) => (
            <div key={g.role} className="flex items-center justify-between px-5 py-3">
              <p className="text-sm font-medium text-gray-900">{g.role}</p>
              <button
                onClick={() => toggleGroup(g.role)}
                className={`relative w-12 h-6 rounded-full transition-colors ${g.forced ? "bg-blue-600" : "bg-gray-300"}`}
              >
                <span
                  className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                    g.forced ? "translate-x-7" : "translate-x-1"
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
