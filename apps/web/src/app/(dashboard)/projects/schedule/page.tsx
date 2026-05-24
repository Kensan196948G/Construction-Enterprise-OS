"use client";

import { useState } from "react";
import { Calendar, Clock, CheckCircle, AlertTriangle } from "lucide-react";

const TASKS = [
  { id: 1, name: "基礎掘削工事", assignee: "田中 健一", start: "2024-04-01", end: "2024-04-20", duration: 19, progress: 100, status: "completed", predecessor: null },
  { id: 2, name: "捨てコンクリート打設", assignee: "鈴木 次郎", start: "2024-04-21", end: "2024-04-25", duration: 4, progress: 100, status: "completed", predecessor: 1 },
  { id: 3, name: "基礎配筋工事", assignee: "佐藤 三郎", start: "2024-04-26", end: "2024-05-15", duration: 19, progress: 100, status: "completed", predecessor: 2 },
  { id: 4, name: "基礎コンクリート打設", assignee: "田中 健一", start: "2024-05-16", end: "2024-05-25", duration: 9, progress: 100, status: "completed", predecessor: 3 },
  { id: 5, name: "地上躯体工事（1F）", assignee: "山田 五郎", start: "2024-06-01", end: "2024-07-15", duration: 44, progress: 85, status: "in-progress", predecessor: 4 },
  { id: 6, name: "地上躯体工事（2F）", assignee: "山田 五郎", start: "2024-07-16", end: "2024-08-31", duration: 46, progress: 40, status: "in-progress", predecessor: 5 },
  { id: 7, name: "地上躯体工事（3F）", assignee: "山田 五郎", start: "2024-09-01", end: "2024-10-15", duration: 44, progress: 0, status: "planned", predecessor: 6 },
  { id: 8, name: "屋根工事", assignee: "木村 七海", start: "2024-10-16", end: "2024-11-10", duration: 25, progress: 0, status: "planned", predecessor: 7 },
  { id: 9, name: "外壁工事", assignee: "中村 八郎", start: "2024-10-20", end: "2024-12-15", duration: 56, progress: 0, status: "planned", predecessor: 7 },
  { id: 10, name: "内装工事", assignee: "小林 九子", start: "2024-11-01", end: "2025-01-31", duration: 91, progress: 0, status: "planned", predecessor: 8 },
  { id: 11, name: "設備工事（電気）", assignee: "加藤 十蔵", start: "2024-11-15", end: "2025-02-28", duration: 105, progress: 0, status: "planned", predecessor: 9 },
  { id: 12, name: "竣工検査・引き渡し", assignee: "田中 健一", start: "2025-03-01", end: "2025-03-31", duration: 30, progress: 0, status: "planned", predecessor: 11 },
];

const MILESTONES = [
  { id: 1, name: "基礎工事完了", planned: "2024-05-25", actual: "2024-05-24", achieved: true },
  { id: 2, name: "躯体工事（1F）完了", planned: "2024-07-15", actual: "2024-07-18", achieved: true },
  { id: 3, name: "上棟式", planned: "2024-10-31", actual: null, achieved: false },
  { id: 4, name: "外装工事完了", planned: "2024-12-15", actual: null, achieved: false },
  { id: 5, name: "竣工・引き渡し", planned: "2025-03-31", actual: null, achieved: false },
];

const STATUS_STYLES: Record<string, string> = {
  completed: "bg-green-100 text-green-800",
  "in-progress": "bg-blue-100 text-blue-800",
  delayed: "bg-red-100 text-red-800",
  planned: "bg-gray-100 text-gray-700",
};

const STATUS_LABELS: Record<string, string> = {
  completed: "完了",
  "in-progress": "進行中",
  delayed: "遅延",
  planned: "予定",
};

export default function SchedulePage() {
  const [activeTab, setActiveTab] = useState<"tasks" | "milestones">("tasks");

  const totalTasks = TASKS.length;
  const completedTasks = TASKS.filter((t) => t.status === "completed").length;
  const delayedTasks = TASKS.filter((t) => t.status === "delayed").length;
  const thisWeekTasks = TASKS.filter((t) => t.status === "in-progress").length;

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">工程管理</h1>
          <p className="text-sm text-gray-500 mt-1">品川タワー新築工事 — ガントチャート・マイルストーン管理</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
          工程更新
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-blue-50 rounded-lg">
            <Calendar className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">総タスク数</p>
            <p className="text-2xl font-bold text-gray-900">{totalTasks}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-green-50 rounded-lg">
            <CheckCircle className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">完了</p>
            <p className="text-2xl font-bold text-gray-900">{completedTasks}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-red-50 rounded-lg">
            <AlertTriangle className="w-5 h-5 text-red-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">遅延</p>
            <p className="text-2xl font-bold text-gray-900">{delayedTasks}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-orange-50 rounded-lg">
            <Clock className="w-5 h-5 text-orange-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">今週完了予定</p>
            <p className="text-2xl font-bold text-gray-900">{thisWeekTasks}</p>
          </div>
        </div>
      </div>

      <div className="border-b border-gray-200">
        <nav className="flex gap-6">
          <button
            onClick={() => setActiveTab("tasks")}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === "tasks"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            タスク一覧 / ガントバー
          </button>
          <button
            onClick={() => setActiveTab("milestones")}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === "milestones"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            マイルストーン
          </button>
        </nav>
      </div>

      {activeTab === "tasks" && (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">No.</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">タスク名</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">担当者</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">開始日</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">終了日</th>
                  <th className="px-4 py-3 text-center font-semibold text-gray-600 whitespace-nowrap">期間(日)</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap w-44">進捗</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">ステータス</th>
                  <th className="px-4 py-3 text-center font-semibold text-gray-600 whitespace-nowrap">先行</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {TASKS.map((task) => (
                  <tr key={task.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-500 whitespace-nowrap">{task.id}</td>
                    <td className="px-4 py-3 font-medium text-gray-900 whitespace-nowrap">{task.name}</td>
                    <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{task.assignee}</td>
                    <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{task.start}</td>
                    <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{task.end}</td>
                    <td className="px-4 py-3 text-gray-600 whitespace-nowrap text-center">{task.duration}</td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2 min-w-[80px]">
                          <div
                            className="bg-blue-500 h-2 rounded-full"
                            style={{ width: `${task.progress}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-600 w-8 text-right">{task.progress}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_STYLES[task.status]}`}>
                        {STATUS_LABELS[task.status]}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-500 whitespace-nowrap text-center">
                      {task.predecessor ?? "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === "milestones" && (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th className="px-4 py-3 text-left font-semibold text-gray-600">マイルストーン名</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-600">予定日</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-600">実際日</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-600">達成状況</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {MILESTONES.map((ms) => (
                  <tr key={ms.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{ms.name}</td>
                    <td className="px-4 py-3 text-gray-600">{ms.planned}</td>
                    <td className="px-4 py-3 text-gray-600">{ms.actual ?? "—"}</td>
                    <td className="px-4 py-3">
                      {ms.achieved ? (
                        <span className="flex items-center gap-1 text-green-700 text-xs font-medium">
                          <CheckCircle className="w-4 h-4" /> 達成済み
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-gray-400 text-xs font-medium">
                          <Clock className="w-4 h-4" /> 未達成
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
