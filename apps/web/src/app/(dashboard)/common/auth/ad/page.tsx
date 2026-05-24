"use client";

import { useState, useCallback, useEffect } from "react";
import { Network, Building, RefreshCw, Shield } from "lucide-react";

const AD_CONFIG = {
  domain: "construction-os.local",
  ldapServer: "ldap://192.168.1.10:389",
  baseDn: "DC=construction-os,DC=local",
  bindUser: "CN=ldap-service,OU=ServiceAccounts,DC=construction-os,DC=local",
  status: "connected",
  lastSync: "2024-11-30 06:00",
  syncedUsers: 38,
  syncedGroups: 8,
};

type GroupMapping = {
  id: number;
  adGroup: string;
  systemRole: string;
  members: number;
};

const GROUP_MAPPINGS: GroupMapping[] = [
  {
    id: 1,
    adGroup: "CN=SystemAdmins,OU=Groups,DC=construction-os,DC=local",
    systemRole: "管理者",
    members: 2,
  },
  {
    id: 2,
    adGroup: "CN=ProjectManagers,OU=Groups,DC=construction-os,DC=local",
    systemRole: "プロジェクトマネージャー",
    members: 5,
  },
  {
    id: 3,
    adGroup: "CN=SiteWorkers,OU=Groups,DC=construction-os,DC=local",
    systemRole: "現場監督",
    members: 20,
  },
  {
    id: 4,
    adGroup: "CN=SafetyOfficers,OU=Groups,DC=construction-os,DC=local",
    systemRole: "安全管理者",
    members: 3,
  },
  {
    id: 5,
    adGroup: "CN=ReadOnly,OU=Groups,DC=construction-os,DC=local",
    systemRole: "閲覧のみ",
    members: 8,
  },
];

export default function AdPage() {
  const [groupMappings, setGroupMappings] =
    useState<GroupMapping[]>(GROUP_MAPPINGS);
  const [loading, setLoading] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/v1/auth/ad/groups");
      if (!res.ok) throw new Error("fetch failed");
      const json = await res.json();
      const items: Record<string, unknown>[] = json?.items ?? json?.data ?? [];
      if (Array.isArray(items) && items.length > 0) {
        setGroupMappings(
          items.map((item: Record<string, unknown>, idx: number) => ({
            id: Number(item.id ?? idx + 1),
            adGroup: String(item.adGroup ?? item.ad_group ?? ""),
            systemRole: String(item.systemRole ?? item.system_role ?? ""),
            members: Number(item.members ?? 0),
          })),
        );
      }
    } catch {
      setGroupMappings(GROUP_MAPPINGS);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Active Directory連携
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            オンプレミスADとのLDAP連携設定
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50">
          <RefreshCw className="w-4 h-4" />
          今すぐ同期
        </button>
      </div>

      {/* 接続情報 */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-base font-semibold text-gray-900">AD接続設定</h2>
          <span className="flex items-center gap-1.5 text-green-700 text-xs font-medium bg-green-50 px-3 py-1 rounded-full">
            <span className="w-2 h-2 bg-green-500 rounded-full" />
            接続済み
          </span>
        </div>
        <div className="grid grid-cols-1 gap-0 sm:grid-cols-2">
          {[
            { label: "ドメイン名", value: AD_CONFIG.domain, icon: Building },
            {
              label: "LDAPサーバー",
              value: AD_CONFIG.ldapServer,
              icon: Network,
            },
            { label: "ベースDN", value: AD_CONFIG.baseDn, icon: Shield },
            {
              label: "バインドユーザー",
              value: AD_CONFIG.bindUser,
              icon: Shield,
            },
          ].map(({ label, value, icon: Icon }) => (
            <div
              key={label}
              className="flex items-start gap-3 px-5 py-3 border-b border-r border-gray-100"
            >
              <div className="p-1.5 bg-gray-50 rounded-lg mt-0.5">
                <Icon className="w-4 h-4 text-gray-500" />
              </div>
              <div>
                <p className="text-xs text-gray-400">{label}</p>
                <p className="text-sm text-gray-900 font-mono break-all">
                  {value}
                </p>
              </div>
            </div>
          ))}
        </div>
        <div className="px-5 py-3 bg-gray-50 flex items-center gap-6 text-sm text-gray-600">
          <span>
            最終同期: <strong>{AD_CONFIG.lastSync}</strong>
          </span>
          <span>
            同期ユーザー: <strong>{AD_CONFIG.syncedUsers}名</strong>
          </span>
          <span>
            同期グループ: <strong>{AD_CONFIG.syncedGroups}件</strong>
          </span>
        </div>
      </div>

      {/* グループマッピング */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-base font-semibold text-gray-900">
            グループマッピング設定
            {loading && (
              <span className="ml-2 text-xs text-gray-400 font-normal">
                読み込み中...
              </span>
            )}
          </h2>
          <button className="px-3 py-1.5 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700">
            マッピング追加
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left font-semibold text-gray-600">
                  ADグループ
                </th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">
                  システムロール
                </th>
                <th className="px-4 py-3 text-right font-semibold text-gray-600 whitespace-nowrap">
                  メンバー数
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {groupMappings.map((mapping) => (
                <tr key={mapping.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono text-xs text-gray-700 break-all">
                    {mapping.adGroup}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                      {mapping.systemRole}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-600 text-right whitespace-nowrap">
                    {mapping.members}名
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
