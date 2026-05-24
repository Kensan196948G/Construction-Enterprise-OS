"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Cpu,
  Activity,
  Thermometer,
  Wind,
  Gauge,
  Zap,
  AlertTriangle,
  CheckCircle,
  WifiOff,
  RefreshCw,
  TrendingUp,
  TrendingDown,
} from "lucide-react";

interface Sensor {
  id: string;
  name: string;
  type: string;
  value: string;
  threshold: string;
  status: "normal" | "warning" | "alert" | "offline";
  battery: number;
  lastUpdate: string;
}

interface SensorGroup {
  project: string;
  sensors: Sensor[];
}

const MOCK_SENSOR_GROUPS: SensorGroup[] = [
  {
    project: "品川タワー新築工事",
    sensors: [
      {
        id: "S-001",
        name: "地盤変位計 #1",
        type: "displacement",
        value: "2.3 mm",
        threshold: "5.0 mm",
        status: "normal",
        battery: 87,
        lastUpdate: "2分前",
      },
      {
        id: "S-002",
        name: "傾斜計 B棟",
        type: "tilt",
        value: "0.12°",
        threshold: "0.5°",
        status: "normal",
        battery: 62,
        lastUpdate: "2分前",
      },
      {
        id: "S-003",
        name: "温度センサー #3",
        type: "temperature",
        value: "34.2°C",
        threshold: "40°C",
        status: "warning",
        battery: 91,
        lastUpdate: "1分前",
      },
      {
        id: "S-004",
        name: "騒音計",
        type: "noise",
        value: "72 dB",
        threshold: "85 dB",
        status: "normal",
        battery: 55,
        lastUpdate: "3分前",
      },
    ],
  },
  {
    project: "川崎物流センター建設",
    sensors: [
      {
        id: "S-010",
        name: "重機振動センサー",
        type: "vibration",
        value: "4.8 gal",
        threshold: "3.0 gal",
        status: "alert",
        battery: 43,
        lastUpdate: "5分前",
      },
      {
        id: "S-011",
        name: "粉塵計",
        type: "dust",
        value: "0.08 mg/m³",
        threshold: "0.15 mg/m³",
        status: "normal",
        battery: 78,
        lastUpdate: "2分前",
      },
      {
        id: "S-012",
        name: "酸素濃度計 坑内",
        type: "oxygen",
        value: "20.8%",
        threshold: "18%",
        status: "normal",
        battery: 95,
        lastUpdate: "1分前",
      },
      {
        id: "S-013",
        name: "電力モニター",
        type: "power",
        value: "45.2 kW",
        threshold: "100 kW",
        status: "offline",
        battery: 0,
        lastUpdate: "2時間前",
      },
    ],
  },
  {
    project: "横浜分譲マンション建設",
    sensors: [
      {
        id: "S-020",
        name: "杭打ち管理センサー",
        type: "pile",
        value: "12.4 m",
        threshold: "13.0 m",
        status: "normal",
        battery: 82,
        lastUpdate: "4分前",
      },
      {
        id: "S-021",
        name: "水位計",
        type: "water",
        value: "1.2 m",
        threshold: "2.0 m",
        status: "normal",
        battery: 71,
        lastUpdate: "3分前",
      },
    ],
  },
];

const statusConfig = {
  normal: {
    label: "正常",
    className: "bg-approve-50 text-approve-700",
    dot: "bg-approve-500",
    icon: CheckCircle,
  },
  warning: {
    label: "警戒",
    className: "bg-safety-50 text-safety-700",
    dot: "bg-safety-500",
    icon: AlertTriangle,
  },
  alert: {
    label: "アラート",
    className: "bg-danger-50 text-danger-700",
    dot: "bg-danger-500",
    icon: AlertTriangle,
  },
  offline: {
    label: "オフライン",
    className: "bg-concrete-50 text-concrete-500",
    dot: "bg-concrete-400",
    icon: WifiOff,
  },
};

const typeIconMap: Record<string, React.ElementType> = {
  displacement: Activity,
  tilt: TrendingDown,
  temperature: Thermometer,
  noise: Wind,
  vibration: Gauge,
  dust: Wind,
  oxygen: Cpu,
  power: Zap,
  pile: TrendingUp,
  water: Activity,
};

