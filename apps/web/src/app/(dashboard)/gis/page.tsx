"use client";

import { useState, useEffect } from "react";
import {
  Map,
  MapPin,
  Layers,
  Navigation,
  AlertTriangle,
  HardHat,
  Truck,
  ZoomIn,
  ZoomOut,
  Search,
} from "lucide-react";

const mapLayers = [
  { id: "sites", label: "工事現場", active: true, color: "primary" },
  { id: "safety", label: "安全区域", active: true, color: "safety" },
  { id: "underground", label: "地下埋設物", active: false, color: "danger" },
  { id: "transport", label: "搬入ルート", active: true, color: "approve" },
  { id: "equipment", label: "重機位置", active: true, color: "site" },
];

interface SitePin {
  id: number;
  name: string;
  lat: number;
  lng: number;
  status: string;
  workers: number;
  alerts: number;
}

const MOCK_SITE_PINS: SitePin[] = [
  {
    id: 1,
    name: "品川タワー新築工事",
    lat: 35.6285,
    lng: 139.7387,
    status: "active",
    workers: 42,
    alerts: 0,
  },
  {
    id: 2,
    name: "横浜分譲マンション建設",
    lat: 35.4437,
    lng: 139.638,
    status: "active",
    workers: 28,
    alerts: 0,
  },
  {
    id: 3,
    name: "大田区道路改良工事",
    lat: 35.5614,
    lng: 139.7161,
    status: "active",
    workers: 15,
    alerts: 0,
  },
  {
    id: 4,
    name: "川崎物流センター建設",
    lat: 35.531,
    lng: 139.7025,
    status: "alert",
    workers: 33,
    alerts: 3,
  },
  {
    id: 5,
    name: "新宿再開発ビル工事",
    lat: 35.6895,
    lng: 139.6917,
    status: "planning",
    workers: 0,
    alerts: 0,
  },
];

const nearbyAlerts = [
  {
    type: "weather",
    message: "強風警報 — 高所作業中止を推奨 (14:00〜18:00)",
    severity: "warning",
    site: "品川タワー",
  },
  {
    type: "equipment",
    message: "重機振動異常 — センサーS-010 閾値超過",
    severity: "alert",
    site: "川崎物流センター",
  },
  {
    type: "traffic",
    message: "搬入ルート渋滞 — 国道15号線 事故処理中",
    severity: "info",
    site: "横浜マンション",
  },
];

const equipment = [
  {
    id: "EQ-001",
    name: "タワークレーン TC-200",
    site: "品川タワー新築工事",
    status: "operating",
    operator: "木村 一郎",
  },
  {
    id: "EQ-002",
    name: "油圧ショベル ZX350",
    site: "川崎物流センター建設",
    status: "alert",
    operator: "加藤 二郎",
  },
  {
    id: "EQ-003",
    name: "コンクリートポンプ車",
    site: "横浜分譲マンション建設",
    status: "standby",
    operator: "松本 三郎",
  },
  {
    id: "EQ-004",
    name: "バックホウ PC200",
    site: "大田区道路改良工事",
    status: "operating",
    operator: "井上 四郎",
  },
];

const equipmentStatus = {
  operating: { label: "稼働中", className: "bg-approve-50 text-approve-700" },
  standby: { label: "待機中", className: "bg-concrete-50 text-concrete-600" },
  alert: { label: "要確認", className: "bg-danger-50 text-danger-700" },
};

