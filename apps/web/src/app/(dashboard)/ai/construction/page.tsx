"use client";

import { useState } from "react";
import {
  Brain,
  TrendingUp,
  AlertTriangle,
  Zap,
  RefreshCw,
  ChevronDown,
} from "lucide-react";

interface AnalysisHistory {
  id: string;
  datetime: string;
  project: string;
  type: string;
  confidence: number;
  summary: string;
}

const PROJECTS = [
  "品川タワー新築工事",
  "大阪ビル改修工事",
  "新宿オフィスビル建設",
  "横浜工場設備更新",
  "道路改良工事 A区間",
];

const MOCK_HISTORY: AnalysisHistory[] = [
  {
    id: "A-001",
    datetime: "2026-05-24 09:15",
    project: "品川タワー新築工事",
    type: "工程リスク分析",
    confidence: 92,
    summary: "3工区の鉄骨工事が5日遅延リスク。天候影響と資材調達遅れが主要因。",
  },
  {
    id: "A-002",
    datetime: "2026-05-24 08:30",
    project: "新宿オフィスビル建設",
    type: "コスト最適化",
    confidence: 87,
    summary:
      "資材単価変動により予算比+2.3%超過予測。代替資材活用で1.8%削減可能。",
  },
  {
    id: "A-003",
    datetime: "2026-05-23 17:00",
    project: "大阪ビル改修工事",
    type: "品質リスク分析",
    confidence: 78,
    summary:
      "コンクリート打設工程での品質ばらつきを検出。養生温度管理の強化を推奨。",
  },
  {
    id: "A-004",
    datetime: "2026-05-23 14:20",
    project: "横浜工場設備更新",
    type: "工程最適化",
    confidence: 95,
    summary:
      "設備据付工程の並列化により工期3日短縮可能。クリティカルパスを再最適化。",
  },
  {
    id: "A-005",
    datetime: "2026-05-22 11:45",
    project: "品川タワー新築工事",
    type: "総合リスク分析",
    confidence: 83,
    summary:
      "全体工程は概ね順調。台風シーズン対応として6月末までの鉄骨工事完了を推奨。",
  },
];

interface AnalysisResult {
  scheduleDelayRisk: number;
  qualityRisk: string;
  costOverrun: number;
  suggestions: string[];
}

const MOCK_RESULTS: Record<string, AnalysisResult> = {
  品川タワー新築工事: {
    scheduleDelayRisk: 35,
    qualityRisk: "中",
    costOverrun: 2.3,
    suggestions: [
      "3工区鉄骨工事の前倒し実施を推奨",
      "資材搬入ルートの代替案を準備",
      "台風シーズン前の上棟完了を目指す",
    ],
  },
  大阪ビル改修工事: {
    scheduleDelayRisk: 12,
    qualityRisk: "低",
    costOverrun: 0.5,
    suggestions: ["現状維持で問題なし", "竣工検査日程の早期確定を推奨"],
  },
  新宿オフィスビル建設: {
    scheduleDelayRisk: 58,
    qualityRisk: "高",
    costOverrun: 4.1,
    suggestions: [
      "資材調達先の多様化が急務",
      "品質管理体制の強化が必要",
      "工程バッファの追加を検討",
    ],
  },
};

const RISK_COLORS = {
  低: "text-green-600 bg-green-50",
  中: "text-yellow-600 bg-yellow-50",
  高: "text-red-600 bg-red-50",
};

export default function AIConstructionPage() {
  const [selectedProject, setSelectedProject] = useState(PROJECTS[0]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const result =
    MOCK_RESULTS[selectedProject] ?? MOCK_RESULTS["大阪ビル改修工事"];

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    setTimeout(() => setIsAnalyzing(false), 1500);
  };

  const delayColor =
    result.scheduleDelayRisk >= 50
      ? "text-red-600"
      : result.scheduleDelayRisk >= 30
        ? "text-yellow-600"
        : "text-green-600";

  return (
    <div className="p-6 space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">施工AI解析</h1>
          <p className="text-sm text-gray-500 mt-1">
            AIによる工程・品質・コストリスク分析
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500 bg-blue-50 px-3 py-1.5 rounded-full">
          <Brain className="w-3.5 h-3.5 text-blue-600" />
          Claude AI powered
        </div>
      </div>

      {/* プロジェクト選択・解析実行 */}
      <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">
          解析対象プロジェクト
        </h2>
        <div className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <select
              value={selectedProject}
              onChange={(e) => setSelectedProject(e.target.value)}
              className="w-full appearance-none border border-gray-200 rounded-lg px-4 py-2.5 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            >
              {PROJECTS.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="flex items-center gap-2 bg-blue-600 text-white px-5 py-2.5 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-60 text-sm font-medium"
          >
            {isAnalyzing ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Zap className="w-4 h-4" />
            )}
            {isAnalyzing ? "解析中..." : "AI解析実行"}
          </button>
        </div>
      </div>

      {/* 解析結果カード */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-4 h-4 text-orange-500" />
            <span className="text-sm font-medium text-gray-700">
              工程遅延リスク
            </span>
          </div>
          <p className={`text-4xl font-bold ${delayColor}`}>
            {result.scheduleDelayRisk}%
          </p>
          <div className="mt-2 h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${result.scheduleDelayRisk >= 50 ? "bg-red-500" : result.scheduleDelayRisk >= 30 ? "bg-yellow-500" : "bg-green-500"}`}
              style={{ width: `${result.scheduleDelayRisk}%` }}
            />
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-4 h-4 text-yellow-500" />
            <span className="text-sm font-medium text-gray-700">
              品質リスク
            </span>
          </div>
          <span
            className={`text-3xl font-bold px-3 py-1 rounded-lg ${RISK_COLORS[result.qualityRisk as keyof typeof RISK_COLORS]}`}
          >
            {result.qualityRisk}
          </span>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-4 h-4 text-red-500" />
            <span className="text-sm font-medium text-gray-700">
              コスト超過予測
            </span>
          </div>
          <p
            className={`text-4xl font-bold ${result.costOverrun > 3 ? "text-red-600" : result.costOverrun > 1 ? "text-yellow-600" : "text-green-600"}`}
          >
            +{result.costOverrun}%
          </p>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2 mb-3">
            <Brain className="w-4 h-4 text-blue-500" />
            <span className="text-sm font-medium text-gray-700">
              最適化提案
            </span>
          </div>
          <ul className="space-y-1">
            {result.suggestions.map((s, i) => (
              <li
                key={i}
                className="text-xs text-gray-600 flex items-start gap-1.5"
              >
                <span className="text-blue-500 mt-0.5">•</span>
                {s}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* 解析履歴 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h2 className="font-semibold text-gray-800">解析履歴</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  解析日時
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  対象プロジェクト
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  解析種別
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  信頼度
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  結果サマリー
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {MOCK_HISTORY.map((h) => (
                <tr key={h.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 text-gray-500 text-xs whitespace-nowrap">
                    {h.datetime}
                  </td>
                  <td className="px-4 py-3 font-medium text-gray-900">
                    {h.project}
                  </td>
                  <td className="px-4 py-3">
                    <span className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded text-xs">
                      {h.type}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-12 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 rounded-full"
                          style={{ width: `${h.confidence}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-600">
                        {h.confidence}%
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-600 text-xs max-w-xs truncate">
                    {h.summary}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
