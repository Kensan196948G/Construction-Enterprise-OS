"use client";

import { useState, useCallback, useEffect } from "react";
import {
  Bot,
  Zap,
  Clock,
  CheckCircle,
  AlertCircle,
  Plus,
  Play,
  Pause,
} from "lucide-react";

interface RpaTask {
  id: string;
  name: string;
  targetProcess: string;
  schedule: string;
  lastRun: string;
  lastResult: "success" | "failed" | "running" | "idle";
  timeSavedMin: number;
  runCountThisMonth: number;
  isActive: boolean;
}

const MOCK_TASKS: RpaTask[] = [
  {
    id: "T-001",
    name: "請求書自動処理",
    targetProcess: "請求書PDF取込・仕訳起票・承認依頼送信",
    schedule: "毎日 08:00",
    lastRun: "2026-05-24 08:00",
    lastResult: "success",
    timeSavedMin: 45,
    runCountThisMonth: 24,
    isActive: true,
  },
  {
    id: "T-002",
    name: "日報自動集計",
    targetProcess: "現場日報PDF→Excel集計→管理者メール送信",
    schedule: "毎日 18:30",
    lastRun: "2026-05-23 18:30",
    lastResult: "success",
    timeSavedMin: 30,
    runCountThisMonth: 23,
    isActive: true,
  },
  {
    id: "T-003",
    name: "週次工程レポート",
    targetProcess: "工程データ取得→グラフ生成→PDF作成→配信",
    schedule: "毎週月曜 07:00",
    lastRun: "2026-05-20 07:00",
    lastResult: "success",
    timeSavedMin: 90,
    runCountThisMonth: 4,
    isActive: true,
  },
  {
    id: "T-004",
    name: "入退場記録転記",
    targetProcess: "入退場ゲートログ→台帳Excel自動転記",
    schedule: "毎日 19:00",
    lastRun: "2026-05-24 09:15",
    lastResult: "running",
    timeSavedMin: 20,
    runCountThisMonth: 24,
    isActive: true,
  },
  {
    id: "T-005",
    name: "書類フォーマット変換",
    targetProcess: "旧形式PDF→新形式テンプレートへ自動変換",
    schedule: "随時（ファイル検知）",
    lastRun: "2026-05-24 11:42",
    lastResult: "success",
    timeSavedMin: 15,
    runCountThisMonth: 38,
    isActive: true,
  },
  {
    id: "T-006",
    name: "発注書自動作成",
    targetProcess: "承認済み見積→発注書PDF生成→メール送付",
    schedule: "毎日 10:00・15:00",
    lastRun: "2026-05-24 10:00",
    lastResult: "failed",
    timeSavedMin: 35,
    runCountThisMonth: 18,
    isActive: false,
  },
  {
    id: "T-007",
    name: "安全パトロール記録集計",
    targetProcess: "点検アプリデータ→月次安全報告書自動生成",
    schedule: "毎月末 17:00",
    lastRun: "2026-04-30 17:00",
    lastResult: "success",
    timeSavedMin: 120,
    runCountThisMonth: 1,
    isActive: true,
  },
  {
    id: "T-008",
    name: "協力会社評価集計",
    targetProcess: "工事完了通知受信→評価フォーム自動配信",
    schedule: "随時（完了通知検知）",
    lastRun: "2026-05-22 14:20",
    lastResult: "success",
    timeSavedMin: 25,
    runCountThisMonth: 7,
    isActive: true,
  },
];

const RESULT_CONFIG = {
  success: {
    label: "成功",
    color: "bg-green-100 text-green-700",
    icon: CheckCircle,
  },
  failed: {
    label: "失敗",
    color: "bg-red-100 text-red-700",
    icon: AlertCircle,
  },
  running: { label: "実行中", color: "bg-blue-100 text-blue-700", icon: Zap },
  idle: { label: "待機中", color: "bg-gray-100 text-gray-600", icon: Clock },
};

