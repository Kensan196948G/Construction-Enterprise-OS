"use client";

import { useState } from "react";
import { FileImage, Layers, RefreshCw, Archive } from "lucide-react";

type DrawingType = "平面" | "立面" | "断面" | "詳細" | "設備";
type DrawingStatus = "current" | "superseded" | "preliminary";

interface Drawing {
  id: string;
  drawingNumber: string;
  drawingName: string;
  type: DrawingType;
  scale: string;
  revision: number;
  updatedDate: string;
  status: DrawingStatus;
}

const MOCK_DRAWINGS: Drawing[] = [
  {
    id: "1",
    drawingNumber: "A-001",
    drawingName: "1階平面図",
    type: "平面",
    scale: "1:100",
    revision: 3,
    updatedDate: "2026-05-22",
    status: "current",
  },
  {
    id: "2",
    drawingNumber: "A-002",
    drawingName: "2階平面図",
    type: "平面",
    scale: "1:100",
    revision: 2,
    updatedDate: "2026-05-20",
    status: "current",
  },
  {
    id: "3",
    drawingNumber: "A-101",
    drawingName: "北面立面図",
    type: "立面",
    scale: "1:200",
    revision: 1,
    updatedDate: "2026-05-18",
    status: "current",
  },
  {
    id: "4",
    drawingNumber: "A-102",
    drawingName: "南面立面図",
    type: "立面",
    scale: "1:200",
    revision: 1,
    updatedDate: "2026-05-18",
    status: "current",
  },
  {
    id: "5",
    drawingNumber: "A-201",
    drawingName: "X方向断面図",
    type: "断面",
    scale: "1:100",
    revision: 2,
    updatedDate: "2026-05-15",
    status: "current",
  },
  {
    id: "6",
    drawingNumber: "A-202",
    drawingName: "Y方向断面図",
    type: "断面",
    scale: "1:100",
    revision: 1,
    updatedDate: "2026-05-10",
    status: "superseded",
  },
  {
    id: "7",
    drawingNumber: "A-301",
    drawingName: "外壁詳細図",
    type: "詳細",
    scale: "1:20",
    revision: 4,
    updatedDate: "2026-05-23",
    status: "current",
  },
  {
    id: "8",
    drawingNumber: "A-302",
    drawingName: "階段詳細図",
    type: "詳細",
    scale: "1:20",
    revision: 0,
    updatedDate: "2026-05-12",
    status: "preliminary",
  },
  {
    id: "9",
    drawingNumber: "M-001",
    drawingName: "空調設備平面図",
    type: "設備",
    scale: "1:100",
    revision: 2,
    updatedDate: "2026-05-21",
    status: "current",
  },
  {
    id: "10",
    drawingNumber: "E-001",
    drawingName: "電気設備平面図",
    type: "設備",
    scale: "1:100",
    revision: 1,
    updatedDate: "2026-05-19",
    status: "current",
  },
  {
    id: "11",
    drawingNumber: "P-001",
    drawingName: "給排水設備図",
    type: "設備",
    scale: "1:100",
    revision: 3,
    updatedDate: "2026-05-16",
    status: "current",
  },
  {
    id: "12",
    drawingNumber: "A-000",
    drawingName: "旧1階平面図",
    type: "平面",
    scale: "1:100",
    revision: 0,
    updatedDate: "2026-04-01",
    status: "superseded",
  },
];

const STATUS_CONFIG: Record<
  DrawingStatus,
  { label: string; className: string }
> = {
  current: { label: "最新版", className: "bg-green-100 text-green-800" },
  superseded: { label: "廃版", className: "bg-gray-100 text-gray-600" },
  preliminary: { label: "暫定版", className: "bg-yellow-100 text-yellow-800" },
};

const TYPE_COLORS: Record<DrawingType, string> = {
  平面: "bg-blue-50 text-blue-700",
  立面: "bg-purple-50 text-purple-700",
  断面: "bg-indigo-50 text-indigo-700",
  詳細: "bg-orange-50 text-orange-700",
  設備: "bg-teal-50 text-teal-700",
};

