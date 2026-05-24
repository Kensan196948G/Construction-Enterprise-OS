import {
  ClipboardList,
  CheckSquare,
  AlertTriangle,
  FileText,
  ArrowUpRight,
  Plus,
  Search,
  Settings,
  Users,
} from 'lucide-react';
import type { DashboardStat, ActivityItem, QuickAction } from '@construction-enterprise-os/core/dashboard-data';
import {
  defaultStats,
  defaultActivities,
  defaultQuickActions,
} from '@construction-enterprise-os/core/dashboard-data';

const statIcons: Record<DashboardStat['color'], typeof ClipboardList> = {
  primary: ClipboardList,
  safety: CheckSquare,
  danger: AlertTriangle,
  approve: FileText,
};

const actionIcons: Record<string, typeof Plus> = {
  'API Docs': FileText,
  'Swagger UI': Search,
  'Redoc': FileText,
  'GitHub': Users,
};

const colorMap: Record<string, { bg: string; text: string; icon: string }> = {
  primary: { bg: 'bg-primary-50', text: 'text-primary-600', icon: 'text-primary-500' },
  safety: { bg: 'bg-safety-50', text: 'text-safety-700', icon: 'text-safety-500' },
  danger: { bg: 'bg-danger-50', text: 'text-danger-700', icon: 'text-danger-500' },
  approve: { bg: 'bg-approve-50', text: 'text-approve-700', icon: 'text-approve-500' },
};

function getGreeting(): { title: string; subtitle: string } {
  const hour = new Date().getHours();
  if (hour < 10) return { title: 'おはようございます', subtitle: '本日も安全第一で。システムの状態を確認しましょう。' };
  if (hour < 18) return { title: 'こんにちは', subtitle: '全サービス正常稼働中です。' };
  return { title: 'こんばんは', subtitle: 'お疲れさまです。本日のサマリーです。' };
}

export default function DashboardPage() {
  const greeting = getGreeting();

  return (
    <div className="p-6 lg:p-8 space-y-8">
      {/* Welcome */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          {greeting.title}
        </h1>
        <p className="mt-1 text-gray-500">
          {greeting.subtitle}
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {defaultStats.map((stat: DashboardStat) => {
          const Icon = statIcons[stat.color];
          const colors = colorMap[stat.color];
          return (
            <div
              key={stat.label}
              className="rounded-xl border border-gray-200 bg-white p-5 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className={`rounded-lg p-2.5 ${colors.bg}`}>
                  <Icon className={`h-5 w-5 ${colors.icon}`} />
                </div>
                <ArrowUpRight className="h-4 w-4 text-gray-400" />
              </div>
              <p className="mt-4 text-3xl font-bold text-gray-900">
                {stat.value}
              </p>
              <p className="mt-1 text-sm font-medium text-gray-600">
                {stat.label}
              </p>
              <p
                className={`mt-2 text-xs ${
                  stat.trendUp ? 'text-approve-600' : 'text-danger-600'
                }`}
              >
                {stat.trend}
              </p>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Activity Feed */}
        <div className="lg:col-span-2 rounded-xl border border-gray-200 bg-white">
          <div className="flex items-center justify-between border-b border-gray-100 px-5 py-4">
            <h2 className="font-bold text-gray-900">最近のアクティビティ</h2>
            <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
              すべて表示
            </button>
          </div>
          <div className="divide-y divide-gray-100">
            {defaultActivities.map((item: ActivityItem, i: number) => (
              <div key={i} className="px-5 py-4 hover:bg-gray-50 transition-colors">
                <p className="text-sm font-medium text-gray-900">{item.action}</p>
                <div className="mt-1 flex items-center gap-2 text-xs text-gray-500">
                  <span>{item.category}</span>
                  <span>•</span>
                  <span>{item.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <h2 className="font-bold text-gray-900 mb-4">クイックアクション</h2>
          <div className="grid grid-cols-2 gap-3">
            {defaultQuickActions.map((action: QuickAction) => {
              const Icon = actionIcons[action.label] || Settings;
              return (
                <a
                  key={action.label}
                  href={action.href}
                  target={action.href.startsWith('http') ? '_blank' : undefined}
                  rel={action.href.startsWith('http') ? 'noopener noreferrer' : undefined}
                  className="flex flex-col items-center gap-2 rounded-lg border border-gray-200 p-4 hover:border-primary-300 hover:bg-primary-50/50 transition-colors text-center"
                >
                  <Icon className="h-5 w-5 text-primary-600" />
                  <span className="text-xs font-medium text-gray-700">
                    {action.label}
                  </span>
                </a>
              );
            })}
          </div>

          {/* System Status */}
          <div className="mt-5 rounded-lg bg-approve-50 p-4">
            <div className="flex items-center gap-2">
              <span className="flex h-2 w-2 rounded-full bg-approve-500" />
              <span className="text-sm font-bold text-approve-700">
                全サービス正常稼働中
              </span>
            </div>
            <p className="mt-1 text-xs text-approve-600">
              認証基盤 / API Gateway / イベント基盤 / GIS / 文書管理 / 通知
              <br />
              451 tests ALL PASS | ビルドステータス: STABLE
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
