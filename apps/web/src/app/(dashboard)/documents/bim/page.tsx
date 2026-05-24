"use client";

import { useState } from "react";
import { Box, Layers, RotateCcw, Download } from "lucide-react";

interface BimModel {
  id: string;
  name: string;
  project: string;
  version: string;
  updatedDate: string;
  fileSize: string;
  format: "IFC" | "Revit" | "ArchiCAD";
  discipline: string;
}

const MOCK_MODELS: BimModel[] = [
  {
    id: "1",
    name: "本館建築モデル",
    project: "大阪オフィスビル新築工事",
    version: "v3.2",
    updatedDate: "2026-05-23",
    fileSize: "284 MB",
    format: "Revit",
    discipline: "建築",
  },
  {
    id: "2",
    name: "構造躯体モデル",
    project: "大阪オフィスビル新築工事",
    version: "v2.8",
    updatedDate: "2026-05-21",
    fileSize: "156 MB",
    format: "IFC",
    discipline: "構造",
  },
  {
    id: "3",
    name: "設備総合モデル",
    project: "大阪オフィスビル新築工事",
    version: "v1.5",
    updatedDate: "2026-05-19",
    fileSize: "412 MB",
    format: "Revit",
    discipline: "設備",
  },
  {
    id: "4",
    name: "橋梁上部工モデル",
    project: "国道XX号線橋梁工事",
    version: "v4.1",
    updatedDate: "2026-05-20",
    fileSize: "98 MB",
    format: "IFC",
    discipline: "土木",
  },
  {
    id: "5",
    name: "トンネル断面モデル",
    project: "山岳トンネル掘削工事",
    version: "v2.0",
    updatedDate: "2026-05-17",
    fileSize: "203 MB",
    format: "ArchiCAD",
    discipline: "トンネル",
  },
  {
    id: "6",
    name: "地下躯体干渉チェックモデル",
    project: "都市再開発第2期工事",
    version: "v1.2",
    updatedDate: "2026-05-15",
    fileSize: "67 MB",
    format: "IFC",
    discipline: "構造",
  },
];

const FORMAT_COLORS: Record<BimModel["format"], string> = {
  IFC: "bg-blue-100 text-blue-800",
  Revit: "bg-purple-100 text-purple-800",
  ArchiCAD: "bg-orange-100 text-orange-800",
};

export default function BimPage() {
  const [selectedModel, setSelectedModel] = useState<BimModel | null>(
    MOCK_MODELS[0],
  );

  const totalSize = MOCK_MODELS.reduce((acc, m) => {
    const num = parseFloat(m.fileSize);
    return acc + num;
  }, 0);

  const latestUpdate = MOCK_MODELS.reduce(
    (latest, m) => (m.updatedDate > latest ? m.updatedDate : latest),
    "",
  );

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            BIM/CIMモデル管理
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            文書・図面管理 — 3Dモデル一覧・ビューワー
          </p>
        </div>
        <Box className="w-8 h-8 text-blue-600" />
      </div>

      {/* 統計カード */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Box className="w-8 h-8 text-blue-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">登録モデル数</p>
            <p className="text-2xl font-bold text-gray-800">
              {MOCK_MODELS.length}
            </p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <RotateCcw className="w-8 h-8 text-green-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">最終更新</p>
            <p className="text-lg font-bold text-gray-800">{latestUpdate}</p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Layers className="w-8 h-8 text-purple-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">総ファイルサイズ</p>
            <p className="text-2xl font-bold text-gray-800">
              {totalSize.toFixed(0)} MB
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* モデル一覧 */}
        <div className="lg:col-span-1 space-y-3">
          <h2 className="font-semibold text-gray-700">モデル一覧</h2>
          <div className="space-y-2">
            {MOCK_MODELS.map((model) => (
              <div
                key={model.id}
                onClick={() => setSelectedModel(model)}
                className={`bg-white rounded-lg border p-4 cursor-pointer transition-all ${
                  selectedModel?.id === model.id
                    ? "border-blue-500 ring-1 ring-blue-500"
                    : "hover:border-gray-300"
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className="font-medium text-gray-900 text-sm truncate">
                      {model.name}
                    </p>
                    <p className="text-xs text-gray-500 mt-0.5 truncate">
                      {model.project}
                    </p>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-medium shrink-0 ${FORMAT_COLORS[model.format]}`}
                  >
                    {model.format}
                  </span>
                </div>
                <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                  <span>{model.version}</span>
                  <span>{model.updatedDate}</span>
                  <span>{model.fileSize}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 3Dビューワー + 詳細 */}
        <div className="lg:col-span-2 space-y-4">
          {/* ビューワーエリア */}
          <div className="bg-gray-900 rounded-lg overflow-hidden">
            <div className="h-96 flex flex-col items-center justify-center text-gray-400">
              <Box className="w-16 h-16 mb-4 text-gray-600" />
              <p className="text-xl font-semibold text-gray-300">BIM Viewer</p>
              {selectedModel && (
                <p className="text-sm mt-2 text-gray-400">
                  {selectedModel.name}
                </p>
              )}
              <div className="mt-6 text-xs text-gray-500 text-center space-y-1">
                <p>
                  マウスドラッグ: 回転 | スクロール: ズーム | 右クリック: パン
                </p>
                <p>実装時はThree.js / IFC.js / Forge Viewer を統合</p>
              </div>
            </div>
          </div>

          {/* 3D操作ガイドと詳細情報 */}
          {selectedModel && (
            <div className="bg-white rounded-lg border p-4">
              <h3 className="font-semibold text-gray-800 mb-3">
                {selectedModel.name} — 詳細情報
              </h3>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-gray-500">プロジェクト:</span>
                  <span className="ml-2 text-gray-800">
                    {selectedModel.project}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">専門分野:</span>
                  <span className="ml-2 text-gray-800">
                    {selectedModel.discipline}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">バージョン:</span>
                  <span className="ml-2 text-gray-800">
                    {selectedModel.version}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">更新日:</span>
                  <span className="ml-2 text-gray-800">
                    {selectedModel.updatedDate}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">ファイル形式:</span>
                  <span
                    className={`ml-2 px-2 py-0.5 rounded text-xs font-medium ${FORMAT_COLORS[selectedModel.format]}`}
                  >
                    {selectedModel.format}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">ファイルサイズ:</span>
                  <span className="ml-2 text-gray-800">
                    {selectedModel.fileSize}
                  </span>
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                <button className="flex items-center gap-1.5 px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">
                  <Download className="w-4 h-4" />
                  ダウンロード
                </button>
                <button className="flex items-center gap-1.5 px-3 py-2 bg-gray-100 text-gray-700 text-sm rounded hover:bg-gray-200">
                  <Layers className="w-4 h-4" />
                  レイヤー設定
                </button>
                <button className="flex items-center gap-1.5 px-3 py-2 bg-gray-100 text-gray-700 text-sm rounded hover:bg-gray-200">
                  <RotateCcw className="w-4 h-4" />
                  ビューリセット
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
