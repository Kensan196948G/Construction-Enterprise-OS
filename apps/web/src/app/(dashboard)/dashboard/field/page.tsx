"use client";

import { Users, HardHat, Sun, Calendar } from "lucide-react";

const RECENT_ALERTS = {
  safety: [
    { id: 1, msg: "第2工区 安全帯未着用検知", time: "08:42", level: "warning" },
    { id: 2, msg: "重機接近警告 BH-003付近", time: "08:15", level: "critical" },
    { id: 3, msg: "ヘルメット未着用 1名", time: "07:58", level: "warning" },
  ],
  quality: [
    {
      id: 4,
      msg: "コンクリート強度試験 要確認",
      time: "09:00",
      level: "warning",
    },
    { id: 5, msg: "配筋検査 第3工区 合格", time: "08:30", level: "info" },
    { id: 6, msg: "型枠精度 許容値内", time: "07:45", level: "info" },
  ],
  schedule: [
    { id: 7, msg: "掘削工事 2日遅延見込み", time: "08:00", level: "warning" },
    {
      id: 8,
      msg: "コンクリート打設 本日予定通り",
      time: "07:30",
      level: "info",
    },
    { id: 9, msg: "鉄筋工 工程前倒し完了", time: "07:00", level: "info" },
  ],
  iot: [
    { id: 10, msg: "GAS-003 CO濃度上昇警報", time: "08:42", level: "critical" },
    { id: 11, msg: "TEMP-001 高温アラート", time: "09:15", level: "critical" },
    { id: 12, msg: "VIB-007 振動超過検知", time: "08:30", level: "warning" },
  ],
};

const SCHEDULE = [
  { time: "07:00", task: "朝礼・安全確認", workers: 42, status: "完了" },
  { time: "08:00", task: "掘削作業 第3工区", workers: 18, status: "進行中" },
  {
    time: "09:00",
    task: "コンクリート打設 B棟基礎",
    workers: 12,
    status: "進行中",
  },
  { time: "10:30", task: "配筋検査 第2工区", workers: 4, status: "予定" },
  { time: "12:00", task: "昼休憩", workers: 42, status: "予定" },
  { time: "13:00", task: "型枠組立 A棟", workers: 15, status: "予定" },
  { time: "15:00", task: "資材搬入 鉄骨部材", workers: 6, status: "予定" },
  { time: "17:00", task: "片付け・終礼", workers: 42, status: "予定" },
];

const LEVEL_COLORS: Record<string, string> = {
  critical: "border-l-red-500 bg-red-50",
  warning: "border-l-yellow-500 bg-yellow-50",
  info: "border-l-blue-400 bg-blue-50",
};

const SCHEDULE_STATUS: Record<string, string> = {
  完了: "bg-green-100 text-green-800",
  進行中: "bg-blue-100 text-blue-800",
  予定: "bg-gray-100 text-gray-600",
};

export default function FieldDashboardPage() {
  const stats = [
    {
      label: "今日の作業員数",
      value: "42名",
      icon: Users,
      color: "text-blue-600",
      bg: "bg-blue-50",
    },
    {
      label: "稼働重機数",
      value: "6台",
      icon: HardHat,
      color: "text-orange-600",
      bg: "bg-orange-50",
    },
    {
      label: "作業指示数",
      value: "18件",
      icon: Calendar,
      color: "text-purple-600",
      bg: "bg-purple-50",
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            現場ダッシュボード
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            ダッシュボード — 本日の作業状況・アラート
          </p>
        </div>
        <HardHat className="w-8 h-8 text-orange-500" />
      </div>

      {/* サマリーカード */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {stats.map((s) => {
          const Icon = s.icon;
          return (
            <div
              key={s.label}
              className="bg-white rounded-lg border p-4 flex items-center gap-4"
            >
              <div
                className={`w-12 h-12 rounded-lg ${s.bg} flex items-center justify-center shrink-0`}
              >
                <Icon className={`w-6 h-6 ${s.color}`} />
              </div>
              <div>
                <p className="text-xs text-gray-500">{s.label}</p>
                <p className="text-2xl font-bold text-gray-900">{s.value}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* 天気情報 */}
      <div className="bg-white rounded-lg border p-4">
        <h2 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <Sun className="w-4 h-4 text-yellow-500" />
          本日の気象情報
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
          <div>
            <p className="text-3xl">☀️</p>
            <p className="text-xs text-gray-500 mt-1">天気</p>
            <p className="font-semibold text-gray-800">晴れ</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-orange-500">28.4°C</p>
            <p className="text-xs text-gray-500 mt-1">気温</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-blue-500">62%</p>
            <p className="text-xs text-gray-500 mt-1">湿度</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-teal-500">3.2 m/s</p>
            <p className="text-xs text-gray-500 mt-1">風速</p>
          </div>
          <div>
            <span className="inline-block px-3 py-1 bg-green-100 text-green-800 text-sm font-semibold rounded-full mt-1">
              作業適 ✓
            </span>
            <p className="text-xs text-gray-500 mt-1">作業適性</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 直近アラート */}
        <div className="space-y-4">
          <h2 className="font-semibold text-gray-700">直近アラート</h2>
          {(
            [
              { key: "safety", label: "安全" },
              { key: "quality", label: "品質" },
              { key: "schedule", label: "工程" },
              { key: "iot", label: "IoT" },
            ] as const
          ).map(({ key, label }) => (
            <div
              key={key}
              className="bg-white rounded-lg border overflow-hidden"
            >
              <div className="px-3 py-2 bg-gray-50 border-b">
                <span className="font-medium text-gray-700 text-sm">
                  {label}アラート
                </span>
              </div>
              <div className="divide-y">
                {RECENT_ALERTS[key].map((alert) => (
                  <div
                    key={alert.id}
                    className={`px-3 py-2 border-l-4 text-sm ${LEVEL_COLORS[alert.level]}`}
                  >
                    <div className="flex justify-between items-start gap-2">
                      <span className="text-gray-800">{alert.msg}</span>
                      <span className="text-xs text-gray-400 shrink-0">
                        {alert.time}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* 今日のスケジュール */}
        <div>
          <h2 className="font-semibold text-gray-700 mb-4">
            今日のスケジュール
          </h2>
          <div className="bg-white rounded-lg border overflow-hidden">
            <div className="divide-y">
              {SCHEDULE.map((item) => (
                <div
                  key={item.time}
                  className="flex items-center gap-4 px-4 py-3"
                >
                  <span className="font-mono text-sm text-gray-500 w-12 shrink-0">
                    {item.time}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 text-sm truncate">
                      {item.task}
                    </p>
                    <p className="text-xs text-gray-400">{item.workers}名</p>
                  </div>
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium shrink-0 ${SCHEDULE_STATUS[item.status]}`}
                  >
                    {item.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
