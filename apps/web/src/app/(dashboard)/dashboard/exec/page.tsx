"use client";

import { TrendingUp, DollarSign, BarChart3, Building } from "lucide-react";

const MONTHLY_DATA = [
  { month: "1月", revenue: 8.2, completion: 6.5, newOrders: 12.1 },
  { month: "2月", revenue: 9.4, completion: 7.8, newOrders: 8.3 },
  { month: "3月", revenue: 11.2, completion: 9.1, newOrders: 15.6 },
  { month: "4月", revenue: 10.8, completion: 8.4, newOrders: 11.2 },
  { month: "5月", revenue: 12.1, completion: 10.3, newOrders: 9.8 },
];

const PROJECTS = [
  {
    name: "大阪オフィスビル新築工事",
    budget: 42.0,
    actual: 38.5,
    progress: 82,
    deadline: "2026-11-30",
    status: "順調",
  },
  {
    name: "国道XX号線橋梁工事",
    budget: 28.5,
    actual: 24.1,
    progress: 68,
    deadline: "2027-03-31",
    status: "順調",
  },
  {
    name: "山岳トンネル掘削工事",
    budget: 65.0,
    actual: 41.2,
    progress: 55,
    deadline: "2027-09-30",
    status: "注意",
  },
  {
    name: "都市再開発第2期工事",
    budget: 35.2,
    actual: 12.8,
    progress: 28,
    deadline: "2028-03-31",
    status: "順調",
  },
  {
    name: "港湾設備整備工事",
    budget: 18.7,
    actual: 19.4,
    progress: 91,
    deadline: "2026-07-31",
    status: "超過",
  },
];

const STATUS_COLORS: Record<string, string> = {
  順調: "bg-green-100 text-green-800",
  注意: "bg-yellow-100 text-yellow-800",
  超過: "bg-red-100 text-red-800",
};

const maxRevenue = Math.max(...MONTHLY_DATA.map((r) => r.revenue));

export default function ExecDashboardPage() {
  const kpis = [
    {
      label: "売上高 (今月)",
      value: "12.1億円",
      sub: "前月比 +12.0%",
      icon: DollarSign,
      color: "text-blue-600",
      bg: "bg-blue-50",
    },
    {
      label: "営業利益率",
      value: "8.4%",
      sub: "目標: 8.0%",
      icon: TrendingUp,
      color: "text-green-600",
      bg: "bg-green-50",
    },
    {
      label: "受注残高",
      value: "189.4億円",
      sub: "前期比 +5.2%",
      icon: BarChart3,
      color: "text-purple-600",
      bg: "bg-purple-50",
    },
    {
      label: "完工件数 (今月)",
      value: "3件",
      sub: "年累計: 18件",
      icon: Building,
      color: "text-orange-600",
      bg: "bg-orange-50",
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            経営ダッシュボード
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            ダッシュボード — 売上・利益・受注状況
          </p>
        </div>
        <TrendingUp className="w-8 h-8 text-blue-600" />
      </div>

      {/* KPIカード */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <div key={kpi.label} className="bg-white rounded-lg border p-4">
              <div
                className={`w-10 h-10 rounded-lg ${kpi.bg} flex items-center justify-center mb-3`}
              >
                <Icon className={`w-5 h-5 ${kpi.color}`} />
              </div>
              <p className="text-xs text-gray-500">{kpi.label}</p>
              <p className="text-xl font-bold text-gray-900 mt-0.5">
                {kpi.value}
              </p>
              <p className="text-xs text-gray-400 mt-1">{kpi.sub}</p>
            </div>
          );
        })}
      </div>

      {/* 月別売上グラフ代替テーブル */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="px-4 py-3 border-b bg-gray-50">
          <h2 className="font-semibold text-gray-700">
            月別実績サマリー（億円）
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  月
                </th>
                <th className="px-4 py-3 text-right font-medium text-gray-600">
                  売上高
                </th>
                <th className="px-4 py-3 text-right font-medium text-gray-600">
                  完工高
                </th>
                <th className="px-4 py-3 text-right font-medium text-gray-600">
                  新規受注
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600 pl-8">
                  売上高バー
                </th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {MONTHLY_DATA.map((row) => {
                const pct = Math.round((row.revenue / maxRevenue) * 100);
                return (
                  <tr key={row.month} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-800">
                      {row.month}
                    </td>
                    <td className="px-4 py-3 text-right font-semibold text-blue-700">
                      {row.revenue.toFixed(1)}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-600">
                      {row.completion.toFixed(1)}
                    </td>
                    <td className="px-4 py-3 text-right text-green-600">
                      {row.newOrders.toFixed(1)}
                    </td>
                    <td className="px-4 py-3 pl-8">
                      <div className="flex items-center gap-2">
                        <div className="w-40 h-3 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-500 rounded-full"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-400">{pct}%</span>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
            <tfoot className="bg-gray-50 border-t">
              <tr>
                <td className="px-4 py-3 font-semibold text-gray-700">合計</td>
                <td className="px-4 py-3 text-right font-bold text-blue-700">
                  {MONTHLY_DATA.reduce((a, r) => a + r.revenue, 0).toFixed(1)}
                </td>
                <td className="px-4 py-3 text-right font-semibold text-gray-600">
                  {MONTHLY_DATA.reduce((a, r) => a + r.completion, 0).toFixed(
                    1,
                  )}
                </td>
                <td className="px-4 py-3 text-right font-semibold text-green-600">
                  {MONTHLY_DATA.reduce((a, r) => a + r.newOrders, 0).toFixed(1)}
                </td>
                <td className="px-4 py-3" />
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      {/* 進行中プロジェクト要約 */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="px-4 py-3 border-b bg-gray-50">
          <h2 className="font-semibold text-gray-700">
            進行中プロジェクト要約
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  プロジェクト名
                </th>
                <th className="px-4 py-3 text-right font-medium text-gray-600">
                  予算 (億円)
                </th>
                <th className="px-4 py-3 text-right font-medium text-gray-600">
                  実績 (億円)
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  進捗
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  完工予定
                </th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">
                  ステータス
                </th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {PROJECTS.map((p) => (
                <tr key={p.name} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">
                    {p.name}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-600">
                    {p.budget.toFixed(1)}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-700 font-medium">
                    {p.actual.toFixed(1)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2.5 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            p.progress >= 90
                              ? "bg-green-500"
                              : p.progress >= 50
                                ? "bg-blue-500"
                                : "bg-yellow-500"
                          }`}
                          style={{ width: `${p.progress}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-600 font-medium">
                        {p.progress}%
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-500 text-xs">
                    {p.deadline}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[p.status]}`}
                    >
                      {p.status}
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
