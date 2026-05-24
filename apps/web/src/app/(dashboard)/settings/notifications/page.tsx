"use client";

import { useState } from "react";
import { Bell, Mail, MessageSquare, Smartphone, CheckCircle, Send } from "lucide-react";

interface NotificationChannel {
  id: string;
  name: string;
  type: "email" | "slack" | "teams" | "sms" | "lineworks";
  description: string;
  enabled: boolean;
}

interface NotificationEvent {
  id: string;
  name: string;
  category: "safety" | "schedule" | "iot" | "approval" | "system";
  email: boolean;
  slack: boolean;
  sms: boolean;
}

const INITIAL_CHANNELS: NotificationChannel[] = [
  {
    id: "ch-email",
    name: "メール",
    type: "email",
    description: "SMTP経由でメール通知を送信",
    enabled: true,
  },
  {
    id: "ch-slack",
    name: "Slack",
    type: "slack",
    description: "Slack Incoming Webhookで通知",
    enabled: true,
  },
  {
    id: "ch-teams",
    name: "Microsoft Teams",
    type: "teams",
    description: "Teams Connectorで通知",
    enabled: false,
  },
  {
    id: "ch-sms",
    name: "SMS",
    type: "sms",
    description: "SMS送信サービス経由で通知",
    enabled: false,
  },
  {
    id: "ch-lineworks",
    name: "LINE Works",
    type: "lineworks",
    description: "LINE Works Bot APIで通知",
    enabled: true,
  },
];

const INITIAL_EVENTS: NotificationEvent[] = [
  { id: "ev-001", name: "緊急安全アラート", category: "safety", email: true, slack: true, sms: true },
  { id: "ev-002", name: "安全点検未実施", category: "safety", email: true, slack: true, sms: false },
  { id: "ev-003", name: "ヒヤリハット登録", category: "safety", email: false, slack: true, sms: false },
  { id: "ev-004", name: "工程遅延検知", category: "schedule", email: true, slack: true, sms: false },
  { id: "ev-005", name: "工程完了", category: "schedule", email: true, slack: false, sms: false },
  { id: "ev-006", name: "クリティカルパス変更", category: "schedule", email: true, slack: true, sms: false },
  { id: "ev-007", name: "IoTセンサー異常", category: "iot", email: true, slack: true, sms: true },
  { id: "ev-008", name: "バッテリー低下", category: "iot", email: false, slack: true, sms: false },
  { id: "ev-009", name: "通信断絶", category: "iot", email: true, slack: true, sms: false },
  { id: "ev-010", name: "承認依頼", category: "approval", email: true, slack: true, sms: false },
  { id: "ev-011", name: "承認完了", category: "approval", email: true, slack: false, sms: false },
  { id: "ev-012", name: "承認期限超過", category: "approval", email: true, slack: true, sms: true },
  { id: "ev-013", name: "システムエラー", category: "system", email: true, slack: true, sms: false },
  { id: "ev-014", name: "バックアップ完了", category: "system", email: false, slack: false, sms: false },
  { id: "ev-015", name: "メンテナンス通知", category: "system", email: true, slack: true, sms: false },
];

const categoryLabel: Record<NotificationEvent["category"], string> = {
  safety: "安全アラート",
  schedule: "工程遅延",
  iot: "IoTアラート",
  approval: "承認依頼",
  system: "システム",
};

const categoryStyle: Record<NotificationEvent["category"], string> = {
  safety: "bg-red-100 text-red-700",
  schedule: "bg-orange-100 text-orange-700",
  iot: "bg-blue-100 text-blue-700",
  approval: "bg-purple-100 text-purple-700",
  system: "bg-gray-100 text-gray-700",
};

const channelIcon: Record<NotificationChannel["type"], React.ReactNode> = {
  email: <Mail className="h-5 w-5" />,
  slack: <MessageSquare className="h-5 w-5" />,
  teams: <MessageSquare className="h-5 w-5" />,
  sms: <Smartphone className="h-5 w-5" />,
  lineworks: <MessageSquare className="h-5 w-5" />,
};

const channelColor: Record<NotificationChannel["type"], string> = {
  email: "bg-blue-100 text-blue-600",
  slack: "bg-green-100 text-green-600",
  teams: "bg-purple-100 text-purple-600",
  sms: "bg-orange-100 text-orange-600",
  lineworks: "bg-teal-100 text-teal-600",
};

