"use client";

import { useState, useEffect, useCallback } from "react";
import { Package, Boxes, DollarSign, RefreshCw } from "lucide-react";

type Material = {
  id: number;
  code: string;
  name: string;
  spec: string;
  unit: string;
  price: number;
  stock: number;
  category: string;
  updated: string;
};

const MOCK_MATERIALS: Material[] = [
  {
    id: 1,
    code: "MAT-001",
    name: "異形棒鋼 D13",
    spec: "SD345 D13×5.5m",
    unit: "t",
    price: 98000,
    stock: 25.5,
    category: "鉄筋",
    updated: "2024-11-01",
  },
  {
    id: 2,
    code: "MAT-002",
    name: "異形棒鋼 D16",
    spec: "SD345 D16×5.5m",
    unit: "t",
    price: 97000,
    stock: 18.2,
    category: "鉄筋",
    updated: "2024-11-01",
  },
  {
    id: 3,
    code: "MAT-003",
    name: "普通コンクリート Fc21",
    spec: "Fc21 スランプ12cm",
    unit: "m³",
    price: 14500,
    stock: 0,
    category: "コンクリート",
    updated: "2024-10-15",
  },
  {
    id: 4,
    code: "MAT-004",
    name: "普通コンクリート Fc24",
    spec: "Fc24 スランプ15cm",
    unit: "m³",
    price: 15200,
    stock: 0,
    category: "コンクリート",
    updated: "2024-10-15",
  },
  {
    id: 5,
    code: "MAT-005",
    name: "杉板型枠",
    spec: "厚さ12mm×幅90mm×3000mm",
    unit: "枚",
    price: 380,
    stock: 1200,
    category: "木材",
    updated: "2024-11-10",
  },
  {
    id: 6,
    code: "MAT-006",
    name: "合板型枠",
    spec: "12mm厚 900×1800",
    unit: "枚",
    price: 680,
    stock: 850,
    category: "木材",
    updated: "2024-11-10",
  },
  {
    id: 7,
    code: "MAT-007",
    name: "VVFケーブル 2.0×3C",
    spec: "2.0mm 3心 100m巻",
    unit: "巻",
    price: 12400,
    stock: 45,
    category: "電材",
    updated: "2024-09-20",
  },
  {
    id: 8,
    code: "MAT-008",
    name: "硬質塩ビ管 VU100",
    spec: "VU100 4m",
    unit: "本",
    price: 1850,
    stock: 320,
    category: "管材",
    updated: "2024-10-01",
  },
  {
    id: 9,
    code: "MAT-009",
    name: "単管パイプ 48.6φ",
    spec: "48.6mm 6m",
    unit: "本",
    price: 580,
    stock: 600,
    category: "仮設",
    updated: "2024-11-15",
  },
  {
    id: 10,
    code: "MAT-010",
    name: "クランプ（直交）",
    spec: "48.6mm用 直交型",
    unit: "個",
    price: 85,
    stock: 3200,
    category: "仮設",
    updated: "2024-11-15",
  },
  {
    id: 11,
    code: "MAT-011",
    name: "ポルトランドセメント",
    spec: "25kg袋 N種",
    unit: "袋",
    price: 840,
    stock: 8,
    category: "コンクリート",
    updated: "2024-11-20",
  },
  {
    id: 12,
    code: "MAT-012",
    name: "鉄筋スペーサー",
    spec: "PC製 D=60mm",
    unit: "個",
    price: 28,
    stock: 5000,
    category: "鉄筋",
    updated: "2024-10-05",
  },
];

const CATEGORY_COLORS: Record<string, string> = {
  鉄筋: "bg-red-100 text-red-800",
  コンクリート: "bg-gray-100 text-gray-700",
  木材: "bg-yellow-100 text-yellow-800",
  電材: "bg-blue-100 text-blue-800",
  管材: "bg-green-100 text-green-800",
  仮設: "bg-purple-100 text-purple-800",
};

