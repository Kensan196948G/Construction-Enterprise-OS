"use client";

import { useState } from "react";
import { Bell, AlertTriangle, Thermometer, Activity } from "lucide-react";

type AlertSeverity = "critical" | "warning" | "info";
type AlertStatus = "active" | "acknowledged" | "resolved";
type SensorType = "temp" | "humidity" | "vibration" | "gas" | "water" | "power";

interface IotAlert {
  id: string;
  sensorId: string;
  location: string;
  sensorType: SensorType;
  value: string;
  threshold: string;
  severity: AlertSeverity;
  occurredAt: string;
  status: AlertStatus;
}

const MOCK_ALERTS: IotAlert[] = [
  {
    id: "1",
    sensorId: "TEMP-001",
    location: "第1工区 地下1F",
    sensorType: "temp",
    value: "48.2°C",
    threshold: "45°C",
    severity: "critical",
    occurredAt: "2026-05-24 09:15",
    status: "active",
  },
  {
    id: "2",
    sensorId: "GAS-003",
    location: "トンネル掘削面",
    sensorType: "gas",
    value: "320 ppm",
    threshold: "300 ppm",
    severity: "critical",
    occurredAt: "2026-05-24 08:42",
    status: "active",
  },
  {
    id: "3",
    sensorId: "VIB-007",
    location: "橋梁支柱 A-3",
    sensorType: "vibration",
    value: "8.4 mm/s",
    threshold: "6 mm/s",
    severity: "warning",
    occurredAt: "2026-05-24 08:30",
    status: "acknowledged",
  },
  {
    id: "4",
    sensorId: "HUM-012",
    location: "資材倉庫",
    sensorType: "humidity",
    value: "91%",
    threshold: "85%",
    severity: "warning",
    occurredAt: "2026-05-24 07:55",
    status: "active",
  },
  {
    id: "5",
    sensorId: "WATER-002",
    location: "排水ポンプ室",
    sensorType: "water",
    value: "2.4 m",
    threshold: "2.0 m",
    severity: "warning",
    occurredAt: "2026-05-24 07:20",
    status: "active",
  },
  {
    id: "6",
    sensorId: "PWR-005",
    location: "仮設電源盤 B",
    sensorType: "power",
    value: "198 V",
    threshold: "200 V (下限)",
    severity: "warning",
    occurredAt: "2026-05-23 22:10",
    status: "acknowledged",
  },
  {
    id: "7",
    sensorId: "TEMP-008",
    location: "コンクリート養生エリア",
    sensorType: "temp",
    value: "4.1°C",
    threshold: "5°C (下限)",
    severity: "warning",
    occurredAt: "2026-05-23 21:30",
    status: "acknowledged",
  },
  {
    id: "8",
    sensorId: "GAS-001",
    location: "地下駐車場工事区",
    sensorType: "gas",
    value: "280 ppm",
    threshold: "300 ppm",
    severity: "info",
    occurredAt: "2026-05-23 18:45",
    status: "resolved",
  },
  {
    id: "9",
    sensorId: "VIB-003",
    location: "隣接既存建物壁面",
    sensorType: "vibration",
    value: "3.2 mm/s",
    threshold: "5 mm/s",
    severity: "info",
    occurredAt: "2026-05-23 16:20",
    status: "resolved",
  },
  {
    id: "10",
    sensorId: "TEMP-005",
    location: "鉄筋ヤード",
    sensorType: "temp",
    value: "38.7°C",
    threshold: "40°C",
    severity: "info",
    occurredAt: "2026-05-23 14:10",
    status: "resolved",
  },
  {
    id: "11",
    sensorId: "HUM-006",
    location: "木材資材置き場",
    sensorType: "humidity",
    value: "78%",
    threshold: "75%",
    severity: "warning",
    occurredAt: "2026-05-23 12:00",
    status: "resolved",
  },
  {
    id: "12",
    sensorId: "PWR-002",
    location: "タワークレーン電源",
    sensorType: "power",
    value: "412 V",
    threshold: "400 V (上限)",
    severity: "critical",
    occurredAt: "2026-05-23 10:30",
    status: "resolved",
  },
];

const SEVERITY_CONFIG: Record<
  AlertSeverity,
  { label: string; rowClass: string; badgeClass: string; dotClass: string }
> = {
  critical: {
    label: "緊急",
    rowClass: "bg-red-50",
    badgeClass: "bg-red-100 text-red-800",
    dotClass: "bg-red-500",
  },
  warning: {
    label: "警告",
    rowClass: "bg-yellow-50",
    badgeClass: "bg-yellow-100 text-yellow-800",
    dotClass: "bg-yellow-500",
  },
  info: {
    label: "情報",
    rowClass: "",
    badgeClass: "bg-blue-100 text-blue-800",
    dotClass: "bg-blue-400",
  },
};

