"use client";

import { useState } from "react";
import { Database, Cloud, Clock, CheckCircle, AlertCircle, Play, Calendar } from "lucide-react";

interface BackupRecord {
  id: string;
  backupId: string;
  type: "full" | "differential" | "incremental";
  startedAt: string;
  completedAt: string | null;
  sizeGB: number;
  status: "success" | "running" | "failed" | "scheduled";
  destination: string;
}

const MOCK_BACKUPS: BackupRecord[] = [
  {
    id: "bk-001",
    backupId: "BK-2026-0524-001",
    type: "incremental",
    startedAt: "2026-05-24 10:00",
    completedAt: "2026-05-24 10:02",
    sizeGB: 0.8,
    status: "success",
    destination: "S3 バケット (東京)",
  },
  {
    id: "bk-002",
    backupId: "BK-2026-0524-002",
    type: "incremental",
    startedAt: "2026-05-24 11:00",
    completedAt: "2026-05-24 11:01",
    sizeGB: 0.6,
    status: "running",
    destination: "S3 バケット (東京)",
  },
  {
    id: "bk-003",
    backupId: "BK-2026-0523-FULL",
    type: "full",
    startedAt: "2026-05-23 02:00",
    completedAt: "2026-05-23 02:48",
    sizeGB: 42.5,
    status: "success",
    destination: "S3 バケット (東京) + テープ",
  },
  {
    id: "bk-004",
    backupId: "BK-2026-0523-DIFF",
    type: "differential",
    startedAt: "2026-05-23 18:00",
    completedAt: "2026-05-23 18:12",
    sizeGB: 5.2,
    status: "success",
    destination: "S3 バケット (東京)",
  },
  {
    id: "bk-005",
    backupId: "BK-2026-0522-DIFF",
    type: "differential",
    startedAt: "2026-05-22 18:00",
    completedAt: "2026-05-22 18:15",
    sizeGB: 6.1,
    status: "success",
    destination: "S3 バケット (東京)",
  },
  {
    id: "bk-006",
    backupId: "BK-2026-0521-FULL",
    type: "full",
    startedAt: "2026-05-21 02:00",
    completedAt: null,
    sizeGB: 0,
    status: "failed",
    destination: "S3 バケット (東京) + テープ",
  },
  {
    id: "bk-007",
    backupId: "BK-2026-0521-DIFF",
    type: "differential",
    startedAt: "2026-05-21 18:00",
    completedAt: "2026-05-21 18:10",
    sizeGB: 4.8,
    status: "success",
    destination: "S3 バケット (東京)",
  },
  {
    id: "bk-008",
    backupId: "BK-2026-0520-DIFF",
    type: "differential",
    startedAt: "2026-05-20 18:00",
    completedAt: "2026-05-20 18:14",
    sizeGB: 5.5,
    status: "success",
    destination: "S3 バケット (東京)",
  },
  {
    id: "bk-009",
    backupId: "BK-2026-0519-FULL",
    type: "full",
    startedAt: "2026-05-19 02:00",
    completedAt: "2026-05-19 02:45",
    sizeGB: 41.8,
    status: "success",
    destination: "S3 バケット (東京) + テープ",
  },
  {
    id: "bk-010",
    backupId: "BK-2026-0519-DIFF",
    type: "differential",
    startedAt: "2026-05-19 18:00",
    completedAt: "2026-05-19 18:11",
    sizeGB: 4.3,
    status: "success",
    destination: "S3 バケット (東京)",
  },
  {
    id: "bk-011",
    backupId: "BK-2026-0518-DIFF",
    type: "differential",
    startedAt: "2026-05-18 18:00",
    completedAt: "2026-05-18 18:08",
    sizeGB: 3.9,
    status: "success",
    destination: "S3 バケット (東京)",
  },
  {
    id: "bk-012",
    backupId: "BK-2026-0524-SCH",
    type: "incremental",
    startedAt: "2026-05-24 12:00",
    completedAt: null,
    sizeGB: 0,
    status: "scheduled",
    destination: "S3 バケット (東京)",
  },
];

