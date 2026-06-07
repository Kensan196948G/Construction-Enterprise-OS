"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Building2,
  User,
  Bell,
  Shield,
  Globe,
  Database,
  Key,
  Mail,
  Phone,
  MapPin,
  Camera,
  Save,
  ChevronRight,
  CheckCircle2,
  AlertCircle,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { useAuthStore } from "@/lib/store/auth";

type SectionId =
  | "company"
  | "profile"
  | "notifications"
  | "system"
  | "security"
  | "integrations";

type NotificationChannel = "email" | "push" | "sms";

interface NotificationRow {
  id: string;
  label: string;
  description: string;
  email: boolean;
  push: boolean;
  sms: boolean;
}

interface SystemSettings {
  language: string;
  timezone: string;
  dateFormat: string;
  theme: string;
}

interface ApiEndpoint {
  id: string;
  label: string;
  path: string;
  status: "idle" | "loading" | "ok" | "error";
  latency: number | null;
}

// --- Sub-components ---

function Toggle({
  checked,
  onChange,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 ${
        checked ? "bg-primary-600" : "bg-gray-200"
      }`}
    >
      <span
        className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform ${
          checked ? "translate-x-[18px]" : "translate-x-0.5"
        }`}
      />
    </button>
  );
}

function SaveToast({ show }: { show: boolean }) {
  if (!show) return null;
  return (
    <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2 rounded-xl bg-gray-900 px-4 py-3 text-sm text-white shadow-lg animate-in slide-in-from-bottom-4">
      <CheckCircle2 className="h-4 w-4 text-approve-400" />
      設定を保存しました
    </div>
  );
}

// --- Static data ---

const settingsSections: {
  id: SectionId;
  label: string;
  icon: React.ElementType;
}[] = [
  { id: "company", label: "会社情報", icon: Building2 },
  { id: "profile", label: "プロフィール", icon: User },
  { id: "notifications", label: "通知設定", icon: Bell },
  { id: "system", label: "システム設定", icon: Globe },
  { id: "security", label: "セキュリティ", icon: Shield },
  { id: "integrations", label: "外部連携", icon: Globe },
];

const initialNotifications: NotificationRow[] = [
  {
    id: "iot_alert",
    label: "IoTアラート",
    description: "センサーが閾値を超えた際に通知",
    email: true,
    push: true,
    sms: false,
  },
  {
    id: "workflow_approval",
    label: "ワークフロー承認依頼",
    description: "承認依頼が届いた際に通知",
    email: true,
    push: true,
    sms: false,
  },
  {
    id: "document_update",
    label: "文書更新",
    description: "書類が更新・承認された際に通知",
    email: true,
    push: false,
    sms: false,
  },
  {
    id: "weather_warning",
    label: "気象警報",
    description: "作業エリアに気象警報が発令された際に通知",
    email: true,
    push: true,
    sms: true,
  },
  {
    id: "equipment_alert",
    label: "重機アラート",
    description: "重機の異常が検知された際に通知",
    email: false,
    push: true,
    sms: false,
  },
  {
    id: "daily_report",
    label: "日次レポート",
    description: "毎日18時に当日のサマリーを通知",
    email: true,
    push: false,
    sms: false,
  },
];

const initialEndpoints: ApiEndpoint[] = [
  {
    id: "gateway",
    label: "API Gateway",
    path: "/api/v1/health",
    status: "idle",
    latency: null,
  },
  {
    id: "auth",
    label: "認証サービス",
    path: "/api/v1/auth/status",
    status: "idle",
    latency: null,
  },
  {
    id: "construction",
    label: "工事管理サービス",
    path: "/api/v1/construction/health",
    status: "idle",
    latency: null,
  },
  {
    id: "documents",
    label: "文書管理サービス",
    path: "/api/v1/documents/health",
    status: "idle",
    latency: null,
  },
];

const integrations = [
  {
    name: "国土交通省 電子納品システム",
    status: "connected",
    lastSync: "2024-11-20 14:00",
  },
  {
    name: "BIM連携 (Autodesk Revit)",
    status: "connected",
    lastSync: "2024-11-19 09:30",
  },
  {
    name: "気象データAPI (気象庁)",
    status: "connected",
    lastSync: "2024-11-20 15:00",
  },
  { name: "ERP連携 (SAP)", status: "disconnected", lastSync: null },
  { name: "kintone 工事台帳", status: "error", lastSync: "2024-11-15 10:00" },
];

// --- Main component ---