export default function IoTPage() {
  const [sensorGroups, setSensorGroups] =
    useState<SensorGroup[]>(MOCK_SENSOR_GROUPS);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const loadData = useCallback(() => {
    setIsLoading(true);
    fetch("/api/v1/iot/devices?per_page=50")
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.success && data?.data?.items?.length > 0) {
          // API items have different shape, keep mock for now
        }
        setLastUpdated(new Date());
      })
      .catch(() => {})
      .finally(() => setIsLoading(false));
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [loadData]);

  const totalSensors = sensorGroups.flatMap((g) => g.sensors);
  const normalCount = totalSensors.filter((s) => s.status === "normal").length;
  const warningCount = totalSensors.filter(
    (s) => s.status === "warning",
  ).length;
  const alertCount = totalSensors.filter((s) => s.status === "alert").length;
  const offlineCount = totalSensors.filter(
    (s) => s.status === "offline",
  ).length;

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">IoT監視</h1>
          <p className="mt-1 text-gray-500 text-sm">
            現場センサー・重機のリアルタイム状態監視
          </p>
        </div>
        <button
          onClick={loadData}
          disabled={isLoading}
          className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
          更新
        </button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <div className="flex items-center gap-3">
            <div className="h-3 w-3 rounded-full bg-approve-500" />
            <div>
              <p className="text-2xl font-bold text-gray-900">{normalCount}</p>
              <p className="text-xs text-gray-500">正常</p>
            </div>
          </div>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <div className="flex items-center gap-3">
            <div className="h-3 w-3 rounded-full bg-safety-500" />
            <div>
              <p className="text-2xl font-bold text-gray-900">{warningCount}</p>
              <p className="text-xs text-gray-500">警戒</p>
            </div>
          </div>
        </div>
        <div className="rounded-xl border border-danger-200 bg-danger-50 p-4">
          <div className="flex items-center gap-3">
            <div className="h-3 w-3 rounded-full bg-danger-500 animate-pulse" />
            <div>
              <p className="text-2xl font-bold text-danger-700">{alertCount}</p>
              <p className="text-xs text-danger-600">アラート</p>
            </div>
          </div>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <div className="flex items-center gap-3">
            <div className="h-3 w-3 rounded-full bg-concrete-400" />
            <div>
              <p className="text-2xl font-bold text-gray-900">{offlineCount}</p>
              <p className="text-xs text-gray-500">オフライン</p>
            </div>
          </div>
        </div>
      </div>

      {/* Alert Banner */}
      {alertCount > 0 && (
        <div className="rounded-xl border border-danger-200 bg-danger-50 p-4 flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-danger-600 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-semibold text-danger-800 text-sm">
              アラート検知: 川崎物流センター 重機振動センサー
            </p>
            <p className="text-xs text-danger-600 mt-1">
              振動値が閾値を超過しています（4.8 gal / 閾値 3.0
              gal）。重機の点検・作業中断を検討してください。
            </p>
          </div>
          <button className="ml-auto flex-shrink-0 text-xs font-medium text-danger-700 border border-danger-300 rounded px-2.5 py-1 hover:bg-danger-100 transition-colors">
            対応する
          </button>
        </div>
      )}

      {/* Sensor Groups */}
      {sensorGroups.map((group) => (
        <div
          key={group.project}
          className="rounded-xl border border-gray-200 bg-white overflow-hidden"
        >
          <div className="px-5 py-4 border-b border-gray-100 bg-gray-50">
            <h2 className="font-bold text-gray-900 text-sm">{group.project}</h2>
            <p className="text-xs text-gray-500 mt-0.5">
              {group.sensors.length} センサー
            </p>
          </div>
          <div className="divide-y divide-gray-100">
            {group.sensors.map((sensor) => {
              const status =
                statusConfig[sensor.status as keyof typeof statusConfig];
              const StatusIcon = status.icon;
              const TypeIcon = typeIconMap[sensor.type] || Cpu;
              return (
                <div
                  key={sensor.id}
                  className="px-5 py-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100 flex-shrink-0">
                      <TypeIcon className="h-5 w-5 text-gray-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-semibold text-gray-900">
                          {sensor.name}
                        </p>
                        <span
                          className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${status.className}`}
                        >
                          <span
                            className={`h-1.5 w-1.5 rounded-full ${status.dot}`}
                          />
                          {status.label}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 mt-0.5">
                        ID: {sensor.id} • 最終更新: {sensor.lastUpdate}
                      </p>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <p
                        className={`text-lg font-bold ${
                          sensor.status === "alert"
                            ? "text-danger-700"
                            : sensor.status === "warning"
                              ? "text-safety-700"
                              : sensor.status === "offline"
                                ? "text-concrete-500"
                                : "text-gray-900"
                        }`}
                      >
                        {sensor.value}
                      </p>
                      <p className="text-xs text-gray-400">
                        閾値: {sensor.threshold}
                      </p>
                    </div>
                    {sensor.status !== "offline" && (
                      <div className="flex-shrink-0 text-right ml-4">
                        <div className="flex items-center gap-1 justify-end">
                          <div className="h-1.5 w-16 rounded-full bg-gray-100">
                            <div
                              className={`h-full rounded-full ${
                                sensor.battery > 50
                                  ? "bg-approve-500"
                                  : sensor.battery > 20
                                    ? "bg-safety-500"
                                    : "bg-danger-500"
                              }`}
                              style={{ width: `${sensor.battery}%` }}
                            />
                          </div>
                          <span className="text-xs text-gray-500 w-8 text-right">
                            {sensor.battery}%
                          </span>
                        </div>
                        <p className="text-xs text-gray-400 mt-0.5">電池残量</p>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