const typeLabel: Record<BackupRecord["type"], string> = {
  full: "フルバックアップ",
  differential: "差分バックアップ",
  incremental: "増分バックアップ",
};

const typeStyle: Record<BackupRecord["type"], string> = {
  full: "bg-blue-100 text-blue-700",
  differential: "bg-purple-100 text-purple-700",
  incremental: "bg-gray-100 text-gray-700",
};

const statusStyle: Record<BackupRecord["status"], { label: string; icon: React.ReactNode; className: string }> = {
  success: {
    label: "成功",
    icon: <CheckCircle className="h-3.5 w-3.5" />,
    className: "bg-green-100 text-green-700",
  },
  running: {
    label: "実行中",
    icon: <Play className="h-3.5 w-3.5" />,
    className: "bg-blue-100 text-blue-700",
  },
  failed: {
    label: "失敗",
    icon: <AlertCircle className="h-3.5 w-3.5" />,
    className: "bg-red-100 text-red-700",
  },
  scheduled: {
    label: "スケジュール済",
    icon: <Calendar className="h-3.5 w-3.5" />,
    className: "bg-yellow-100 text-yellow-700",
  },
};

export default function BackupPage() {
  const [isBackingUp, setIsBackingUp] = useState(false);

  const lastFull = MOCK_BACKUPS.find((b) => b.type === "full" && b.status === "success");
  const lastDiff = MOCK_BACKUPS.find((b) => b.type === "differential" && b.status === "success");
  const totalSize = MOCK_BACKUPS.filter((b) => b.status === "success").reduce((s, b) => s + b.sizeGB, 0);

  const handleBackupNow = () => {
    setIsBackingUp(true);
    setTimeout(() => setIsBackingUp(false), 3000);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">バックアップ管理</h1>
          <p className="mt-1 text-sm text-gray-500">
            データバックアップの履歴・スケジュールを管理します
          </p>
        </div>
        <button
          onClick={handleBackupNow}
          disabled={isBackingUp}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60 transition-colors"
        >
          {isBackingUp ? (
            <>
              <Play className="h-4 w-4 animate-pulse" />
              バックアップ中...
            </>
          ) : (
            <>
              <Play className="h-4 w-4" />
              今すぐバックアップ
            </>
          )}
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">最終フルバックアップ</p>
              <p className="mt-1 text-base font-bold text-gray-900">
                {lastFull?.startedAt.split(" ")[0] ?? "—"}
              </p>
            </div>
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50">
              <Database className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <p className="mt-2 text-xs text-gray-400">
            {lastFull ? `サイズ: ${lastFull.sizeGB}GB` : "未実施"}
          </p>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">最終差分バックアップ</p>
              <p className="mt-1 text-base font-bold text-gray-900">
                {lastDiff?.startedAt.split(" ")[0] ?? "—"}
              </p>
            </div>
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-50">
              <Cloud className="h-6 w-6 text-purple-600" />
            </div>
          </div>
          <p className="mt-2 text-xs text-gray-400">
            {lastDiff ? `${lastDiff.startedAt.split(" ")[1]}` : "未実施"}
          </p>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">総バックアップサイズ</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">
                {totalSize.toFixed(1)}
                <span className="ml-1 text-lg font-medium text-gray-500">GB</span>
              </p>
            </div>
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-green-50">
              <Cloud className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <p className="mt-2 text-xs text-gray-400">成功済み合計</p>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">保持期間</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">
                90
                <span className="ml-1 text-lg font-medium text-gray-500">日</span>
              </p>
            </div>
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-orange-50">
              <Clock className="h-6 w-6 text-orange-600" />
            </div>
          </div>
          <p className="mt-2 text-xs text-gray-400">自動削除まで</p>
        </div>
      </div>

      {/* Schedule Settings */}
      <div className="rounded-xl border border-gray-200 bg-white shadow-sm">
        <div className="flex items-center gap-2 border-b border-gray-200 px-6 py-4">
          <Calendar className="h-5 w-5 text-gray-500" />
          <h2 className="text-base font-semibold text-gray-900">スケジュール設定</h2>
        </div>
        <div className="grid grid-cols-1 divide-y divide-gray-100 sm:grid-cols-3 sm:divide-x sm:divide-y-0">
          <div className="px-6 py-5">
            <div className="flex items-center gap-3 mb-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100">
                <Database className="h-4 w-4 text-blue-600" />
              </div>
              <p className="text-sm font-semibold text-gray-900">フルバックアップ</p>
            </div>
            <div className="space-y-2 text-xs text-gray-500">
              <div className="flex justify-between">
                <span>頻度</span>
                <span className="font-medium text-gray-700">週次（日曜日）</span>
              </div>
              <div className="flex justify-between">
                <span>実行時刻</span>
                <span className="font-medium text-gray-700">02:00</span>
              </div>
              <div className="flex justify-between">
                <span>保存先</span>
                <span className="font-medium text-gray-700">S3 + テープ</span>
              </div>
              <div className="flex justify-between">
                <span>保持期間</span>
                <span className="font-medium text-gray-700">90日</span>
              </div>
            </div>
          </div>
          <div className="px-6 py-5">
            <div className="flex items-center gap-3 mb-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-100">
                <Cloud className="h-4 w-4 text-purple-600" />
              </div>
              <p className="text-sm font-semibold text-gray-900">差分バックアップ</p>
            </div>
            <div className="space-y-2 text-xs text-gray-500">
              <div className="flex justify-between">
                <span>頻度</span>
                <span className="font-medium text-gray-700">日次（月〜土）</span>
              </div>
              <div className="flex justify-between">
                <span>実行時刻</span>
                <span className="font-medium text-gray-700">18:00</span>
              </div>
              <div className="flex justify-between">
                <span>保存先</span>
                <span className="font-medium text-gray-700">S3</span>
              </div>
              <div className="flex justify-between">
                <span>保持期間</span>
                <span className="font-medium text-gray-700">30日</span>
              </div>
            </div>
          </div>
          <div className="px-6 py-5">
            <div className="flex items-center gap-3 mb-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gray-100">
                <Clock className="h-4 w-4 text-gray-600" />
              </div>
              <p className="text-sm font-semibold text-gray-900">増分バックアップ</p>
            </div>
            <div className="space-y-2 text-xs text-gray-500">
              <div className="flex justify-between">
                <span>頻度</span>
                <span className="font-medium text-gray-700">毎時</span>
              </div>
              <div className="flex justify-between">
                <span>実行時刻</span>
                <span className="font-medium text-gray-700">:00</span>
              </div>
              <div className="flex justify-between">
                <span>保存先</span>
                <span className="font-medium text-gray-700">S3</span>
              </div>
              <div className="flex justify-between">
                <span>保持期間</span>
                <span className="font-medium text-gray-700">7日</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Backup History */}
      <div className="rounded-xl border border-gray-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <div className="flex items-center gap-2">
            <Database className="h-5 w-5 text-gray-500" />
            <h2 className="text-base font-semibold text-gray-900">バックアップ履歴</h2>
          </div>
          <span className="text-sm text-gray-500">{MOCK_BACKUPS.length}件</span>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">バックアップID</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">種別</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">開始時刻</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">完了時刻</th>
                <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">サイズ</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">ステータス</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">保存先</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
              {MOCK_BACKUPS.map((backup) => {
                const st = statusStyle[backup.status];
                return (
                  <tr key={backup.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <p className="text-sm font-mono text-gray-700">{backup.backupId}</p>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${typeStyle[backup.type]}`}>
                        {typeLabel[backup.type]}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500 whitespace-nowrap">{backup.startedAt}</td>
                    <td className="px-4 py-3 text-sm text-gray-500 whitespace-nowrap">
                      {backup.completedAt ?? "—"}
                    </td>
                    <td className="px-4 py-3 text-right text-sm font-medium text-gray-700">
                      {backup.sizeGB > 0 ? `${backup.sizeGB}GB` : "—"}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ${st.className}`}>
                        {st.icon}
                        {st.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{backup.destination}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