export default function RpaPage() {
  const [tasks, setTasks] = useState<RpaTask[]>(MOCK_TASKS);
  const [loading, setLoading] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/v1/autonomous/rpa-tasks?per_page=50");
      const json = await res.json();
      const items: Record<string, unknown>[] =
        json?.data?.items ?? json?.items ?? [];
      if (Array.isArray(items) && items.length > 0) {
        setTasks(
          items.map((item: Record<string, unknown>) => ({
            id: String(item.id ?? ""),
            name: String(item.name ?? ""),
            targetProcess: String(
              item.targetProcess ?? item.target_process ?? "",
            ),
            schedule: String(item.schedule ?? ""),
            lastRun: String(item.lastRun ?? item.last_run ?? ""),
            lastResult: String(
              item.lastResult ?? item.last_result ?? "idle",
            ) as RpaTask["lastResult"],
            timeSavedMin: Number(item.timeSavedMin ?? item.time_saved_min ?? 0),
            runCountThisMonth: Number(
              item.runCountThisMonth ?? item.run_count_this_month ?? 0,
            ),
            isActive: Boolean(item.isActive ?? item.is_active ?? false),
          })),
        );
      }
    } catch {
      setTasks(MOCK_TASKS);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const activeTasks = tasks.filter((t) => t.isActive).length;
  const totalRunsThisMonth = tasks.reduce((s, t) => s + t.runCountThisMonth, 0);
  const totalTimeSavedMin = tasks.reduce(
    (s, t) => s + t.timeSavedMin * t.runCountThisMonth,
    0,
  );
  const successRate = Math.round(
    (tasks.filter((t) => t.lastResult === "success").length / tasks.length) *
      100,
  );

  const timeSavedHours = Math.floor(totalTimeSavedMin / 60);
  const timeSavedMins = totalTimeSavedMin % 60;

  return (
    <div className="p-6 space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">RPA自動化</h1>
          <p className="text-sm text-gray-500 mt-1">
            定型業務の自動化タスク管理
          </p>
        </div>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm">
          <Plus className="w-4 h-4" />
          タスク追加
        </button>
      </div>

      {/* 統計カード */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-50 rounded-lg">
              <Bot className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">実行中タスク数</p>
              <p className="text-2xl font-bold text-gray-900">
                {loading ? "—" : activeTasks}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-50 rounded-lg">
              <Zap className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">今月実行回数</p>
              <p className="text-2xl font-bold text-gray-900">
                {loading ? "—" : totalRunsThisMonth}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-50 rounded-lg">
              <Clock className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">削減工数</p>
              <p className="text-xl font-bold text-gray-900">
                {loading ? "—" : `${timeSavedHours}h${timeSavedMins}m`}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-50 rounded-lg">
              <CheckCircle className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">成功率</p>
              <p className="text-2xl font-bold text-gray-900">
                {loading ? "—" : `${successRate}%`}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 削減効果サマリー */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-xl p-5 text-white">
        <div className="flex items-center gap-2 mb-3">
          <Bot className="w-5 h-5" />
          <h2 className="font-semibold">今月の自動化効果</h2>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-blue-200 text-xs">自動実行回数</p>
            <p className="text-2xl font-bold">{totalRunsThisMonth}回</p>
          </div>
          <div>
            <p className="text-blue-200 text-xs">削減工数（推定）</p>
            <p className="text-2xl font-bold">
              {timeSavedHours}時間
              {timeSavedMins > 0 ? `${timeSavedMins}分` : ""}
            </p>
          </div>
          <div>
            <p className="text-blue-200 text-xs">人件費削減（推定）</p>
            <p className="text-2xl font-bold">
              ¥{Math.round((totalTimeSavedMin / 60) * 3000).toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {/* タスク一覧テーブル */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h2 className="font-semibold text-gray-800">RPAタスク一覧</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  タスク名
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  自動化対象業務
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  実行スケジュール
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  最終実行
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  実行結果
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  今月実行
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  1回あたり節約
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  状態
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {tasks.map((task) => {
                const ResultIcon = RESULT_CONFIG[task.lastResult].icon;
                return (
                  <tr
                    key={task.id}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-4 py-3 font-medium text-gray-900">
                      {task.name}
                    </td>
                    <td className="px-4 py-3 text-gray-600 text-xs max-w-[200px]">
                      {task.targetProcess}
                    </td>
                    <td className="px-4 py-3 text-gray-600 text-xs whitespace-nowrap">
                      {task.schedule}
                    </td>
                    <td className="px-4 py-3 text-gray-500 text-xs whitespace-nowrap">
                      {task.lastRun}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium w-fit ${RESULT_CONFIG[task.lastResult].color}`}
                      >
                        <ResultIcon className="w-3 h-3" />
                        {RESULT_CONFIG[task.lastResult].label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-700 text-center">
                      {task.runCountThisMonth}回
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1 text-green-600 text-xs font-medium">
                        <Clock className="w-3 h-3" />
                        {task.timeSavedMin}分
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <button
                        className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors ${
                          task.isActive
                            ? "bg-green-50 text-green-700 hover:bg-green-100"
                            : "bg-gray-50 text-gray-500 hover:bg-gray-100"
                        }`}
                      >
                        {task.isActive ? (
                          <>
                            <Play className="w-3 h-3" />
                            有効
                          </>
                        ) : (
                          <>
                            <Pause className="w-3 h-3" />
                            停止中
                          </>
                        )}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div className="px-4 py-3 border-t border-gray-100 text-sm text-gray-500">
          {tasks.length}件（有効: {activeTasks}件）
        </div>
      </div>
    </div>
  );
}