export default function MaterialsPage() {
  const [materials, setMaterials] = useState<Material[]>(MOCK_MATERIALS);
  const [loading, setLoading] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/v1/construction/materials?per_page=50");
      if (!res.ok) {
        const res2 = await fetch("/api/v1/erp/materials?per_page=50");
        if (res2.ok) {
          const json = await res2.json();
          const data = json?.data?.items ?? json?.items ?? json?.data ?? [];
          if (Array.isArray(data) && data.length > 0) {
            setMaterials(
              data.map((item: Record<string, unknown>) => ({
                id: Number(item.id ?? 0),
                code: String(item.code ?? item.material_code ?? ""),
                name: String(item.name ?? ""),
                spec: String(item.spec ?? item.specification ?? ""),
                unit: String(item.unit ?? ""),
                price: Number(item.unit_price ?? item.price ?? 0),
                stock: Number(item.stock_quantity ?? item.stock ?? 0),
                category: String(item.material_type ?? item.category ?? ""),
                updated: String(item.updated_at ?? item.created_at ?? ""),
              })),
            );
          }
        }
        return;
      }
      const json = await res.json();
      const data = json?.data?.items ?? json?.items ?? json?.data ?? [];
      if (Array.isArray(data) && data.length > 0) {
        setMaterials(
          data.map((item: Record<string, unknown>) => ({
            id: Number(item.id ?? 0),
            code: String(item.code ?? item.material_code ?? ""),
            name: String(item.name ?? ""),
            spec: String(item.spec ?? item.specification ?? ""),
            unit: String(item.unit ?? ""),
            price: Number(item.unit_price ?? item.price ?? 0),
            stock: Number(item.stock_quantity ?? item.stock ?? 0),
            category: String(item.material_type ?? item.category ?? ""),
            updated: String(item.updated_at ?? item.created_at ?? ""),
          })),
        );
      }
    } catch {
      /* fallback to mock */
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const totalItems = materials.length;
  const thisMonthUpdated = materials.filter((m) =>
    m.updated.startsWith("2024-11"),
  ).length;
  const lowStock = materials.filter((m) => m.stock < 10).length;
  const priceRevision = 3;

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">資材マスタ</h1>
          <p className="text-sm text-gray-500 mt-1">
            建設資材・材料のマスタデータ管理
            {loading && (
              <span className="ml-2 text-blue-500 animate-pulse">
                読み込み中...
              </span>
            )}
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
          <Package className="w-4 h-4" />
          品目追加
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-blue-50 rounded-lg">
            <Package className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">総品目数</p>
            <p className="text-2xl font-bold text-gray-900">{totalItems}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-green-50 rounded-lg">
            <RefreshCw className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">今月更新</p>
            <p className="text-2xl font-bold text-gray-900">
              {thisMonthUpdated}
            </p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-orange-50 rounded-lg">
            <Boxes className="w-5 h-5 text-orange-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">低在庫</p>
            <p className="text-2xl font-bold text-gray-900">{lowStock}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-purple-50 rounded-lg">
            <DollarSign className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">単価改定予定</p>
            <p className="text-2xl font-bold text-gray-900">{priceRevision}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">
                  品目コード
                </th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600">
                  品名
                </th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600">
                  規格
                </th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">
                  単位
                </th>
                <th className="px-4 py-3 text-right font-semibold text-gray-600 whitespace-nowrap">
                  標準単価
                </th>
                <th className="px-4 py-3 text-right font-semibold text-gray-600 whitespace-nowrap">
                  在庫数
                </th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">
                  カテゴリ
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {materials.map((mat) => (
                <tr
                  key={mat.id}
                  className={`hover:bg-gray-50 ${mat.stock < 10 ? "bg-red-50" : ""}`}
                >
                  <td className="px-4 py-3 text-gray-500 whitespace-nowrap text-xs font-mono">
                    {mat.code}
                  </td>
                  <td className="px-4 py-3 font-medium text-gray-900">
                    {mat.name}
                  </td>
                  <td className="px-4 py-3 text-gray-600 text-xs">
                    {mat.spec}
                  </td>
                  <td className="px-4 py-3 text-gray-600 whitespace-nowrap">
                    {mat.unit}
                  </td>
                  <td className="px-4 py-3 text-gray-900 whitespace-nowrap text-right font-medium">
                    ¥{mat.price.toLocaleString()}
                  </td>
                  <td
                    className={`px-4 py-3 whitespace-nowrap text-right font-medium ${mat.stock < 10 ? "text-red-600" : "text-gray-900"}`}
                  >
                    {mat.stock.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${CATEGORY_COLORS[mat.category] ?? "bg-gray-100 text-gray-700"}`}
                    >
                      {mat.category}
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
