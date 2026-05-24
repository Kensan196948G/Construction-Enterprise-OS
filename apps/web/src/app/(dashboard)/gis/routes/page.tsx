"use client";

import { Route, Truck, MapPin, AlertTriangle } from "lucide-react";

type RouteStatus = "通常" | "工事中" | "通行止め" | "迂回推奨";

interface TransportRoute {
  id: string;
  name: string;
  origin: string;
  destination: string;
  distance: string;
  duration: string;
  weightLimit: string;
  status: RouteStatus;
  tripsThisMonth: number;
}

const MOCK_ROUTES: TransportRoute[] = [
  {
    id: "1",
    name: "メインルートA",
    origin: "資材置き場（南ゲート）",
    destination: "第1工区 作業エリア",
    distance: "1.2 km",
    duration: "8 分",
    weightLimit: "25 t",
    status: "通常",
    tripsThisMonth: 142,
  },
  {
    id: "2",
    name: "資材搬入ルートB",
    origin: "資材置き場（南ゲート）",
    destination: "第2工区 作業エリア",
    distance: "2.1 km",
    duration: "14 分",
    weightLimit: "20 t",
    status: "工事中",
    tripsThisMonth: 87,
  },
  {
    id: "3",
    name: "土砂搬出ルートC",
    origin: "掘削エリア（東）",
    destination: "土砂仮置き場",
    distance: "0.8 km",
    duration: "5 分",
    weightLimit: "30 t",
    status: "通常",
    tripsThisMonth: 215,
  },
  {
    id: "4",
    name: "重機搬入ルートD",
    origin: "北ゲート",
    destination: "第3工区 重機置き場",
    distance: "3.4 km",
    duration: "22 分",
    weightLimit: "50 t",
    status: "通行止め",
    tripsThisMonth: 0,
  },
  {
    id: "5",
    name: "コンクリートルートE",
    origin: "生コン車進入口",
    destination: "打設エリア",
    distance: "1.6 km",
    duration: "10 分",
    weightLimit: "20 t",
    status: "迂回推奨",
    tripsThisMonth: 63,
  },
  {
    id: "6",
    name: "廃材搬出ルートF",
    origin: "解体エリア",
    destination: "廃材置き場（西）",
    distance: "2.8 km",
    duration: "18 分",
    weightLimit: "15 t",
    status: "通常",
    tripsThisMonth: 98,
  },
];

const STATUS_CONFIG: Record<RouteStatus, { className: string; dot: string }> = {
  通常: { className: "bg-green-100 text-green-800", dot: "bg-green-500" },
  工事中: { className: "bg-yellow-100 text-yellow-800", dot: "bg-yellow-500" },
  通行止め: { className: "bg-red-100 text-red-800", dot: "bg-red-500" },
  迂回推奨: {
    className: "bg-orange-100 text-orange-800",
    dot: "bg-orange-500",
  },
};

export default function RoutesPage() {
  const stats = {
    total: MOCK_ROUTES.length,
    closed: MOCK_ROUTES.filter((r) => r.status === "通行止め").length,
    tripsTotal: MOCK_ROUTES.reduce((acc, r) => acc + r.tripsThisMonth, 0),
    trucks: 24,
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">運搬ルート管理</h1>
          <p className="text-sm text-gray-500 mt-1">
            GIS/地図 — 資材運搬ルート・通行状況
          </p>
        </div>
        <Route className="w-8 h-8 text-blue-600" />
      </div>

      {/* 統計カード */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Route className="w-8 h-8 text-blue-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">登録ルート数</p>
            <p className="text-2xl font-bold text-gray-800">{stats.total}</p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <AlertTriangle className="w-8 h-8 text-red-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">通行止め数</p>
            <p className="text-2xl font-bold text-red-600">{stats.closed}</p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Truck className="w-8 h-8 text-green-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">今月通行回数</p>
            <p className="text-2xl font-bold text-gray-800">
              {stats.tripsTotal}
            </p>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4 flex items-center gap-3">
          <Truck className="w-8 h-8 text-purple-500 shrink-0" />
          <div>
            <p className="text-xs text-gray-500">資材運搬台数</p>
            <p className="text-2xl font-bold text-gray-800">{stats.trucks}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ルートテーブル */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg border overflow-hidden">
            <div className="px-4 py-3 border-b bg-gray-50">
              <h2 className="font-semibold text-gray-700">ルート一覧</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium text-gray-600">
                      ルート名
                    </th>
                    <th className="px-4 py-3 text-left font-medium text-gray-600">
                      出発地
                    </th>
                    <th className="px-4 py-3 text-left font-medium text-gray-600">
                      目的地
                    </th>
                    <th className="px-4 py-3 text-left font-medium text-gray-600">
                      距離
                    </th>
                    <th className="px-4 py-3 text-left font-medium text-gray-600">
                      所要時間
                    </th>
                    <th className="px-4 py-3 text-left font-medium text-gray-600">
                      制限重量
                    </th>
                    <th className="px-4 py-3 text-left font-medium text-gray-600">
                      通行状況
                    </th>
                    <th className="px-4 py-3 text-left font-medium text-gray-600">
                      今月回数
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {MOCK_ROUTES.map((route) => (
                    <tr
                      key={route.id}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      <td className="px-4 py-3 font-medium text-gray-900">
                        {route.name}
                      </td>
                      <td className="px-4 py-3 text-gray-600 text-xs">
                        {route.origin}
                      </td>
                      <td className="px-4 py-3 text-gray-600 text-xs">
                        {route.destination}
                      </td>
                      <td className="px-4 py-3 text-gray-600">
                        {route.distance}
                      </td>
                      <td className="px-4 py-3 text-gray-600">
                        {route.duration}
                      </td>
                      <td className="px-4 py-3 text-gray-600">
                        {route.weightLimit}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${STATUS_CONFIG[route.status].className}`}
                        >
                          <span
                            className={`w-1.5 h-1.5 rounded-full ${STATUS_CONFIG[route.status].dot}`}
                          />
                          {route.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-600 text-right">
                        {route.tripsThisMonth}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* 地図プレースホルダー */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-slate-800 rounded-lg overflow-hidden">
            <div className="h-72 flex flex-col items-center justify-center text-slate-400">
              <MapPin className="w-12 h-12 mb-3 text-slate-600" />
              <p className="text-base font-semibold text-slate-300">
                Route Map
              </p>
              <p className="text-xs mt-2 text-slate-500 text-center px-4">
                実装時は Mapbox / Leaflet を統合
              </p>
            </div>
          </div>

          {/* ステータス凡例 */}
          <div className="bg-white rounded-lg border p-4 space-y-2">
            <h3 className="font-semibold text-gray-700 text-sm">
              通行状況凡例
            </h3>
            {(Object.keys(STATUS_CONFIG) as RouteStatus[]).map((status) => (
              <div key={status} className="flex items-center gap-2 text-sm">
                <span
                  className={`w-2.5 h-2.5 rounded-full ${STATUS_CONFIG[status].dot}`}
                />
                <span className="text-gray-700">{status}</span>
                <span className="ml-auto text-gray-500 text-xs">
                  {MOCK_ROUTES.filter((r) => r.status === status).length} ルート
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
