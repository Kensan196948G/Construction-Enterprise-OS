"use client";

import { useState } from "react";
import { Star, BarChart3, Award, ClipboardCheck, Search } from "lucide-react";

interface Evaluation {
  id: string;
  companyName: string;
  projectName: string;
  period: string;
  qualityScore: number;
  safetyScore: number;
  costScore: number;
  scheduleScore: number;
  totalScore: number;
  evaluator: string;
  grade: "A" | "B" | "C" | "D";
}

const MOCK_EVALUATIONS: Evaluation[] = [
  {
    id: "E-001",
    companyName: "山田建設株式会社",
    projectName: "品川タワー新築工事",
    period: "2026年1月〜3月",
    qualityScore: 92,
    safetyScore: 95,
    costScore: 88,
    scheduleScore: 90,
    totalScore: 91,
    evaluator: "工事部長 鈴木",
    grade: "A",
  },
  {
    id: "E-002",
    companyName: "鈴木電気工業",
    projectName: "大阪ビル改修工事",
    period: "2026年2月〜4月",
    qualityScore: 85,
    safetyScore: 88,
    costScore: 82,
    scheduleScore: 84,
    totalScore: 85,
    evaluator: "現場監督 田中",
    grade: "B",
  },
  {
    id: "E-003",
    companyName: "田中設備工業",
    projectName: "横浜工場設備更新",
    period: "2025年11月〜2026年2月",
    qualityScore: 78,
    safetyScore: 80,
    costScore: 75,
    scheduleScore: 77,
    totalScore: 78,
    evaluator: "設備部長 佐藤",
    grade: "C",
  },
  {
    id: "E-004",
    companyName: "佐藤建築工業",
    projectName: "新宿オフィスビル建設",
    period: "2026年1月〜5月",
    qualityScore: 96,
    safetyScore: 98,
    costScore: 93,
    scheduleScore: 95,
    totalScore: 96,
    evaluator: "工事部長 鈴木",
    grade: "A",
  },
  {
    id: "E-005",
    companyName: "伊藤土木建設",
    projectName: "道路改良工事 A区間",
    period: "2025年12月〜2026年3月",
    qualityScore: 82,
    safetyScore: 85,
    costScore: 80,
    scheduleScore: 83,
    totalScore: 83,
    evaluator: "現場監督 高橋",
    grade: "B",
  },
  {
    id: "E-006",
    companyName: "中村電設工業",
    projectName: "工場電気設備工事",
    period: "2026年2月〜3月",
    qualityScore: 89,
    safetyScore: 91,
    costScore: 86,
    scheduleScore: 88,
    totalScore: 89,
    evaluator: "設備部長 佐藤",
    grade: "B",
  },
  {
    id: "E-007",
    companyName: "小林管工事",
    projectName: "集合住宅設備工事",
    period: "2025年10月〜2026年1月",
    qualityScore: 71,
    safetyScore: 73,
    costScore: 68,
    scheduleScore: 70,
    totalScore: 71,
    evaluator: "現場監督 田中",
    grade: "C",
  },
  {
    id: "E-008",
    companyName: "渡辺建設工業",
    projectName: "倉庫新築工事",
    period: "2026年3月〜4月",
    qualityScore: 94,
    safetyScore: 96,
    costScore: 91,
    scheduleScore: 93,
    totalScore: 94,
    evaluator: "工事部長 鈴木",
    grade: "A",
  },
];

const GRADE_COLORS: Record<Evaluation["grade"], string> = {
  A: "bg-green-100 text-green-800 font-bold",
  B: "bg-blue-100 text-blue-800 font-bold",
  C: "bg-yellow-100 text-yellow-800 font-bold",
  D: "bg-red-100 text-red-800 font-bold",
};