export default function NotificationsPage() {
  const [channels, setChannels] = useState<NotificationChannel[]>(INITIAL_CHANNELS);
  const [events, setEvents] = useState<NotificationEvent[]>(INITIAL_EVENTS);
  const [testSent, setTestSent] = useState<string | null>(null);

  const toggleChannel = (id: string) => {
    setChannels((prev) =>
      prev.map((ch) => (ch.id === id ? { ...ch, enabled: !ch.enabled } : ch))
    );
  };

  const toggleEventSetting = (
    eventId: string,
    field: "email" | "slack" | "sms"
  ) => {
    setEvents((prev) =>
      prev.map((ev) =>
        ev.id === eventId ? { ...ev, [field]: !ev[field] } : ev
      )
    );
  };

  const handleTestSend = (channelId: string) => {
    setTestSent(channelId);
    setTimeout(() => setTestSent(null), 2000);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">通知設定</h1>
        <p className="mt-1 text-sm text-gray-500">
          通知チャンネルとイベント別通知ルールを設定します
        </p>
      </div>

      {/* Notification Channels */}
      <div className="rounded-xl border border-gray-200 bg-white shadow-sm">
        <div className="flex items-center gap-2 border-b border-gray-200 px-6 py-4">
          <Bell className="h-5 w-5 text-gray-500" />
          <h2 className="text-base font-semibold text-gray-900">通知チャンネル設定</h2>
        </div>
        <div className="divide-y divide-gray-100">
          {channels.map((channel) => (
            <div key={channel.id} className="flex items-center justify-between px-6 py-4">
              <div className="flex items-center gap-4">
                <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${channelColor[channel.type]}`}>
                  {channelIcon[channel.type]}
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">{channel.name}</p>
                  <p className="text-xs text-gray-500">{channel.description}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                {/* Test Send Button */}
                <button
                  onClick={() => handleTestSend(channel.id)}
                  disabled={!channel.enabled}
                  className="flex items-center gap-1.5 rounded-lg border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40 transition-colors"
                >
                  {testSent === channel.id ? (
                    <>
                      <CheckCircle className="h-3.5 w-3.5 text-green-500" />
                      送信済
                    </>
                  ) : (
                    <>
                      <Send className="h-3.5 w-3.5" />
                      テスト送信
                    </>
                  )}
                </button>
                {/* Toggle */}
                <button
                  onClick={() => toggleChannel(channel.id)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${channel.enabled ? "bg-blue-600" : "bg-gray-200"}`}
                  role="switch"
                  aria-checked={channel.enabled}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${channel.enabled ? "translate-x-6" : "translate-x-1"}`}
                  />
                </button>
                <span className={`text-xs font-medium ${channel.enabled ? "text-blue-600" : "text-gray-400"}`}>
                  {channel.enabled ? "有効" : "無効"}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Event Notification Table */}
      <div className="rounded-xl border border-gray-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5 text-gray-500" />
            <h2 className="text-base font-semibold text-gray-900">通知イベント設定</h2>
          </div>
          <span className="text-sm text-gray-500">{events.length}イベント</span>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">イベント名</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">カテゴリ</th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500">
                  <div className="flex items-center justify-center gap-1">
                    <Mail className="h-3.5 w-3.5" />
                    メール
                  </div>
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500">
                  <div className="flex items-center justify-center gap-1">
                    <MessageSquare className="h-3.5 w-3.5" />
                    Slack
                  </div>
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500">
                  <div className="flex items-center justify-center gap-1">
                    <Smartphone className="h-3.5 w-3.5" />
                    SMS
                  </div>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
              {events.map((event) => (
                <tr key={event.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">{event.name}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${categoryStyle[event.category]}`}>
                      {categoryLabel[event.category]}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <input
                      type="checkbox"
                      checked={event.email}
                      onChange={() => toggleEventSetting(event.id, "email")}
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                    />
                  </td>
                  <td className="px-4 py-3 text-center">
                    <input
                      type="checkbox"
                      checked={event.slack}
                      onChange={() => toggleEventSetting(event.id, "slack")}
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                    />
                  </td>
                  <td className="px-4 py-3 text-center">
                    <input
                      type="checkbox"
                      checked={event.sms}
                      onChange={() => toggleEventSetting(event.id, "sms")}
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="flex items-center justify-end gap-3 border-t border-gray-200 px-6 py-4">
          <button className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
            リセット
          </button>
          <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors">
            設定を保存
          </button>
        </div>
      </div>
    </div>
  );
}
