"use client";

import { useState, useEffect, useCallback } from "react";
import { TrendingUp, DollarSign, BarChart3, Building } from "lucide-react";

const MONTHLY_DATA = [
  { month: "1月", revenue: 8.2, completion: 6.5, newOrders: 12.1 },
  { month: "2月", revenue: 9.4, completion: 7.8, newOrders: 8.3 },
  { month: "3月", revenue: 11.2, completion: 9.1, newOrders: 15.6 },
  { month: "4月", revenue: 10.8, completion: 8.4, newOrders: 11.2 },
  { month: "5月", revenue: 12.1, completion: 10.3, newOrders: 9.8 },
];

interface LedgerItem {
  id: string;
  project_name: string;
  budget_amount: number;
  actual_cost: number;
  progress_rate: number;
  completion_date: string | null;
  status: string;
}

const MOCK_PROJECTS: LedgerItem[] = [
  {
    id: "1",
    project_name: "大阪オフィスビル新築工事",
    budget_amount: 4200000000,
    actual_cost: 3850000000,
    progress_rate: 82,
    completion_date: "2026-11-30",
    status: "in_progress",
  },
  {
    id: "2",
    project_name: "国道XX号線橋梁工事",
    budget_amount: 2850000000,
    actual_cost: 2410000000,
    progress_rate: 68,
    completion_date: "2027-03-31",
    status: "in_progress",
  },
  {
    id: "3",
    project_name: "山岳トンネル掘削工事",
    budget_amount: 6500000000,
    actual_cost: 4120000000,
    progress_rate: 55,
    completion_date: "2027-09-30",
    status: "in_progress",
  },
  {
    id: "4",
    project_name: "都市再開発第2期工事",
    budget_amount: 3520000000,
    actual_cost: 1280000000,
    progress_rate: 28,
    completion_date: "2028-03-31",
    status: "in_progress",
  },
  {
    id: "5",
    project_name: "港湾設備整備工事",
    budget_amount: 1870000000,
    actual_cost: 1940000000,
    progress_rate: 91,
    completion_date: "2026-07-31",
    status: "over_budget",
  },
];

function formatOkuYen(amount: number): string {
  return (amount / 100000000).toFixed(1);
}

function getProjectStatus(item: LedgerItem): { label: string; color: string } {
  if (item.status === "over_budget" || item.actual_cost > item.budget_amount) {
    return { label: "超過", color: "bg-red-100 text-red-800" };
  }
  if (item.progress_rate < 50) {
    return { label: "注意", color: "bg-yellow-100 text-yellow-800" };
  }
  return { label: "順調", color: "bg-green-100 text-green-800" };
}

export default function ExecDashboardPage() {
  const [projects, setProjects] = useState<LedgerItem[]>(MOCK_PROJECTS);
  const [loading, setLoading] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/v1/erp/ledger?per_page=20");
      if (res.ok) {
        const json = await res.json();
        const items = json?.data?.items ?? json?.items;
        if (Array.isArray(items) && items.length > 0) {
          setProjects(
            items.map(
              (item: Record<string, unknown>): LedgerItem => ({
                id: String(item.id ?? ""),
                project_name: String(item.project_name ?? ""),
                budget_amount: Number(item.budget_amount ?? 0),
                actual_cost: Number(item.actual_cost ?? 0),
                progress_rate: Number(item.progress_rate ?? 0),
                completion_date: item.completion_date
                  ? String(item.completion_date)
                  : null,
                status: String(item.status ?? "in_progress"),
              }),
            ),
          );
        }
      }
    } catch {
      // fallback to mock data
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const totalBudget = projects.reduce((s, p) => s + p.budget_amount, 0);
  const totalActual = projects.reduce((s, p) => s + p.actual_cost, 0);
  const overBudgetCount = projects.filter(
    (p) => p.actual_cost > p.budget_amount,
  ).length;
  const maxRevenue = Math.max(...MONTHLY_DATA.map((r) => r.revenue));

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
      value: `${formatOkuYen(totalBudget)}億円`,
      sub: `${projects.length}件進行中`,
      icon: BarChart3,
      color: "text-purple-600",
      bg: "bg-purple-50",
    },
    {
      label: "予算超過プロジェクト",
      value: `${overBudgetCount}件`,
      sub: `総実績: ${formatOkuYen(totalActual)}億円`,
      icon: Building,
      color: overBudgetCount > 0 ? "text-red-600" : "text-orange-600",
      bg: overBudgetCount > 0 ? "bg-red-50" : "bg-orange-50",
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

      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="px-4 py-3 border-b bg-gray-50 flex items-center justify-between">
          <h2 className="font-semibold text-gray-700">
            進行中プロジェクト要約
          </h2>
          {loading && (
            <span className="text-xs text-gray-400 animate-pulse">
              読み込み中...
            </span>
          )}
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
              {projects.map((p) => {
                const { label, color } = getProjectStatus(p);
                return (
                  <tr key={p.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">
                      {p.project_name}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-600">
                      {formatOkuYen(p.budget_amount)}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-700 font-medium">
                      {formatOkuYen(p.actual_cost)}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-2.5 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              p.progress_rate >= 90
                                ? "bg-green-500"
                                : p.progress_rate >= 50
                                  ? "bg-blue-500"
                                  : "bg-yellow-500"
                            }`}
                            style={{
                              width: `${Math.min(100, p.progress_rate)}%`,
                            }}
                          />
                        </div>
                        <span className="text-xs text-gray-600 font-medium">
                          {p.progress_rate}%
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-gray-500 text-xs">
                      {p.completion_date ?? "—"}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${color}`}
                      >
                        {label}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
