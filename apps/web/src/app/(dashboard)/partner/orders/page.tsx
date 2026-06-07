"use client";

import { useState } from "react";
import {
  FileText,
  DollarSign,
  Truck,
  CheckCircle,
  Search,
  Plus,
} from "lucide-react";

interface Order {
  id: string;
  orderNo: string;
  projectName: string;
  companyName: string;
  amount: number;
  orderDate: string;
  workPeriod: string;
  progress: number;
  status: "draft" | "issued" | "in_progress" | "completed" | "cancelled";
}

const MOCK_ORDERS: Order[] = [
  {
    id: "O-001",
    orderNo: "2026-001",
    projectName: "品川タワー新築工事",
    companyName: "山田建設株式会社",
    amount: 12500000,
    orderDate: "2026-01-15",
    workPeriod: "2026/02〜2026/06",
    progress: 45,
    status: "in_progress",
  },
  {
    id: "O-002",
    orderNo: "2026-002",
    projectName: "大阪ビル改修工事",
    companyName: "鈴木電気工業",
    amount: 3200000,
    orderDate: "2026-02-01",
    workPeriod: "2026/02〜2026/04",
    progress: 80,
    status: "in_progress",
  },
  {
    id: "O-003",
    orderNo: "2026-003",
    projectName: "横浜工場設備更新",
    companyName: "田中設備工業",
    amount: 7800000,
    orderDate: "2026-01-20",
    workPeriod: "2026/01〜2026/03",
    progress: 100,
    status: "completed",
  },
  {
    id: "O-004",
    orderNo: "2026-004",
    projectName: "新宿オフィスビル建設",
    companyName: "佐藤建築工業",
    amount: 45000000,
    orderDate: "2026-01-10",
    workPeriod: "2026/01〜2026/08",
    progress: 30,
    status: "in_progress",
  },
  {
    id: "O-005",
    orderNo: "2026-005",
    projectName: "道路改良工事 A区間",
    companyName: "伊藤土木建設",
    amount: 18000000,
    orderDate: "2026-02-15",
    workPeriod: "2026/03〜2026/07",
    progress: 10,
    status: "issued",
  },
  {
    id: "O-006",
    orderNo: "2026-006",
    projectName: "工場電気設備工事",
    companyName: "中村電設工業",
    amount: 5600000,
    orderDate: "2026-02-20",
    workPeriod: "2026/03〜2026/04",
    progress: 0,
    status: "draft",
  },
  {
    id: "O-007",
    orderNo: "2025-098",
    projectName: "集合住宅設備工事",
    companyName: "小林管工事",
    amount: 9200000,
    orderDate: "2025-10-01",
    workPeriod: "2025/10〜2026/01",
    progress: 100,
    status: "completed",
  },
  {
    id: "O-008",
    orderNo: "2026-007",
    projectName: "倉庫新築工事",
    companyName: "渡辺建設工業",
    amount: 22000000,
    orderDate: "2026-03-01",
    workPeriod: "2026/03〜2026/06",
    progress: 5,
    status: "issued",
  },
];

const STATUS_LABELS: Record<Order["status"], string> = {
  draft: "下書き",
  issued: "発注済",
  in_progress: "施工中",
  completed: "完了",
  cancelled: "取消",
};

const STATUS_COLORS: Record<Order["status"], string> = {
  draft: "bg-gray-100 text-gray-600",
  issued: "bg-blue-100 text-blue-700",
  in_progress: "bg-yellow-100 text-yellow-700",
  completed: "bg-green-100 text-green-700",
  cancelled: "bg-red-100 text-red-700",
};

function ProgressBar({ value }: { value: number }) {
  const color =
    value === 100
      ? "bg-green-500"
      : value >= 50
        ? "bg-blue-500"
        : "bg-yellow-500";
  return (
    <div className="flex items-center gap-2">
      <div className="w-20 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${color}`}
          style={{ width: `${value}%` }}
        />
      </div>
      <span className="text-xs text-gray-600 w-8">{value}%</span>
    </div>
  );
}

export default function PartnerOrdersPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("すべて");

  const filtered = MOCK_ORDERS.filter((o) => {
    const matchSearch =
      o.projectName.includes(searchQuery) ||
      o.companyName.includes(searchQuery) ||
      o.orderNo.includes(searchQuery);
    const matchStatus = statusFilter === "すべて" || o.status === statusFilter;
    return matchSearch && matchStatus;
  });

  const inProgress = MOCK_ORDERS.filter(
    (o) => o.status === "in_progress" || o.status === "issued",
  ).length;
  const totalAmount = MOCK_ORDERS.filter(
    (o) => o.status !== "cancelled" && o.status !== "draft",
  ).reduce((sum, o) => sum + o.amount, 0);
  const completed = MOCK_ORDERS.filter((o) => o.status === "completed").length;
  const thisMonth = MOCK_ORDERS.filter((o) =>
    o.orderDate.startsWith("2026-03"),
  ).length;

  const formatAmount = (amount: number) =>
    new Intl.NumberFormat("ja-JP", {
      style: "currency",
      currency: "JPY",
      notation: "compact",
    }).format(amount);

  return (
    <div className="p-6 space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">発注管理</h1>
          <p className="text-sm text-gray-500 mt-1">
            協力会社への発注・進捗管理
          </p>
        </div>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
          <Plus className="w-4 h-4" />
          新規発注
        </button>
      </div>

      {/* 統計カード */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-50 rounded-lg">
              <Truck className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">発注中件数</p>
              <p className="text-2xl font-bold text-gray-900">{inProgress}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-50 rounded-lg">
              <DollarSign className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">発注総額</p>
              <p className="text-xl font-bold text-gray-900">
                {formatAmount(totalAmount)}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-50 rounded-lg">
              <CheckCircle className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">完了件数</p>
              <p className="text-2xl font-bold text-gray-900">{completed}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-50 rounded-lg">
              <FileText className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">今月発注</p>
              <p className="text-2xl font-bold text-gray-900">{thisMonth}</p>
            </div>
          </div>
        </div>
      </div>

      {/* フィルター */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="発注番号・工事件名・協力会社で検索..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="すべて">すべてのステータス</option>
            <option value="draft">下書き</option>
            <option value="issued">発注済</option>
            <option value="in_progress">施工中</option>
            <option value="completed">完了</option>
            <option value="cancelled">取消</option>
          </select>
        </div>
      </div>

      {/* テーブル */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  発注番号
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  工事件名
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  協力会社
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  発注金額
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  発注日
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  工期
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  進捗
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  ステータス
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((order) => (
                <tr
                  key={order.id}
                  className="hover:bg-gray-50 transition-colors cursor-pointer"
                >
                  <td className="px-4 py-3 font-mono text-xs text-gray-600">
                    {order.orderNo}
                  </td>
                  <td className="px-4 py-3 font-medium text-gray-900">
                    {order.projectName}
                  </td>
                  <td className="px-4 py-3 text-gray-700">
                    {order.companyName}
                  </td>
                  <td className="px-4 py-3 font-semibold text-gray-900">
                    ¥{order.amount.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-gray-600">{order.orderDate}</td>
                  <td className="px-4 py-3 text-gray-600 text-xs whitespace-nowrap">
                    {order.workPeriod}
                  </td>
                  <td className="px-4 py-3">
                    <ProgressBar value={order.progress} />
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[order.status]}`}
                    >
                      {STATUS_LABELS[order.status]}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-4 py-3 border-t border-gray-100 text-sm text-gray-500">
          {filtered.length}件表示 / 全{MOCK_ORDERS.length}件
        </div>
      </div>
    </div>
  );
}