function ScoreBar({ score }: { score: number }) {
  const color =
    score >= 90
      ? "bg-green-500"
      : score >= 80
        ? "bg-blue-500"
        : score >= 70
          ? "bg-yellow-500"
          : "bg-red-500";
  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${color}`}
          style={{ width: `${score}%` }}
        />
      </div>
      <span className="text-sm font-medium text-gray-700 w-8">{score}</span>
    </div>
  );
}

export default function PartnerEvaluationPage() {
  const [searchQuery, setSearchQuery] = useState("");

  const filtered = MOCK_EVALUATIONS.filter(
    (e) =>
      e.companyName.includes(searchQuery) ||
      e.projectName.includes(searchQuery) ||
      e.evaluator.includes(searchQuery),
  );

  const avgTotal =
    Math.round(
      (MOCK_EVALUATIONS.reduce((sum, e) => sum + e.totalScore, 0) /
        MOCK_EVALUATIONS.length) *
        10,
    ) / 10;
  const excellentCount = MOCK_EVALUATIONS.filter((e) => e.grade === "A").length;

  return (
    <div className="p-6 space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">評価管理</h1>
          <p className="text-sm text-gray-500 mt-1">協力会社の実績・品質評価</p>
        </div>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
          <ClipboardCheck className="w-4 h-4" />
          新規評価入力
        </button>
      </div>

      {/* 統計カード */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-50 rounded-lg">
              <ClipboardCheck className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">評価完了数</p>
              <p className="text-2xl font-bold text-gray-900">
                {MOCK_EVALUATIONS.length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-50 rounded-lg">
              <BarChart3 className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">平均総合点</p>
              <p className="text-2xl font-bold text-gray-900">{avgTotal}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-50 rounded-lg">
              <Award className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">優良認定数(A評価)</p>
              <p className="text-2xl font-bold text-gray-900">
                {excellentCount}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* グレード分布 */}
      <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <h2 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
          <Star className="w-4 h-4 text-yellow-500" />
          評価グレード分布
        </h2>
        <div className="flex gap-4">
          {(["A", "B", "C", "D"] as const).map((grade) => {
            const count = MOCK_EVALUATIONS.filter(
              (e) => e.grade === grade,
            ).length;
            const pct = Math.round((count / MOCK_EVALUATIONS.length) * 100);
            return (
              <div key={grade} className="flex-1 text-center">
                <div
                  className={`inline-flex items-center justify-center w-10 h-10 rounded-full text-lg mb-1 ${GRADE_COLORS[grade]}`}
                >
                  {grade}
                </div>
                <p className="text-lg font-bold text-gray-900">{count}社</p>
                <p className="text-xs text-gray-500">{pct}%</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* 検索 */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="会社名・工事件名・評価者で検索..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
        </div>
      </div>

      {/* 評価テーブル */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  会社名
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  工事件名
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  評価期間
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  品質
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  安全
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  コスト
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  工程
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  総合点
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  評価者
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((ev) => (
                <tr key={ev.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-medium text-gray-900">
                    {ev.companyName}
                  </td>
                  <td className="px-4 py-3 text-gray-700">{ev.projectName}</td>
                  <td className="px-4 py-3 text-gray-500 text-xs whitespace-nowrap">
                    {ev.period}
                  </td>
                  <td className="px-4 py-3">
                    <ScoreBar score={ev.qualityScore} />
                  </td>
                  <td className="px-4 py-3">
                    <ScoreBar score={ev.safetyScore} />
                  </td>
                  <td className="px-4 py-3">
                    <ScoreBar score={ev.costScore} />
                  </td>
                  <td className="px-4 py-3">
                    <ScoreBar score={ev.scheduleScore} />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className="text-base font-bold text-gray-900">
                        {ev.totalScore}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded text-xs ${GRADE_COLORS[ev.grade]}`}
                      >
                        {ev.grade}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-600 text-xs">
                    {ev.evaluator}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-4 py-3 border-t border-gray-100 text-sm text-gray-500">
          {filtered.length}件表示 / 全{MOCK_EVALUATIONS.length}件
        </div>
      </div>
    </div>
  );
}
