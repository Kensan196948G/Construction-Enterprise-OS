"use client";

import { useState } from "react";
import { Plane, Camera, Map, Download } from "lucide-react";

interface UavPhoto {
  id: string;
  area: string;
  capturedDate: string;
  resolution: string;
  fileSize: string;
  altitude: string;
  overlap: string;
}

const MOCK_PHOTOS: UavPhoto[] = [
  {
    id: "1",
    area: "第1工区 全景",
    capturedDate: "2026-05-23",
    resolution: "4K (3840×2160)",
    fileSize: "2.4 GB",
    altitude: "80 m",
    overlap: "80%",
  },
  {
    id: "2",
    area: "基礎工事エリア",
    capturedDate: "2026-05-22",
    resolution: "4K (3840×2160)",
    fileSize: "1.8 GB",
    altitude: "60 m",
    overlap: "75%",
  },
  {
    id: "3",
    area: "第2工区 北側",
    capturedDate: "2026-05-21",
    resolution: "2.7K (2704×1520)",
    fileSize: "1.2 GB",
    altitude: "100 m",
    overlap: "70%",
  },
  {
    id: "4",
    area: "資材置き場",
    capturedDate: "2026-05-20",
    resolution: "4K (3840×2160)",
    fileSize: "0.9 GB",
    altitude: "50 m",
    overlap: "85%",
  },
  {
    id: "5",
    area: "第3工区 掘削エリア",
    capturedDate: "2026-05-19",
    resolution: "4K (3840×2160)",
    fileSize: "3.1 GB",
    altitude: "70 m",
    overlap: "80%",
  },
  {
    id: "6",
    area: "橋梁工事区間",
    capturedDate: "2026-05-18",
    resolution: "2.7K (2704×1520)",
    fileSize: "2.2 GB",
    altitude: "120 m",
    overlap: "75%",
  },
  {
    id: "7",
    area: "全現場俯瞰",
    capturedDate: "2026-05-17",
    resolution: "4K (3840×2160)",
    fileSize: "4.5 GB",
    altitude: "150 m",
    overlap: "70%",
  },
  {
    id: "8",
    area: "第1工区 進捗確認",
    capturedDate: "2026-05-16",
    resolution: "4K (3840×2160)",
    fileSize: "2.1 GB",
    altitude: "80 m",
    overlap: "80%",
  },
  {
    id: "9",
    area: "北側アクセス道路",
    capturedDate: "2026-05-15",
    resolution: "1080p (1920×1080)",
    fileSize: "0.6 GB",
    altitude: "40 m",
    overlap: "65%",
  },
  {
    id: "10",
    area: "土砂仮置き場",
    capturedDate: "2026-05-14",
    resolution: "2.7K (2704×1520)",
    fileSize: "1.1 GB",
    altitude: "60 m",
    overlap: "75%",
  },
  {
    id: "11",
    area: "第2工区 配筋確認",
    capturedDate: "2026-05-13",
    resolution: "4K (3840×2160)",
    fileSize: "1.7 GB",
    altitude: "30 m",
    overlap: "90%",
  },
  {
    id: "12",
    area: "外周フェンス点検",
    capturedDate: "2026-05-12",
    resolution: "1080p (1920×1080)",
    fileSize: "0.8 GB",
    altitude: "20 m",
    overlap: "60%",
  },
];

const AREAS = [
  "すべて",
  "第1工区",
  "第2工区",
  "第3工区",
  "橋梁工事区間",
  "全現場",
];