export default function DrawingsPage() {
  const [filterType, setFilterType] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");

  const stats = {
    total: MOCK_DRAWINGS.length,
    current: MOCK_DRAWINGS.filter((d) => d.status === "current").length,
    preliminary: MOCK_DRAWINGS.filter((d) => d.status === "preliminary").length,
    superseded: MOCK_DRAWINGS.filter((d) => d.status === "superseded").length,
  };

  const filtered = MOCK_DRAWINGS.filter((d) => {
    const typeMatch = filterType === "all" || d.type === filterType;
    const statusMatch = filterStatus === "all" || d.status === filterStatus;
    return typeMatch && statusMatch;
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">図面管理</h1>
          <p className="text-sm text-gray-500 mt-1">
            文書・図面管理 — 図面一覧・改訂管理
          </p>
        </div>
        <FileImage className="w-8 h-8 text-blue-600" />
      </div>

      {/* 統計カード */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Layers className="w-8 h-8 text-blue-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">総図面数</p>
            <p className="text-2xl font-bold text-gray-800">{stats.total}</p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <FileImage className="w-8 h-8 text-green-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">最新版</p>
            <p className="text-2xl font-bold text-green-600">{stats.current}</p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <RefreshCw className="w-8 h-8 text-yellow-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">暫定版</p>
            <p className="text-2xl font-bold text-yellow-600">
              {stats.preliminary}
            </p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Archive className="w-8 h-8 text-gray-400 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">廃版</p>
            <p className="text-2xl font-bold text-gray-500">
              {stats.superseded}
            </p>
          </div>
        </div>
      </div>

      {/* フィルタ */}
      <div className="bg-white rounded-lg border p-4 space-y-3">
        <div>
          <p className="text-xs font-medium text-gray-500 mb-2">図面種別</p>
          <div className="flex gap-2 flex-wrap">
            {(["all", "平面", "立面", "断面", "詳細", "設備"] as const).map(
              (t) => (
                <button
                  key={t}
                  onClick={() => setFilterType(t)}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    filterType === t
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  {t === "all" ? "すべて" : t}
                </button>
              ),
            )}
          </div>
        </div>
        <div>
          <p className="text-xs font-medium text-gray-500 mb-2">
            改訂ステータス
          </p>
          <div className="flex gap-2 flex-wrap">
            {(["all", "current", "preliminary", "superseded"] as const).map(
              (s) => (
                <button
                  key={s}
                  onClick={() => setFilterStatus(s)}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    filterStatus === s
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  {s === "all" ? "すべて" : STATUS_CONFIG[s].label}
                </button>
              ),
            )}
          </div>
        </div>
      </div>

      {/* 図面テーブル */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  図面番号
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  図面名
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  種別
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  縮尺
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  改訂番号
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  更新日
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  ステータス
                </th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filtered.map((drawing) => (
                <tr
                  key={drawing.id}
                  className={`hover:bg-gray-50 transition-colors ${
                    drawing.status === "superseded" ? "opacity-60" : ""
                  }`}
                >
                  <td className="px-4 py-3 font-mono text-xs font-semibold text-gray-700">
                    {drawing.drawingNumber}
                  </td>
                  <td className="px-4 py-3 font-medium text-gray-900">
                    {drawing.drawingName}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-medium ${TYPE_COLORS[drawing.type]}`}
                    >
                      {drawing.type}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-600 font-mono text-xs">
                    {drawing.scale}
                  </td>
                  <td className="px-4 py-3 text-gray-600 text-center">
                    Rev.{drawing.revision}
                  </td>
                  <td className="px-4 py-3 text-gray-600">
                    {drawing.updatedDate}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_CONFIG[drawing.status].className}`}
                    >
                      {STATUS_CONFIG[drawing.status].label}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-4 py-3 border-t bg-gray-50 text-xs text-gray-500">
          {filtered.length} 件表示 / 全 {MOCK_DRAWINGS.length} 件
        </div>
      </div>
    </div>
  );
}