const STATUS_CONFIG: Record<AlertStatus, { label: string; className: string }> =
  {
    active: { label: "アクティブ", className: "bg-red-100 text-red-700" },
    acknowledged: {
      label: "確認済み",
      className: "bg-yellow-100 text-yellow-700",
    },
    resolved: { label: "解除済み", className: "bg-gray-100 text-gray-600" },
  };

const SENSOR_LABELS: Record<SensorType, string> = {
  temp: "温度",
  humidity: "湿度",
  vibration: "振動",
  gas: "ガス",
  water: "水位",
  power: "電力",
};

export default function IotAlertsPage() {
  const [filterSeverity, setFilterSeverity] = useState<string>("all");
  const [alerts, setAlerts] = useState<IotAlert[]>(MOCK_ALERTS);

  const stats = {
    active: alerts.filter((a) => a.status === "active").length,
    critical: alerts.filter(
      (a) => a.severity === "critical" && a.status === "active",
    ).length,
    today: alerts.filter((a) => a.occurredAt.startsWith("2026-05-24")).length,
    resolved: alerts.filter((a) => a.status === "resolved").length,
  };

  const filtered =
    filterSeverity === "all"
      ? alerts
      : alerts.filter((a) => a.severity === filterSeverity);

  const handleAcknowledge = (id: string) => {
    setAlerts((prev) =>
      prev.map((a) =>
        a.id === id ? { ...a, status: "acknowledged" as AlertStatus } : a,
      ),
    );
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">IoTアラート</h1>
          <p className="text-sm text-gray-500 mt-1">
            IoTセンサー — センサー異常・警報一覧
          </p>
        </div>
        <Bell className="w-8 h-8 text-red-500" />
      </div>

      {/* 統計カード */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Activity className="w-8 h-8 text-red-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">アクティブアラート</p>
            <p className="text-2xl font-bold text-red-600">{stats.active}</p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <AlertTriangle className="w-8 h-8 text-red-600 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">緊急アラート</p>
            <p className="text-2xl font-bold text-red-700">{stats.critical}</p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Bell className="w-8 h-8 text-orange-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">今日のアラート</p>
            <p className="text-2xl font-bold text-orange-600">{stats.today}</p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Thermometer className="w-8 h-8 text-green-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">解除済み</p>
            <p className="text-2xl font-bold text-green-600">
              {stats.resolved}
            </p>
          </div>
        </div>
      </div>

      {/* フィルタ */}
      <div className="bg-white rounded-lg border p-4">
        <div className="flex gap-2 flex-wrap">
          {(["all", "critical", "warning", "info"] as const).map((s) => (
            <button
              key={s}
              onClick={() => setFilterSeverity(s)}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                filterSeverity === s
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              {s === "all" ? "すべて" : SEVERITY_CONFIG[s].label}
            </button>
          ))}
        </div>
      </div>

      {/* アラートテーブル */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  重要度
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  アラートID
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  センサーID
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  設置場所
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  種別
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  値
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  閾値
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  発生日時
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  ステータス
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filtered.map((alert) => (
                <tr
                  key={alert.id}
                  className={`hover:brightness-95 transition-all ${SEVERITY_CONFIG[alert.severity].rowClass}`}
                >
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${SEVERITY_CONFIG[alert.severity].badgeClass}`}
                    >
                      <span
                        className={`w-1.5 h-1.5 rounded-full ${SEVERITY_CONFIG[alert.severity].dotClass}`}
                      />
                      {SEVERITY_CONFIG[alert.severity].label}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-gray-600">
                    ALT-{alert.id.padStart(4, "0")}
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-gray-700 font-medium">
                    {alert.sensorId}
                  </td>
                  <td className="px-4 py-3 text-gray-700 text-xs">
                    {alert.location}
                  </td>
                  <td className="px-4 py-3 text-gray-600">
                    {SENSOR_LABELS[alert.sensorType]}
                  </td>
                  <td className="px-4 py-3 font-semibold text-gray-900">
                    {alert.value}
                  </td>
                  <td className="px-4 py-3 text-gray-500 text-xs">
                    {alert.threshold}
                  </td>
                  <td className="px-4 py-3 text-gray-600 text-xs whitespace-nowrap">
                    {alert.occurredAt}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_CONFIG[alert.status].className}`}
                    >
                      {STATUS_CONFIG[alert.status].label}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {alert.status === "active" && (
                      <button
                        onClick={() => handleAcknowledge(alert.id)}
                        className="px-2 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 whitespace-nowrap"
                      >
                        確認済みにする
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-4 py-3 border-t bg-gray-50 text-xs text-gray-500">
          {filtered.length} 件表示 / 全 {MOCK_ALERTS.length} 件
        </div>
      </div>
    </div>
  );
}
