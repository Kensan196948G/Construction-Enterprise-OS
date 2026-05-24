"use client";

import { DollarSign, RefreshCw, TrendingUp, FileText } from "lucide-react";

const PRICES = [
  { id: 1, name: "土砂掘削工（機械）", unit: "m³", price: 850, region: "首都圏", validFrom: "2024-04-01", validTo: "2025-03-31", note: "建設機械賃料含む" },
  { id: 2, name: "コンクリート打設工", unit: "m³", price: 3200, region: "首都圏", validFrom: "2024-04-01", validTo: "2025-03-31", note: "型枠費用別途" },
  { id: 3, name: "鉄筋組立工", unit: "t", price: 85000, region: "首都圏", validFrom: "2024-04-01", validTo: "2025-03-31", note: "材料費別途" },
  { id: 4, name: "型枠工（パネル）", unit: "m²", price: 4500, region: "首都圏", validFrom: "2024-04-01", validTo: "2025-03-31", note: "脱型・清掃含む" },
  { id: 5, name: "左官工（モルタル塗）", unit: "m²", price: 2800, region: "首都圏", validFrom: "2024-07-01", validTo: "2025-03-31", note: "7月改定" },
  { id: 6, name: "電気工事（低圧）", unit: "点", price: 12000, region: "首都圏", validFrom: "2024-04-01", validTo: "2025-03-31", note: "コンセント・照明等" },
  { id: 7, name: "給排水工事", unit: "m", price: 18000, region: "首都圏", validFrom: "2024-04-01", validTo: "2025-03-31", note: "管材費含む" },
  { id: 8, name: "道路舗装工（アスファルト）", unit: "m²", price: 3600, region: "首都圏", validFrom: "2024-04-01", validTo: "2025-03-31", note: "T=50mm" },
  { id: 9, name: "外壁タイル工", unit: "m²", price: 9500, region: "首都圏", validFrom: "2024-10-01", validTo: "2025-03-31", note: "10月改定" },
  { id: 10, name: "足場組立・解体工", unit: "m²", price: 1200, region: "首都圏", validFrom: "2024-04-01", validTo: "2025-03-31", note: "建物延べ面積あたり" },
];

const HISTORY = [
  { date: "2024-10-01", name: "外壁タイル工", before: 8800, after: 9500, rate: 7.9 },
  { date: "2024-07-01", name: "左官工（モルタル塗）", before: 2600, after: 2800, rate: 7.7 },
  { date: "2024-04-01", name: "鉄筋組立工", before: 80000, after: 85000, rate: 6.3 },
  { date: "2024-04-01", name: "コンクリート打設工", before: 3000, after: 3200, rate: 6.7 },
];

export default function PricesPage() {
  const totalTypes = PRICES.length;
  const thisMonthRevised = HISTORY.filter((h) => h.date.startsWith("2024-10")).length;

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">単価マスタ</h1>
          <p className="text-sm text-gray-500 mt-1">工種別単価の管理・改定履歴</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
          <DollarSign className="w-4 h-4" />
          単価追加
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-blue-50 rounded-lg">
            <FileText className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">登録工種数</p>
            <p className="text-2xl font-bold text-gray-900">{totalTypes}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-orange-50 rounded-lg">
            <RefreshCw className="w-5 h-5 text-orange-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">今月改定数</p>
            <p className="text-2xl font-bold text-gray-900">{thisMonthRevised}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-green-50 rounded-lg">
            <TrendingUp className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">年間改定件数</p>
            <p className="text-2xl font-bold text-gray-900">{HISTORY.length}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-purple-50 rounded-lg">
            <DollarSign className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">適用地域</p>
            <p className="text-xl font-bold text-gray-900">首都圏</p>
          </div>
        </div>
      </div>

      {/* 単価テーブル */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-200">
          <h2 className="text-base font-semibold text-gray-900">工種別単価一覧</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left font-semibold text-gray-600">工種名</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">単位</th>
                <th className="px-4 py-3 text-right font-semibold text-gray-600 whitespace-nowrap">単価</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">適用地域</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">有効期間</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600">備考</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {PRICES.map((p) => (
                <tr key={p.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{p.name}</td>
                  <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{p.unit}</td>
                  <td className="px-4 py-3 text-gray-900 font-medium whitespace-nowrap text-right">
                    ¥{p.price.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{p.region}</td>
                  <td className="px-4 py-3 text-gray-600 whitespace-nowrap text-xs">
                    {p.validFrom} 〜 {p.validTo}
                  </td>
                  <td className="px-4 py-3 text-gray-500 text-xs">{p.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 改定履歴 */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-200">
          <h2 className="text-base font-semibold text-gray-900">改定履歴</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">改定日</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600">工種名</th>
                <th className="px-4 py-3 text-right font-semibold text-gray-600 whitespace-nowrap">変更前単価</th>
                <th className="px-4 py-3 text-right font-semibold text-gray-600 whitespace-nowrap">変更後単価</th>
                <th className="px-4 py-3 text-right font-semibold text-gray-600 whitespace-nowrap">変更率</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {HISTORY.map((h, i) => (
                <tr key={i} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{h.date}</td>
                  <td className="px-4 py-3 font-medium text-gray-900">{h.name}</td>
                  <td className="px-4 py-3 text-gray-500 whitespace-nowrap text-right">¥{h.before.toLocaleString()}</td>
                  <td className="px-4 py-3 text-gray-900 font-medium whitespace-nowrap text-right">¥{h.after.toLocaleString()}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-right">
                    <span className="flex items-center justify-end gap-1 text-red-600 font-medium">
                      <TrendingUp className="w-3.5 h-3.5" />
                      +{h.rate}%
                    </span>
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