export default function SettingsPage() {
  const { user } = useAuthStore();
  const [activeSection, setActiveSection] = useState<SectionId>("company");
  const [showToast, setShowToast] = useState(false);

  // Profile state — synced from auth store
  const [profileName, setProfileName] = useState("田中 健一");
  const [profileRole, setProfileRole] = useState("現場監督");
  const [profileEmail, setProfileEmail] = useState(
    "tanaka.kenichi@construction-eos.co.jp",
  );
  const [profilePhone, setProfilePhone] = useState("090-1234-5678");

  // Sync from auth store when user loads
  useEffect(() => {
    if (user?.name) setProfileName(user.name);
    if (user?.email) setProfileEmail(user.email);
    if (user?.role) setProfileRole(user.role);
  }, [user]);

  // Notification toggles
  const [notifications, setNotifications] =
    useState<NotificationRow[]>(initialNotifications);

  const toggleNotification = useCallback(
    (id: string, channel: NotificationChannel) => {
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, [channel]: !n[channel] } : n)),
      );
    },
    [],
  );

  // MFA toggle
  const [mfaEnabled, setMfaEnabled] = useState(true);

  // System settings
  const [systemSettings, setSystemSettings] = useState<SystemSettings>({
    language: "ja",
    timezone: "Asia/Tokyo",
    dateFormat: "YYYY/MM/DD",
    theme: "light",
  });

  // API endpoint test
  const [endpoints, setEndpoints] = useState<ApiEndpoint[]>(initialEndpoints);

  const testEndpoint = useCallback(async (id: string) => {
    setEndpoints((prev) =>
      prev.map((ep) =>
        ep.id === id ? { ...ep, status: "loading", latency: null } : ep,
      ),
    );
    const ep = initialEndpoints.find((e) => e.id === id)!;
    const start = Date.now();
    try {
      const res = await fetch(ep.path, {
        method: "GET",
        signal: AbortSignal.timeout(5000),
      });
      const latency = Date.now() - start;
      setEndpoints((prev) =>
        prev.map((e) =>
          e.id === id ? { ...e, status: res.ok ? "ok" : "error", latency } : e,
        ),
      );
    } catch {
      setEndpoints((prev) =>
        prev.map((e) =>
          e.id === id
            ? { ...e, status: "error", latency: Date.now() - start }
            : e,
        ),
      );
    }
  }, []);

  const testAllEndpoints = useCallback(async () => {
    for (const ep of initialEndpoints) {
      await testEndpoint(ep.id);
    }
  }, [testEndpoint]);

  // Save handler
  const handleSave = () => {
    setShowToast(true);
    setTimeout(() => setShowToast(false), 2500);
  };

  // Display helpers
  const displayName = user?.name ?? profileName;
  const initials = displayName
    .split(/[\s　]/)
    .map((s) => s[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <div className="p-6 lg:p-8 space-y-6">
      <SaveToast show={showToast} />

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">設定</h1>
        <p className="mt-1 text-gray-500 text-sm">
          システム・アカウント・通知の設定を管理します
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar Navigation */}
        <div className="rounded-xl border border-gray-200 bg-white overflow-hidden h-fit">
          {settingsSections.map((section, i) => {
            const Icon = section.icon;
            const isActive = activeSection === section.id;
            return (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`w-full flex items-center justify-between px-4 py-3 text-sm hover:bg-gray-50 transition-colors ${
                  isActive
                    ? "bg-primary-50 text-primary-700 font-medium"
                    : "text-gray-700"
                } ${i < settingsSections.length - 1 ? "border-b border-gray-100" : ""}`}
              >
                <div className="flex items-center gap-3">
                  <Icon className="h-4 w-4" />
                  {section.label}
                </div>
                <ChevronRight className="h-3.5 w-3.5 text-gray-400" />
              </button>
            );
          })}
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3 space-y-6">
          {/* Company Info */}
          {activeSection === "company" && (
            <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <h2 className="font-bold text-gray-900">会社情報</h2>
                <p className="text-xs text-gray-500 mt-0.5">
                  システム全体に表示される会社情報を設定します
                </p>
              </div>
              <div className="p-6 space-y-5">
                <div className="flex items-center gap-5">
                  <div className="h-16 w-16 rounded-xl bg-primary-600 flex items-center justify-center flex-shrink-0">
                    <Building2 className="h-8 w-8 text-white" />
                  </div>
                  <div>
                    <button className="inline-flex items-center gap-2 rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                      <Camera className="h-3.5 w-3.5" />
                      ロゴを変更
                    </button>
                    <p className="text-xs text-gray-400 mt-1">
                      PNG, JPG（最大 2MB）
                    </p>
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                      会社名
                    </label>
                    <input
                      type="text"
                      defaultValue="建設エンタープライズ株式会社"
                      className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                      建設業許可番号
                    </label>
                    <input
                      type="text"
                      defaultValue="国土交通大臣許可（特-05）第12345号"
                      className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                      代表電話番号
                    </label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-gray-400" />
                      <input
                        type="tel"
                        defaultValue="03-1234-5678"
                        className="w-full rounded-lg border border-gray-200 pl-9 pr-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                      代表メールアドレス
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-gray-400" />
                      <input
                        type="email"
                        defaultValue="info@construction-eos.co.jp"
                        className="w-full rounded-lg border border-gray-200 pl-9 pr-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                      />
                    </div>
                  </div>
                  <div className="sm:col-span-2">
                    <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                      本社所在地
                    </label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-gray-400" />
                      <input
                        type="text"
                        defaultValue="東京都港区芝浦1-2-3 建設ビル10F"
                        className="w-full rounded-lg border border-gray-200 pl-9 pr-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Profile */}
          {activeSection === "profile" && (
            <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <h2 className="font-bold text-gray-900">プロフィール</h2>
                <p className="text-xs text-gray-500 mt-0.5">
                  ログイン中のアカウント情報
                </p>
              </div>
              <div className="p-6 space-y-4">
                <div className="flex items-center gap-4">
                  <div className="h-14 w-14 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0">
                    <span className="text-primary-700 font-bold text-lg">
                      {initials}
                    </span>
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">{displayName}</p>
                    <p className="text-xs text-gray-500">
                      {user?.role ?? "現場監督"}
                    </p>
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                      氏名
                    </label>
                    <input
                      type="text"
                      value={profileName}
                      onChange={(e) => setProfileName(e.target.value)}
                      className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                      役職
                    </label>
                    <input
                      type="text"
                      value={profileRole}
                      onChange={(e) => setProfileRole(e.target.value)}
                      className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                      メールアドレス
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-gray-400" />
                      <input
                        type="email"
                        value={profileEmail}
                        onChange={(e) => setProfileEmail(e.target.value)}
                        className="w-full rounded-lg border border-gray-200 pl-9 pr-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                      携帯電話
                    </label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-gray-400" />
                      <input
                        type="tel"
                        value={profilePhone}
                        onChange={(e) => setProfilePhone(e.target.value)}
                        className="w-full rounded-lg border border-gray-200 pl-9 pr-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Notifications */}
          {activeSection === "notifications" && (
            <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <h2 className="font-bold text-gray-900">通知設定</h2>
                <p className="text-xs text-gray-500 mt-0.5">
                  各イベントの通知方法を設定します
                </p>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-100">
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500">
                        通知種別
                      </th>
                      <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500">
                        メール
                      </th>
                      <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500">
                        プッシュ
                      </th>
                      <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500">
                        SMS
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {notifications.map((notif) => (
                      <tr
                        key={notif.id}
                        className="hover:bg-gray-50 transition-colors"
                      >
                        <td className="px-6 py-3.5">
                          <p className="text-sm font-medium text-gray-900">
                            {notif.label}
                          </p>
                          <p className="text-xs text-gray-500 mt-0.5">
                            {notif.description}
                          </p>
                        </td>
                        {(
                          ["email", "push", "sms"] as NotificationChannel[]
                        ).map((channel) => (
                          <td key={channel} className="px-4 py-3.5 text-center">
                            <div className="flex justify-center">
                              <Toggle
                                checked={notif[channel]}
                                onChange={() =>
                                  toggleNotification(notif.id, channel)
                                }
                              />
                            </div>
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* System Settings */}
          {activeSection === "system" && (
            <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <h2 className="font-bold text-gray-900">システム設定</h2>
                <p className="text-xs text-gray-500 mt-0.5">
                  表示言語・タイムゾーン・テーマを設定します
                </p>
              </div>
              <div className="p-6 space-y-5">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                      表示言語
                    </label>
                    <select
                      value={systemSettings.language}
                      onChange={(e) =>
                        setSystemSettings((s) => ({
                          ...s,
                          language: e.target.value,
                        }))
                      }
                      className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                    >
                      <option value="ja">日本語</option>
                      <option value="en">English</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                      タイムゾーン
                    </label>
                    <select
                      value={systemSettings.timezone}
                      onChange={(e) =>
                        setSystemSettings((s) => ({
                          ...s,
                          timezone: e.target.value,
                        }))
                      }
                      className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                    >
                      <option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
                      <option value="UTC">UTC</option>
                      <option value="America/New_York">America/New_York</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                      日付フォーマット
                    </label>
                    <select
                      value={systemSettings.dateFormat}
                      onChange={(e) =>
                        setSystemSettings((s) => ({
                          ...s,
                          dateFormat: e.target.value,
                        }))
                      }
                      className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                    >
                      <option value="YYYY/MM/DD">YYYY/MM/DD</option>
                      <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                      <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                      テーマ
                    </label>
                    <select
                      value={systemSettings.theme}
                      onChange={(e) =>
                        setSystemSettings((s) => ({
                          ...s,
                          theme: e.target.value,
                        }))
                      }
                      className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                    >
                      <option value="light">ライト</option>
                      <option value="dark">ダーク</option>
                      <option value="system">システム設定に従う</option>
                    </select>
                  </div>
                </div>

                {/* API Connection Test */}
                <div className="mt-4 rounded-lg border border-gray-200 overflow-hidden">
                  <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-100">
                    <span className="text-xs font-semibold text-gray-700">
                      API 接続テスト
                    </span>
                    <button
                      onClick={testAllEndpoints}
                      className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 px-2.5 py-1 text-xs font-medium text-gray-600 hover:bg-white transition-colors"
                    >
                      <RefreshCw className="h-3 w-3" />
                      全て再テスト
                    </button>
                  </div>
                  <div className="divide-y divide-gray-100">
                    {endpoints.map((ep) => (
                      <div
                        key={ep.id}
                        className="flex items-center justify-between px-4 py-3"
                      >
                        <span className="text-sm text-gray-700">
                          {ep.label}
                        </span>
                        <div className="flex items-center gap-3">
                          {ep.status === "loading" && (
                            <Loader2 className="h-4 w-4 text-gray-400 animate-spin" />
                          )}
                          {ep.status === "ok" && (
                            <span className="flex items-center gap-1 text-xs text-approve-600 font-medium">
                              <CheckCircle2 className="h-3.5 w-3.5" />
                              {ep.latency}ms
                            </span>
                          )}
                          {ep.status === "error" && (
                            <span className="flex items-center gap-1 text-xs text-danger-600 font-medium">
                              <AlertCircle className="h-3.5 w-3.5" />
                              エラー
                            </span>
                          )}
                          <button
                            onClick={() => testEndpoint(ep.id)}
                            disabled={ep.status === "loading"}
                            className="rounded border border-gray-200 px-2 py-0.5 text-xs font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-50 transition-colors"
                          >
                            テスト
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Security */}
          {activeSection === "security" && (
            <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <h2 className="font-bold text-gray-900">セキュリティ</h2>
                <p className="text-xs text-gray-500 mt-0.5">
                  パスワードと認証設定
                </p>
              </div>
              <div className="divide-y divide-gray-100">
                <div className="flex items-center justify-between px-6 py-4">
                  <div className="flex items-center gap-3">
                    <Key className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        パスワード変更
                      </p>
                      <p className="text-xs text-gray-500">
                        最終変更: 2024-09-01
                      </p>
                    </div>
                  </div>
                  <button className="rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                    変更する
                  </button>
                </div>
                <div className="flex items-center justify-between px-6 py-4">
                  <div className="flex items-center gap-3">
                    <Shield className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        二段階認証（MFA）
                      </p>
                      <p className="text-xs text-gray-500">
                        より安全なログインのために推奨します
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-xs font-medium ${mfaEnabled ? "text-approve-600" : "text-gray-400"}`}
                    >
                      {mfaEnabled ? "有効" : "無効"}
                    </span>
                    <Toggle checked={mfaEnabled} onChange={setMfaEnabled} />
                  </div>
                </div>
                <div className="flex items-center justify-between px-6 py-4">
                  <div className="flex items-center gap-3">
                    <Database className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        ログイン履歴
                      </p>
                      <p className="text-xs text-gray-500">
                        直近のアクセス履歴を確認
                      </p>
                    </div>
                  </div>
                  <button className="rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                    確認する
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Integrations */}
          {activeSection === "integrations" && (
            <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <h2 className="font-bold text-gray-900">外部連携</h2>
                <p className="text-xs text-gray-500 mt-0.5">
                  外部システムとの連携状態を管理します
                </p>
              </div>
              <div className="divide-y divide-gray-100">
                {integrations.map((intg) => (
                  <div
                    key={intg.name}
                    className="flex items-center justify-between px-6 py-4"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`h-2 w-2 rounded-full flex-shrink-0 ${intg.status === "connected" ? "bg-approve-500" : intg.status === "error" ? "bg-danger-500" : "bg-gray-300"}`}
                      />
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {intg.name}
                        </p>
                        {intg.lastSync && (
                          <p className="text-xs text-gray-400">
                            最終同期: {intg.lastSync}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-xs font-medium ${intg.status === "connected" ? "text-approve-600" : intg.status === "error" ? "text-danger-600" : "text-gray-400"}`}
                      >
                        {intg.status === "connected"
                          ? "接続中"
                          : intg.status === "error"
                            ? "エラー"
                            : "未接続"}
                      </span>
                      <button className="rounded-lg border border-gray-200 px-2.5 py-1 text-xs font-medium text-gray-600 hover:bg-gray-50 transition-colors">
                        {intg.status === "disconnected" ? "接続する" : "設定"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Save Button */}
          <div className="flex justify-end">
            <button
              onClick={handleSave}
              className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-primary-700 transition-colors"
            >
              <Save className="h-4 w-4" />
              設定を保存
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
