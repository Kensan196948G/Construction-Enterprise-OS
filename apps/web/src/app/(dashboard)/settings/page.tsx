import {
  Building2,
  User,
  Bell,
  Shield,
  Palette,
  Globe,
  Database,
  Key,
  Mail,
  Phone,
  MapPin,
  Camera,
  Save,
  ChevronRight,
} from "lucide-react";

const settingsSections = [
  { id: "company", label: "会社情報", icon: Building2 },
  { id: "profile", label: "プロフィール", icon: User },
  { id: "notifications", label: "通知設定", icon: Bell },
  { id: "security", label: "セキュリティ", icon: Shield },
  { id: "appearance", label: "表示設定", icon: Palette },
  { id: "integrations", label: "連携設定", icon: Globe },
];

const notifications = [
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

export default function SettingsPage() {
  return (
    <div className="p-6 lg:p-8 space-y-6">
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
            return (
              <button
                key={section.id}
                className={`w-full flex items-center justify-between px-4 py-3 text-sm hover:bg-gray-50 transition-colors ${
                  i === 0
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
          <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-100">
              <h2 className="font-bold text-gray-900">会社情報</h2>
              <p className="text-xs text-gray-500 mt-0.5">
                システム全体に表示される会社情報を設定します
              </p>
            </div>
            <div className="p-6 space-y-5">
              {/* Logo Upload */}
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
                    PNG, JPG (最大 2MB)
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

          {/* Profile */}
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
                  <span className="text-primary-700 font-bold text-lg">田</span>
                </div>
                <div>
                  <p className="font-semibold text-gray-900">田中 健一</p>
                  <p className="text-xs text-gray-500">
                    現場監督 / 品川タワー新築工事
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
                    defaultValue="田中 健一"
                    className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                    役職
                  </label>
                  <input
                    type="text"
                    defaultValue="現場監督"
                    className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                    メールアドレス
                  </label>
                  <input
                    type="email"
                    defaultValue="tanaka.kenichi@construction-eos.co.jp"
                    className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                    携帯電話
                  </label>
                  <input
                    type="tel"
                    defaultValue="090-1234-5678"
                    className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Notifications */}
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
                      {(["email", "push", "sms"] as const).map((channel) => (
                        <td key={channel} className="px-4 py-3.5 text-center">
                          <div className="flex justify-center">
                            <div
                              className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                                notif[channel]
                                  ? "bg-primary-600"
                                  : "bg-gray-200"
                              }`}
                            >
                              <span
                                className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform ${
                                  notif[channel]
                                    ? "translate-x-4.5"
                                    : "translate-x-0.5"
                                }`}
                              />
                            </div>
                          </div>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Security */}
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
                      二段階認証
                    </p>
                    <p className="text-xs text-gray-500">
                      より安全なログインのために推奨します
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-approve-600 font-medium">
                    有効
                  </span>
                  <div className="relative inline-flex h-5 w-9 items-center rounded-full bg-primary-600">
                    <span className="inline-block h-3.5 w-3.5 transform translate-x-4.5 rounded-full bg-white shadow" />
                  </div>
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

          {/* Integrations */}
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
                      className={`h-2 w-2 rounded-full flex-shrink-0 ${
                        intg.status === "connected"
                          ? "bg-approve-500"
                          : intg.status === "error"
                            ? "bg-danger-500"
                            : "bg-gray-300"
                      }`}
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
                      className={`text-xs font-medium ${
                        intg.status === "connected"
                          ? "text-approve-600"
                          : intg.status === "error"
                            ? "text-danger-600"
                            : "text-gray-400"
                      }`}
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

          {/* Save Button */}
          <div className="flex justify-end">
            <button className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-primary-700 transition-colors">
              <Save className="h-4 w-4" />
              設定を保存
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
