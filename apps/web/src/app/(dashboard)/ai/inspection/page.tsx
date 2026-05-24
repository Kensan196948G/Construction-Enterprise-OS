"use client";

import { Camera, Brain, AlertCircle, CheckCircle, Search } from "lucide-react";

interface InspectionItem {
  id: string;
  fileName: string;
  location: string;
  status: "queued" | "analyzing" | "completed" | "error";
  anomalies: string[];
  confidence: number;
  capturedAt: string;
}

const MOCK_ITEMS: InspectionItem[] = [
  {
    id: "I-001",
    fileName: "IMG_2026_001.jpg",
    location: "品川タワー B1F 柱脚部",
    status: "completed",
    anomalies: ["ひび割れ"],
    confidence: 94,
    capturedAt: "2026-05-24 09:10",
  },
  {
    id: "I-002",
    fileName: "IMG_2026_002.jpg",
    location: "品川タワー 3F 梁",
    status: "completed",
    anomalies: [],
    confidence: 97,
    capturedAt: "2026-05-24 09:15",
  },
  {
    id: "I-003",
    fileName: "IMG_2026_003.jpg",
    location: "大阪ビル 外壁 北面",
    status: "completed",
    anomalies: ["錆び", "剥離"],
    confidence: 88,
    capturedAt: "2026-05-24 10:02",
  },
  {
    id: "I-004",
    fileName: "IMG_2026_004.jpg",
    location: "横浜工場 屋根 東エリア",
    status: "analyzing",
    anomalies: [],
    confidence: 0,
    capturedAt: "2026-05-24 10:30",
  },
  {
    id: "I-005",
    fileName: "IMG_2026_005.jpg",
    location: "新宿ビル 1F スラブ",
    status: "completed",
    anomalies: ["ひび割れ", "その他"],
    confidence: 81,
    capturedAt: "2026-05-24 11:00",
  },
  {
    id: "I-006",
    fileName: "IMG_2026_006.jpg",
    location: "品川タワー 5F 壁面",
    status: "completed",
    anomalies: [],
    confidence: 99,
    capturedAt: "2026-05-24 11:20",
  },
  {
    id: "I-007",
    fileName: "IMG_2026_007.jpg",
    location: "道路工事 路盤 A区間",
    status: "queued",
    anomalies: [],
    confidence: 0,
    capturedAt: "2026-05-24 12:00",
  },
  {
    id: "I-008",
    fileName: "IMG_2026_008.jpg",
    location: "大阪ビル 地下ピット",
    status: "completed",
    anomalies: ["錆び"],
    confidence: 91,
    capturedAt: "2026-05-24 13:10",
  },
  {
    id: "I-009",
    fileName: "IMG_2026_009.jpg",
    location: "新宿ビル 外壁 南面",
    status: "error",
    anomalies: [],
    confidence: 0,
    capturedAt: "2026-05-24 13:45",
  },
  {
    id: "I-010",
    fileName: "IMG_2026_010.jpg",
    location: "横浜工場 基礎 西側",
    status: "queued",
    anomalies: [],
    confidence: 0,
    capturedAt: "2026-05-24 14:00",
  },
];

const STATUS_CONFIG = {
  queued: { label: "待機中", color: "bg-gray-100 text-gray-600" },
  analyzing: { label: "解析中", color: "bg-blue-100 text-blue-700" },
  completed: { label: "完了", color: "bg-green-100 text-green-700" },
  error: { label: "エラー", color: "bg-red-100 text-red-700" },
};

const ANOMALY_COLORS: Record<string, string> = {
  ひび割れ: "bg-orange-100 text-orange-700",
  錆び: "bg-red-100 text-red-700",
  剥離: "bg-yellow-100 text-yellow-700",
  その他: "bg-gray-100 text-gray-700",
};