export default function UavPage() {
  const [filterArea, setFilterArea] = useState("すべて");
  const [filterDate, setFilterDate] = useState("");
  const [selected, setSelected] = useState<UavPhoto | null>(null);

  const filtered = MOCK_PHOTOS.filter((p) => {
    const areaMatch =
      filterArea === "すべて" ||
      p.area.includes(filterArea.replace("すべて", ""));
    const dateMatch = !filterDate || p.capturedDate >= filterDate;
    return areaMatch && dateMatch;
  });

  const totalSize = MOCK_PHOTOS.reduce(
    (acc, p) => acc + parseFloat(p.fileSize),
    0,
  );
  const latestDate = MOCK_PHOTOS.reduce(
    (latest, p) => (p.capturedDate > latest ? p.capturedDate : latest),
    "",
  );

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            UAV/ドローン写真管理
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            GIS/地図 — 航空写真・オルソ画像
          </p>
        </div>
        <Plane className="w-8 h-8 text-blue-600" />
      </div>

      {/* 統計カード */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Camera className="w-8 h-8 text-blue-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">総撮影数</p>
            <p className="text-2xl font-bold text-gray-800">
              {MOCK_PHOTOS.length}
            </p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Plane className="w-8 h-8 text-green-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">最新撮影日</p>
            <p className="text-lg font-bold text-gray-800">{latestDate}</p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Map className="w-8 h-8 text-purple-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">カバレッジ面積</p>
            <p className="text-2xl font-bold text-gray-800">5.8 km²</p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Download className="w-8 h-8 text-orange-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">総データ容量</p>
            <p className="text-2xl font-bold text-gray-800">
              {totalSize.toFixed(1)} GB
            </p>
          </div>
        </div>
      </div>

      {/* フィルタ */}
      <div className="bg-white rounded-lg border p-4 flex flex-wrap gap-4 items-end">
        <div>
          <p className="text-xs font-medium text-gray-500 mb-1.5">エリア</p>
          <div className="flex gap-2 flex-wrap">
            {AREAS.map((a) => (
              <button
                key={a}
                onClick={() => setFilterArea(a)}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  filterArea === a
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {a}
              </button>
            ))}
          </div>
        </div>
        <div>
          <p className="text-xs font-medium text-gray-500 mb-1.5">
            撮影日 (以降)
          </p>
          <input
            type="date"
            value={filterDate}
            onChange={(e) => setFilterDate(e.target.value)}
            className="border rounded px-3 py-1.5 text-sm text-gray-700 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
        {(filterArea !== "すべて" || filterDate) && (
          <button
            onClick={() => {
              setFilterArea("すべて");
              setFilterDate("");
            }}
            className="px-3 py-1.5 bg-gray-200 text-gray-600 text-sm rounded hover:bg-gray-300"
          >
            リセット
          </button>
        )}
      </div>

      {/* 写真グリッド */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {filtered.map((photo) => (
          <div
            key={photo.id}
            onClick={() => setSelected(photo)}
            className={`bg-white rounded-lg border overflow-hidden cursor-pointer transition-all hover:shadow-md ${
              selected?.id === photo.id ? "ring-2 ring-blue-500" : ""
            }`}
          >
            {/* 写真プレースホルダー */}
            <div className="bg-slate-900 aspect-video flex flex-col items-center justify-center text-slate-500">
              <Camera className="w-8 h-8 mb-1 text-slate-600" />
              <span className="text-xs text-slate-400">UAV Photo</span>
            </div>
            <div className="p-3 space-y-1">
              <p className="font-medium text-gray-900 text-sm leading-tight">
                {photo.area}
              </p>
              <p className="text-xs text-gray-500">{photo.capturedDate}</p>
              <div className="flex justify-between text-xs text-gray-400 pt-1">
                <span>{photo.resolution.split(" ")[0]}</span>
                <span>{photo.fileSize}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 選択写真詳細 */}
      {selected && (
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-semibold text-gray-800">
                {selected.area} — 詳細情報
              </h3>
              <div className="mt-3 grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                <div>
                  <span className="text-gray-500">撮影日:</span>
                  <span className="ml-2 text-gray-800">
                    {selected.capturedDate}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">解像度:</span>
                  <span className="ml-2 text-gray-800">
                    {selected.resolution}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">ファイルサイズ:</span>
                  <span className="ml-2 text-gray-800">
                    {selected.fileSize}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">飛行高度:</span>
                  <span className="ml-2 text-gray-800">
                    {selected.altitude}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">オーバーラップ:</span>
                  <span className="ml-2 text-gray-800">{selected.overlap}</span>
                </div>
              </div>
            </div>
            <div className="flex gap-2 shrink-0">
              <button className="flex items-center gap-1.5 px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">
                <Download className="w-4 h-4" />
                ダウンロード
              </button>
              <button
                onClick={() => setSelected(null)}
                className="px-3 py-2 bg-gray-100 text-gray-600 text-sm rounded hover:bg-gray-200"
              >
                閉じる
              </button>
            </div>
          </div>
        </div>
      )}

      <p className="text-xs text-gray-400 text-right">
        {filtered.length} 件表示 / 全 {MOCK_PHOTOS.length} 件
      </p>
    </div>
  );
}
