"use client";

import { useState } from "react";
import { Mountain, Layers, Ruler, Globe } from "lucide-react";

const DISPLAY_LAYERS = [
  { id: "construction", label: "工事区域", defaultChecked: true },
  { id: "contour", label: "等高線", defaultChecked: true },
  { id: "buildings", label: "建物", defaultChecked: true },
  { id: "infrastructure", label: "インフラ", defaultChecked: false },
  { id: "labels", label: "注記", defaultChecked: true },
];

const MAP_TYPES = ["地形", "衛星", "建物3D"] as const;
type MapType = (typeof MAP_TYPES)[number];

export default function Terrain3DPage() {
  const [mapType, setMapType] = useState<MapType>("地形");
  const [altitude, setAltitude] = useState(50);
  const [opacity, setOpacity] = useState(80);
  const [layers, setLayers] = useState<Record<string, boolean>>(
    Object.fromEntries(DISPLAY_LAYERS.map((l) => [l.id, l.defaultChecked])),
  );
  const [activeTool, setActiveTool] = useState<string | null>(null);

  const toggleLayer = (id: string) => {
    setLayers((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">3D地形表示</h1>
          <p className="text-sm text-gray-500 mt-1">
            GIS/地図 — 3Dテレイン・標高データ
          </p>
        </div>
        <Mountain className="w-8 h-8 text-green-600" />
      </div>

      {/* 統計カード */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <p className="text-xs text-gray-500">表示範囲</p>
          <p className="text-sm font-semibold text-gray-800 mt-1">
            北緯34.68° 東経135.52°
          </p>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Mountain className="w-7 h-7 text-green-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">最高標高</p>
            <p className="text-xl font-bold text-gray-800">142 m</p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Globe className="w-7 h-7 text-blue-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">最低標高</p>
            <p className="text-xl font-bold text-gray-800">3 m</p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Ruler className="w-7 h-7 text-purple-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">表示面積</p>
            <p className="text-xl font-bold text-gray-800">2.4 km²</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* コントロールパネル */}
        <div className="lg:col-span-1 space-y-4">
          {/* 地図種別 */}
          <div className="bg-white rounded-lg border p-4 space-y-3">
            <h3 className="font-semibold text-gray-700 text-sm flex items-center gap-1.5">
              <Globe className="w-4 h-4" />
              地図種別
            </h3>
            <div className="space-y-1">
              {MAP_TYPES.map((t) => (
                <button
                  key={t}
                  onClick={() => setMapType(t)}
                  className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                    mapType === t
                      ? "bg-blue-600 text-white"
                      : "bg-gray-50 text-gray-700 hover:bg-gray-100"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* スライダー */}
          <div className="bg-white rounded-lg border p-4 space-y-4">
            <h3 className="font-semibold text-gray-700 text-sm">表示設定</h3>
            <div>
              <div className="flex justify-between text-xs text-gray-500 mb-1">
                <span>高度倍率</span>
                <span>{altitude}%</span>
              </div>
              <input
                type="range"
                min={10}
                max={200}
                value={altitude}
                onChange={(e) => setAltitude(Number(e.target.value))}
                className="w-full accent-blue-600"
              />
            </div>
            <div>
              <div className="flex justify-between text-xs text-gray-500 mb-1">
                <span>透明度</span>
                <span>{opacity}%</span>
              </div>
              <input
                type="range"
                min={0}
                max={100}
                value={opacity}
                onChange={(e) => setOpacity(Number(e.target.value))}
                className="w-full accent-blue-600"
              />
            </div>
          </div>

          {/* レイヤー */}
          <div className="bg-white rounded-lg border p-4 space-y-3">
            <h3 className="font-semibold text-gray-700 text-sm flex items-center gap-1.5">
              <Layers className="w-4 h-4" />
              表示レイヤー
            </h3>
            <div className="space-y-2">
              {DISPLAY_LAYERS.map((layer) => (
                <label
                  key={layer.id}
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={layers[layer.id]}
                    onChange={() => toggleLayer(layer.id)}
                    className="accent-blue-600"
                  />
                  <span className="text-sm text-gray-700">{layer.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* 計測ツール */}
          <div className="bg-white rounded-lg border p-4 space-y-3">
            <h3 className="font-semibold text-gray-700 text-sm flex items-center gap-1.5">
              <Ruler className="w-4 h-4" />
              計測ツール
            </h3>
            <div className="space-y-1">
              {["面積計測", "距離計測", "標高断面"].map((tool) => (
                <button
                  key={tool}
                  onClick={() =>
                    setActiveTool(activeTool === tool ? null : tool)
                  }
                  className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                    activeTool === tool
                      ? "bg-orange-500 text-white"
                      : "bg-gray-50 text-gray-700 hover:bg-gray-100"
                  }`}
                >
                  {tool}
                  {activeTool === tool && " ✓"}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 3Dビューワー */}
        <div className="lg:col-span-3">
          <div className="bg-slate-900 rounded-lg overflow-hidden">
            <div className="h-96 flex flex-col items-center justify-center text-slate-400">
              <Mountain className="w-16 h-16 mb-4 text-slate-600" />
              <p className="text-xl font-semibold text-slate-300">
                3D Terrain Viewer
              </p>
              <p className="text-sm mt-2 text-slate-500">地図種別: {mapType}</p>
              <div className="mt-4 text-xs text-slate-500 text-center space-y-1">
                <p>
                  ドラッグ: 視点回転 | ホイール: ズーム | Shift+ドラッグ: パン
                </p>
                <p>実装時は Mapbox GL JS / Cesium / deck.gl を統合</p>
              </div>
              {activeTool && (
                <div className="mt-4 px-4 py-2 bg-orange-500 text-white text-sm rounded-lg">
                  {activeTool} モード有効 — 地図上をクリックして計測
                </div>
              )}
            </div>
          </div>
          <div className="mt-3 flex gap-2 text-xs text-gray-500 flex-wrap">
            <span className="bg-gray-100 px-2 py-1 rounded">
              高度倍率: {altitude}%
            </span>
            <span className="bg-gray-100 px-2 py-1 rounded">
              透明度: {opacity}%
            </span>
            <span className="bg-gray-100 px-2 py-1 rounded">
              表示レイヤー: {Object.values(layers).filter(Boolean).length} /{" "}
              {DISPLAY_LAYERS.length}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