export default function AIInspectionPage() {
  const completed = MOCK_ITEMS.filter((i) => i.status === "completed").length;
  const withAnomalies = MOCK_ITEMS.filter((i) => i.anomalies.length > 0).length;
  const needsReview = MOCK_ITEMS.filter(
    (i) => i.anomalies.length > 0 && i.confidence < 90,
  ).length;
  const avgConfidence = Math.round(
    MOCK_ITEMS.filter((i) => i.confidence > 0).reduce(
      (s, i) => s + i.confidence,
      0,
    ) / MOCK_ITEMS.filter((i) => i.confidence > 0).length,
  );

  const anomalyCounts = {
    ひび割れ: MOCK_ITEMS.flatMap((i) => i.anomalies).filter(
      (a) => a === "ひび割れ",
    ).length,
    錆び: MOCK_ITEMS.flatMap((i) => i.anomalies).filter((a) => a === "錆び")
      .length,
    剥離: MOCK_ITEMS.flatMap((i) => i.anomalies).filter((a) => a === "剥離")
      .length,
    その他: MOCK_ITEMS.flatMap((i) => i.anomalies).filter((a) => a === "その他")
      .length,
  };

  return (
    <div className="p-6 space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI点検</h1>
          <p className="text-sm text-gray-500 mt-1">
            点検画像のAI自動解析・異常検出
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500 bg-blue-50 px-3 py-1.5 rounded-full">
          <Brain className="w-3.5 h-3.5 text-blue-600" />
          Vision AI powered
        </div>
      </div>

      {/* 統計カード */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-50 rounded-lg">
              <Camera className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">解析済み数</p>
              <p className="text-2xl font-bold text-gray-900">{completed}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-50 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">異常検出数</p>
              <p className="text-2xl font-bold text-gray-900">
                {withAnomalies}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-50 rounded-lg">
              <Search className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">要確認数</p>
              <p className="text-2xl font-bold text-gray-900">{needsReview}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-50 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">解析精度</p>
              <p className="text-2xl font-bold text-gray-900">
                {avgConfidence}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 異常検出サマリー */}
      <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <h2 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-orange-500" />
          異常検出カテゴリ別件数
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Object.entries(anomalyCounts).map(([cat, count]) => (
            <div key={cat} className="text-center p-3 rounded-lg bg-gray-50">
              <span
                className={`inline-block px-2 py-0.5 rounded text-xs font-medium mb-2 ${ANOMALY_COLORS[cat]}`}
              >
                {cat}
              </span>
              <p className="text-2xl font-bold text-gray-900">{count}</p>
              <p className="text-xs text-gray-500">件</p>
            </div>
          ))}
        </div>
      </div>

      {/* 解析キューテーブル */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h2 className="font-semibold text-gray-800">点検画像解析キュー</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  ファイル名
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  撮影場所
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  解析状況
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  検出異常
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  信頼度
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  撮影日時
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {MOCK_ITEMS.map((item) => (
                <tr
                  key={item.id}
                  className="hover:bg-gray-50 transition-colors"
                >
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <Camera className="w-4 h-4 text-gray-400" />
                      <span className="font-mono text-xs text-gray-700">
                        {item.fileName}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-700">{item.location}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_CONFIG[item.status].color}`}
                    >
                      {STATUS_CONFIG[item.status].label}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {item.anomalies.length === 0 ? (
                      item.status === "completed" ? (
                        <span className="flex items-center gap-1 text-green-600 text-xs">
                          <CheckCircle className="w-3 h-3" />
                          異常なし
                        </span>
                      ) : (
                        <span className="text-gray-400 text-xs">—</span>
                      )
                    ) : (
                      <div className="flex flex-wrap gap-1">
                        {item.anomalies.map((a) => (
                          <span
                            key={a}
                            className={`px-1.5 py-0.5 rounded text-xs ${ANOMALY_COLORS[a]}`}
                          >
                            {a}
                          </span>
                        ))}
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {item.confidence > 0 ? (
                      <div className="flex items-center gap-2">
                        <div className="w-12 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${item.confidence >= 90 ? "bg-green-500" : item.confidence >= 75 ? "bg-yellow-500" : "bg-red-500"}`}
                            style={{ width: `${item.confidence}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-600">
                          {item.confidence}%
                        </span>
                      </div>
                    ) : (
                      <span className="text-gray-400 text-xs">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-gray-500 text-xs whitespace-nowrap">
                    {item.capturedAt}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-4 py-3 border-t border-gray-100 text-sm text-gray-500">
          {MOCK_ITEMS.length}件
        </div>
      </div>
    </div>
  );
}