export default function GISPage() {
  const [sitePins, setSitePins] = useState<SitePin[]>(MOCK_SITE_PINS);

  useEffect(() => {
    fetch("/api/v1/gis/sites")
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.success && data?.data?.items?.length > 0) {
          const mapped: SitePin[] = data.data.items.map(
            (s: {
              id: number;
              name: string;
              latitude?: number;
              longitude?: number;
              status?: string;
              worker_count?: number;
              alert_count?: number;
            }) => ({
              id: s.id,
              name: s.name,
              lat: s.latitude ?? 35.6,
              lng: s.longitude ?? 139.7,
              status: s.status ?? "active",
              workers: s.worker_count ?? 0,
              alerts: s.alert_count ?? 0,
            }),
          );
          setSitePins(mapped);
        }
      })
      .catch(() => {});
  }, []);

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">GIS・現場マップ</h1>
          <p className="mt-1 text-gray-500 text-sm">
            工事現場・重機位置・安全区域のリアルタイム地図管理
          </p>
        </div>
        <div className="flex gap-2">
          <button className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
            <Layers className="h-4 w-4" />
            レイヤー管理
          </button>
          <button className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-700 transition-colors">
            <Navigation className="h-4 w-4" />
            現在地
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map Placeholder */}
        <div className="lg:col-span-2 space-y-4">
          {/* Map Container */}
          <div
            className="relative rounded-xl border border-gray-200 bg-white overflow-hidden"
            style={{ height: "480px" }}
          >
            {/* Map background simulation */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-green-50 to-gray-100">
              {/* Simulated map grid */}
              <svg
                className="absolute inset-0 w-full h-full opacity-20"
                xmlns="http://www.w3.org/2000/svg"
              >
                <defs>
                  <pattern
                    id="grid"
                    width="40"
                    height="40"
                    patternUnits="userSpaceOnUse"
                  >
                    <path
                      d="M 40 0 L 0 0 0 40"
                      fill="none"
                      stroke="#94a3b8"
                      strokeWidth="0.5"
                    />
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#grid)" />
              </svg>

              {/* Simulated roads */}
              <svg
                className="absolute inset-0 w-full h-full"
                xmlns="http://www.w3.org/2000/svg"
              >
                <line
                  x1="0"
                  y1="240"
                  x2="100%"
                  y2="240"
                  stroke="#e2e8f0"
                  strokeWidth="6"
                />
                <line
                  x1="0"
                  y1="200"
                  x2="100%"
                  y2="300"
                  stroke="#e2e8f0"
                  strokeWidth="4"
                />
                <line
                  x1="200"
                  y1="0"
                  x2="200"
                  y2="100%"
                  stroke="#e2e8f0"
                  strokeWidth="6"
                />
                <line
                  x1="400"
                  y1="0"
                  x2="350"
                  y2="100%"
                  stroke="#e2e8f0"
                  strokeWidth="4"
                />
                <line
                  x1="0"
                  y1="350"
                  x2="100%"
                  y2="380"
                  stroke="#e2e8f0"
                  strokeWidth="3"
                />
                {/* Road labels */}
                <text x="10" y="235" fill="#94a3b8" fontSize="10">
                  国道15号線
                </text>
                <text x="205" y="120" fill="#94a3b8" fontSize="10">
                  第一京浜
                </text>
              </svg>

              {/* Site pins */}
              {sitePins.map((pin, i) => {
                const positions = [
                  { top: "20%", left: "55%" },
                  { top: "65%", left: "30%" },
                  { top: "45%", left: "45%" },
                  { top: "50%", left: "40%" },
                  { top: "15%", left: "42%" },
                ];
                const pos = positions[i % positions.length];
                return (
                  <div
                    key={pin.id}
                    className="absolute transform -translate-x-1/2 -translate-y-full cursor-pointer group"
                    style={pos}
                  >
                    <div
                      className={`flex h-8 w-8 items-center justify-center rounded-full shadow-lg ${
                        pin.status === "alert"
                          ? "bg-danger-500"
                          : pin.status === "planning"
                            ? "bg-primary-300"
                            : "bg-primary-600"
                      }`}
                    >
                      {pin.status === "alert" ? (
                        <AlertTriangle className="h-4 w-4 text-white" />
                      ) : (
                        <HardHat className="h-4 w-4 text-white" />
                      )}
                    </div>
                    {/* Tooltip */}
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block z-10">
                      <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-2 text-xs whitespace-nowrap">
                        <p className="font-semibold text-gray-900">
                          {pin.name}
                        </p>
                        <p className="text-gray-500">{pin.workers}名 作業中</p>
                        {pin.alerts > 0 && (
                          <p className="text-danger-600">
                            {pin.alerts}件 アラート
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* Equipment markers */}
              <div className="absolute" style={{ top: "28%", left: "52%" }}>
                <div className="flex h-6 w-6 items-center justify-center rounded bg-site-500 shadow">
                  <Truck className="h-3 w-3 text-white" />
                </div>
              </div>
              <div className="absolute" style={{ top: "47%", left: "37%" }}>
                <div className="flex h-6 w-6 items-center justify-center rounded bg-danger-500 shadow animate-pulse">
                  <Truck className="h-3 w-3 text-white" />
                </div>
              </div>
            </div>

            {/* Map Controls */}
            <div className="absolute top-4 right-4 flex flex-col gap-2">
              <button className="flex h-8 w-8 items-center justify-center rounded-lg bg-white border border-gray-200 shadow hover:bg-gray-50 transition-colors">
                <ZoomIn className="h-4 w-4 text-gray-700" />
              </button>
              <button className="flex h-8 w-8 items-center justify-center rounded-lg bg-white border border-gray-200 shadow hover:bg-gray-50 transition-colors">
                <ZoomOut className="h-4 w-4 text-gray-700" />
              </button>
            </div>

            {/* Search Box */}
            <div className="absolute top-4 left-4 w-64">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="場所・工事を検索..."
                  className="w-full rounded-lg border border-gray-200 bg-white pl-9 pr-3 py-2 text-sm shadow focus:outline-none focus:border-primary-500"
                />
              </div>
            </div>

            {/* Legend */}
            <div className="absolute bottom-4 left-4 bg-white rounded-lg border border-gray-200 shadow p-3 text-xs">
              <p className="font-semibold text-gray-700 mb-2">凡例</p>
              <div className="space-y-1.5">
                <div className="flex items-center gap-2">
                  <div className="h-4 w-4 rounded-full bg-primary-600" />
                  <span className="text-gray-600">施工中現場</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-4 w-4 rounded-full bg-danger-500" />
                  <span className="text-gray-600">アラート発生</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-4 w-4 rounded-full bg-primary-300" />
                  <span className="text-gray-600">計画中現場</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-4 w-4 rounded bg-site-500" />
                  <span className="text-gray-600">重機</span>
                </div>
              </div>
            </div>

            {/* Map attribution */}
            <div className="absolute bottom-4 right-4 text-[10px] text-gray-400">
              地図データ © Construction-Enterprise-OS
            </div>
          </div>

          {/* Layer Controls */}
          <div className="rounded-xl border border-gray-200 bg-white p-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">
              表示レイヤー
            </h3>
            <div className="flex flex-wrap gap-2">
              {mapLayers.map((layer) => (
                <label
                  key={layer.id}
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <div
                    className={`relative inline-flex h-5 w-9 items-center rounded-full ${
                      layer.active ? `bg-${layer.color}-500` : "bg-gray-200"
                    } transition-colors`}
                  >
                    <span
                      className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform ${
                        layer.active ? "translate-x-4.5" : "translate-x-0.5"
                      }`}
                    />
                  </div>
                  <span className="text-sm text-gray-700">{layer.label}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Right Panel */}
        <div className="space-y-4">
          {/* Alerts */}
          <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-100">
              <h3 className="font-bold text-gray-900 text-sm">
                エリアアラート
              </h3>
            </div>
            <div className="divide-y divide-gray-100">
              {nearbyAlerts.map((alert, i) => (
                <div key={i} className="px-4 py-3">
                  <div className={`flex items-start gap-2`}>
                    <AlertTriangle
                      className={`h-4 w-4 mt-0.5 flex-shrink-0 ${
                        alert.severity === "alert"
                          ? "text-danger-500"
                          : alert.severity === "warning"
                            ? "text-safety-500"
                            : "text-primary-500"
                      }`}
                    />
                    <div>
                      <p className="text-xs font-semibold text-gray-800">
                        {alert.site}
                      </p>
                      <p className="text-xs text-gray-600 mt-0.5 leading-relaxed">
                        {alert.message}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Equipment List */}
          <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-100">
              <h3 className="font-bold text-gray-900 text-sm">重機位置</h3>
            </div>
            <div className="divide-y divide-gray-100">
              {equipment.map((eq) => {
                const status =
                  equipmentStatus[eq.status as keyof typeof equipmentStatus];
                return (
                  <div
                    key={eq.id}
                    className="px-4 py-3 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="text-xs font-semibold text-gray-900">
                          {eq.name}
                        </p>
                        <p className="text-xs text-gray-500 mt-0.5">
                          {eq.site}
                        </p>
                        <p className="text-xs text-gray-400">
                          操作: {eq.operator}
                        </p>
                      </div>
                      <span
                        className={`flex-shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${status.className}`}
                      >
                        {status.label}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Site List */}
          <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-100">
              <h3 className="font-bold text-gray-900 text-sm">工事現場一覧</h3>
            </div>
            <div className="divide-y divide-gray-100">
              {sitePins.map((site) => (
                <div
                  key={site.id}
                  className="px-4 py-3 hover:bg-gray-50 transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <MapPin
                      className={`h-4 w-4 flex-shrink-0 ${
                        site.status === "alert"
                          ? "text-danger-500"
                          : site.status === "planning"
                            ? "text-gray-400"
                            : "text-primary-500"
                      }`}
                    />
                    <div>
                      <p className="text-xs font-semibold text-gray-900">
                        {site.name}
                      </p>
                      {site.workers > 0 && (
                        <p className="text-xs text-gray-500">
                          {site.workers}名 作業中
                        </p>
                      )}
                    </div>
                    {site.alerts > 0 && (
                      <span className="ml-auto text-xs bg-danger-500 text-white rounded-full px-1.5">
                        {site.alerts}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
