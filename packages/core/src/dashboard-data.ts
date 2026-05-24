/**
 * Dashboard data types and content
 */
import type { ProjectStatus, DocumentStatus, WorkflowStatus, NotificationPriority } from './index';

// ============================================
// Dashboard Stat Cards
// ============================================
export interface DashboardStat {
  label: string;
  value: string;
  trend: string;
  trendUp: boolean;
  color: 'primary' | 'safety' | 'danger' | 'approve';
}

// ============================================
// Activity Feed
// ============================================
export interface ActivityItem {
  action: string;
  category: string;
  time: string;
  priority?: NotificationPriority;
}

// ============================================
// Quick Actions
// ============================================
export interface QuickAction {
  label: string;
  href: string;
}

// ============================================
// System Status
// ============================================
export interface SystemStatus {
  service: string;
  status: 'healthy' | 'degraded' | 'down';
  uptime?: string;
}

// ============================================
// Construction Project (for display)
// ============================================
export interface ConstructionProject {
  id: string;
  name: string;
  type: string;
  status: ProjectStatus;
  location: string;
  progress: number;
  startDate: string;
  endDate: string;
}

// ============================================
// Pending Approvals
// ============================================
export interface PendingApproval {
  id: string;
  document: string;
  project: string;
  submittedBy: string;
  submittedAt: string;
  status: WorkflowStatus;
}

// ============================================
// Default Dashboard Data
// ============================================

export const defaultStats: DashboardStat[] = [
  {
    label: '進行中プロジェクト',
    value: '21',
    trend: '全5レイヤ稼働中',
    trendUp: true,
    color: 'primary',
  },
  {
    label: 'アクティブサービス',
    value: '18',
    trend: '稼働率 100%',
    trendUp: true,
    color: 'approve',
  },
  {
    label: 'テストカバレッジ',
    value: '451',
    trend: 'ALL PASS',
    trendUp: true,
    color: 'approve',
  },
  {
    label: '実行中タスク',
    value: '6',
    trend: '自律化層 開発中',
    trendUp: true,
    color: 'primary',
  },
];

export const defaultActivities: ActivityItem[] = [
  {
    action: '認証サービスの全テストがパスしました',
    category: '認証基盤',
    time: '5分前',
    priority: 'normal',
  },
  {
    action: 'GISタイルサーバーのメトリクス更新',
    category: 'GIS基盤',
    time: '18分前',
    priority: 'normal',
  },
  {
    action: '文書管理サービスのヘルスチェック完了',
    category: '文書管理',
    time: '42分前',
    priority: 'normal',
  },
  {
    action: 'イベントバスのコンシューマー再起動',
    category: 'イベント基盤',
    time: '1時間前',
    priority: 'low',
  },
  {
    action: '通知サービスのレート制限メトリクス更新',
    category: '通知基盤',
    time: '2時間前',
    priority: 'low',
  },
];

export const defaultQuickActions: QuickAction[] = [
  { label: 'API Docs', href: '/docs' },
  { label: 'Swagger UI', href: '/docs' },
  { label: 'Redoc', href: '/redoc' },
  { label: 'GitHub', href: 'https://github.com/Kensan196948G/Construction-Enterprise-OS' },
];

export const defaultSystemStatus: SystemStatus[] = [
  { service: '認証基盤', status: 'healthy', uptime: '99.9%' },
  { service: 'API Gateway', status: 'healthy', uptime: '99.9%' },
  { service: 'イベント基盤', status: 'healthy', uptime: '99.8%' },
  { service: '文書管理', status: 'healthy', uptime: '99.7%' },
  { service: 'GIS基盤', status: 'healthy', uptime: '99.9%' },
  { service: '通知基盤', status: 'healthy', uptime: '99.9%' },
];

export const defaultConstructionProjects: ConstructionProject[] = [
  {
    id: 'prj-001',
    name: '認証基盤マイクロサービス',
    type: 'Foundation',
    status: 'in_progress',
    location: 'services/auth/',
    progress: 100,
    startDate: '2026-05-24',
    endDate: '2026-05-24',
  },
  {
    id: 'prj-002',
    name: 'API Gateway',
    type: 'Foundation',
    status: 'in_progress',
    location: 'services/gateway/',
    progress: 100,
    startDate: '2026-05-24',
    endDate: '2026-05-24',
  },
  {
    id: 'prj-003',
    name: 'GIS統合基盤',
    type: 'Data & AI',
    status: 'in_progress',
    location: 'services/gis/',
    progress: 100,
    startDate: '2026-05-24',
    endDate: '2026-05-24',
  },
  {
    id: 'prj-004',
    name: '自律化エンジン',
    type: 'Autonomous',
    status: 'planning',
    location: 'services/autonomous/',
    progress: 85,
    startDate: '2026-05-24',
    endDate: '2026-06-30',
  },
];
