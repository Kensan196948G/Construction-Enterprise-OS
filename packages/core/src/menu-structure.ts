/**
 * Construction-Enterprise-OS サイドメニュー構造定義
 * 
 * 3階層構造: 大項目(カテゴリ) → 中項目(セクション) → 小項目(ページ)
 * 役割別に表示制御: site_supervisor(現場監督) / executive(経営層) / it_admin(IT管理者)
 */

export interface MenuPage {
  id: string;
  label: string;
  icon?: string;
  href: string;
  roles?: string[];      // 表示する役割 (未指定=全員)
  badge?: string;         // バッジ表示 (未読数等)
}

export interface MenuSection {
  id: string;
  label: string;
  icon: string;
  roles?: string[];
  defaultOpen?: boolean;
  pages: MenuPage[];
}

export interface MenuCategory {
  id: string;
  label: string;
  icon: string;
  sections: MenuSection[];
}

/** 役割定義 */
export const ROLES = {
  site_supervisor: { id: 'site_supervisor', label: '現場監督', color: '#f97316' },
  site_worker:     { id: 'site_worker',     label: '現場作業員', color: '#eab308' },
  executive:       { id: 'executive',       label: '経営層',     color: '#1a56db' },
  accountant:      { id: 'accountant',      label: '経理担当',   color: '#16a34a' },
  it_admin:        { id: 'it_admin',        label: 'IT管理者',   color: '#7c3aed' },
  safety_officer:  { id: 'safety_officer',  label: '安全管理者', color: '#dc2626' },
  inspector:       { id: 'inspector',       label: '検査員',     color: '#0891b2' },
  admin:           { id: 'admin',           label: 'システム管理者', color: '#000' },
} as const;

export type RoleId = keyof typeof ROLES;

/** 全メニュー定義 (3階層) */
export const MENU_STRUCTURE: MenuCategory[] = [
  {
    id: 'dashboard',
    label: '📊 ダッシュボード',
    icon: 'LayoutDashboard',
    sections: [
      {
        id: 'dash-overview',
        label: '概要',
        icon: 'Gauge',
        defaultOpen: true,
        pages: [
          { id: 'dash-company',    label: '全社統合ダッシュボード', href: '/dashboard/company',    roles: ['admin','executive','it_admin'] },
          { id: 'dash-site',       label: '現場ダッシュボード',     href: '/dashboard/site',       roles: ['site_supervisor','site_worker'] },
          { id: 'dash-executive',  label: '経営ダッシュボード',     href: '/dashboard/executive',  roles: ['executive','admin'] },
          { id: 'dash-ai',         label: 'AI分析ダッシュボード',   href: '/dashboard/ai',         roles: ['executive','admin'] },
          { id: 'dash-bim-gis',    label: 'BIM/GISビュー',         href: '/dashboard/bim-gis',    roles: ['site_supervisor','executive'] },
          { id: 'dash-kpi',        label: 'KPI/アラート',          href: '/dashboard/kpi',        roles: ['executive','admin'] },
        ]
      }
    ]
  },
  {
    id: 'foundation',
    label: '🏢 共通基盤',
    icon: 'Building2',
    sections: [
      {
        id: 'found-auth',
        label: '認証管理',
        icon: 'Key',
        pages: [
          { id: 'auth-entra',  label: 'Entra ID',   href: '/admin/auth/entra',  roles: ['it_admin','admin'] },
          { id: 'auth-ad',     label: 'AD連携',      href: '/admin/auth/ad',     roles: ['it_admin','admin'] },
          { id: 'auth-mfa',    label: 'MFA',         href: '/admin/auth/mfa',    roles: ['it_admin','admin'] },
          { id: 'auth-sso',    label: 'SSO',         href: '/admin/auth/sso',    roles: ['it_admin','admin'] },
        ]
      },
      {
        id: 'found-users',
        label: 'ユーザー管理',
        icon: 'Users',
        pages: [
          { id: 'users-list',    label: 'ユーザー一覧',   href: '/admin/users',        roles: ['it_admin','admin'] },
          { id: 'users-roles',   label: '権限管理',        href: '/admin/users/roles',   roles: ['it_admin','admin'] },
          { id: 'users-partner', label: '協力会社ユーザー', href: '/admin/users/partner', roles: ['it_admin','admin'] },
        ]
      },
      {
        id: 'found-system',
        label: 'システム管理',
        icon: 'Settings',
        pages: [
          { id: 'sys-api',        label: 'API管理',       href: '/admin/api',        roles: ['it_admin','admin'] },
          { id: 'sys-events',     label: 'イベント管理',    href: '/admin/events',     roles: ['it_admin','admin'] },
          { id: 'sys-notify',     label: '通知管理',        href: '/admin/notifications', roles: ['it_admin','admin'] },
          { id: 'sys-logs',       label: '共通ログ',        href: '/admin/logs',       roles: ['it_admin','admin'] },
          { id: 'sys-master',     label: 'マスタ管理',      href: '/admin/master',     roles: ['it_admin','admin'] },
          { id: 'sys-settings',   label: 'システム設定',     href: '/admin/settings',   roles: ['it_admin','admin'] },
        ]
      }
    ]
  },
  {
    id: 'documents',
    label: '📁 文書・図面管理',
    icon: 'FolderOpen',
    sections: [
      {
        id: 'doc-manage',
        label: '文書管理',
        icon: 'FileText',
        defaultOpen: true,
        pages: [
          { id: 'doc-pdf',     label: 'PDF管理',         href: '/documents/pdf' },
          { id: 'doc-cad',     label: 'CAD図面',          href: '/documents/cad' },
          { id: 'doc-bim',     label: 'BIM/CIM',          href: '/documents/bim' },
          { id: 'doc-photo',   label: '写真管理',         href: '/documents/photos' },
          { id: 'doc-video',   label: '動画管理',         href: '/documents/video' },
          { id: 'doc-ocr',     label: 'OCR',              href: '/documents/ocr',      roles: ['admin','it_admin'] },
          { id: 'doc-blackboard', label: '電子黒板',      href: '/documents/blackboard' },
          { id: 'doc-delivery',   label: '電子納品',      href: '/documents/delivery' },
          { id: 'doc-version',    label: 'バージョン管理',  href: '/documents/versions', roles: ['admin','it_admin'] },
          { id: 'doc-ai-search',  label: 'AI文書検索',     href: '/documents/ai-search' },
        ]
      }
    ]
  },
  {
    id: 'field-dx',
    label: '🏗 現場DX',
    icon: 'HardHat',
    sections: [
      {
        id: 'field-projects',
        label: '工事管理',
        icon: 'Building',
        defaultOpen: true,
        pages: [
          { id: 'field-list',       label: '工事一覧',         href: '/field/projects' },
          { id: 'field-progress',   label: '現場進捗',         href: '/field/progress' },
          { id: 'field-schedule',   label: '工程管理',         href: '/field/schedule' },
          { id: 'field-daily',      label: '作業日報',         href: '/field/daily-reports' },
          { id: 'field-photos',     label: '現場写真',         href: '/field/photos' },
          { id: 'field-asbuilt',    label: '出来形管理',       href: '/field/as-built' },
        ]
      },
      {
        id: 'field-safety',
        label: '安全管理',
        icon: 'Shield',
        pages: [
          { id: 'safety-mgmt',      label: '安全管理',         href: '/field/safety' },
          { id: 'safety-ky',        label: 'KY活動',           href: '/field/safety/ky' },
          { id: 'safety-hiyari',    label: 'ヒヤリハット',      href: '/field/safety/hiyari' },
          { id: 'safety-equipment', label: '重機管理',         href: '/field/equipment' },
          { id: 'safety-workers',   label: '作業員管理',       href: '/field/workers' },
          { id: 'safety-live',      label: '現場ライブビュー',   href: '/field/live-view' },
        ]
      }
    ]
  },
  {
    id: 'partners',
    label: '🤝 協力会社連携',
    icon: 'Handshake',
    sections: [
      {
        id: 'partner-mgmt',
        label: '協力会社管理',
        icon: 'Building2',
        pages: [
          { id: 'partner-list',     label: '協力会社一覧',     href: '/partners' },
          { id: 'partner-entry',    label: '入退場管理',       href: '/partners/entry-exit', roles: ['site_supervisor','safety_officer'] },
          { id: 'partner-docs',     label: '提出書類',         href: '/partners/documents' },
          { id: 'partner-training', label: '安全教育',         href: '/partners/training',   roles: ['safety_officer','site_supervisor'] },
          { id: 'partner-contracts',label: '契約管理',         href: '/partners/contracts',  roles: ['admin','executive'] },
          { id: 'partner-billing',  label: '請求管理',         href: '/partners/billing',    roles: ['admin','accountant'] },
          { id: 'partner-permits',  label: '作業申請',         href: '/partners/permits' },
          { id: 'partner-portal',   label: '協力会社ポータル',  href: '/partners/portal' },
        ]
      }
    ]
  },
  {
    id: 'gis',
    label: '🌏 GIS / 地図',
    icon: 'Map',
    sections: [
      {
        id: 'gis-maps',
        label: '地図情報',
        icon: 'MapPin',
        defaultOpen: true,
        pages: [
          { id: 'gis-sites',       label: '工事位置',             href: '/gis/sites' },
          { id: 'gis-marine',      label: '海域マップ',            href: '/gis/marine',       roles: ['site_supervisor','executive'] },
          { id: 'gis-disaster',    label: '災害情報',             href: '/gis/disaster' },
          { id: 'gis-drone',       label: 'ドローン地図',          href: '/gis/drone' },
          { id: 'gis-pointcloud',  label: '点群データ',            href: '/gis/pointcloud' },
          { id: 'gis-geology',     label: '地質情報',             href: '/gis/geology' },
          { id: 'gis-hazard',      label: 'ハザードマップ',        href: '/gis/hazard' },
          { id: 'gis-realtime',    label: 'リアルタイム位置情報',   href: '/gis/realtime' },
        ]
      }
    ]
  },
  {
    id: 'ai',
    label: '🧠 AI・分析基盤',
    icon: 'Brain',
    sections: [
      {
        id: 'ai-tools',
        label: 'AIツール',
        icon: 'Sparkles',
        defaultOpen: true,
        pages: [
          { id: 'ai-chat',       label: 'AIチャット',       href: '/ai/chat' },
          { id: 'ai-knowledge',  label: 'ナレッジAI',       href: '/ai/knowledge' },
          { id: 'ai-ocr',        label: 'OCR AI',           href: '/ai/ocr' },
          { id: 'ai-image',      label: '画像解析AI',       href: '/ai/image' },
          { id: 'ai-inspection', label: '点検AI',           href: '/ai/inspection',  roles: ['inspector','site_supervisor'] },
          { id: 'ai-design',     label: '設計照査AI',       href: '/ai/design-review', roles: ['admin','executive'] },
          { id: 'ai-predict',    label: '予測AI',           href: '/ai/predict',     roles: ['executive','admin'] },
          { id: 'ai-anomaly',    label: '異常検知AI',       href: '/ai/anomaly',     roles: ['it_admin','admin'] },
          { id: 'ai-training',   label: 'AI学習管理',       href: '/ai/training',    roles: ['it_admin','admin'] },
          { id: 'ai-agent',      label: 'AI Agent',         href: '/ai/agent',       roles: ['admin','it_admin'] },
        ]
      }
    ]
  },
  {
    id: 'iot',
    label: '📡 IoT・リアルタイム監視',
    icon: 'Radio',
    sections: [
      {
        id: 'iot-monitor',
        label: '監視',
        icon: 'Eye',
        pages: [
          { id: 'iot-sensors',   label: 'センサ一覧',       href: '/iot/sensors' },
          { id: 'iot-marine',    label: '海象情報',         href: '/iot/marine',      roles: ['site_supervisor','executive'] },
          { id: 'iot-weather',   label: '気象情報',         href: '/iot/weather' },
          { id: 'iot-wave',      label: '波浪監視',         href: '/iot/wave',        roles: ['site_supervisor','executive'] },
          { id: 'iot-water',     label: '水位監視',         href: '/iot/water-level' },
          { id: 'iot-gateway',   label: 'IoT Gateway',      href: '/iot/gateway',     roles: ['it_admin','admin'] },
          { id: 'iot-edge',      label: 'Edge AI',          href: '/iot/edge',        roles: ['it_admin','admin'] },
          { id: 'iot-alerts',    label: 'アラート管理',      href: '/iot/alerts' },
          { id: 'iot-realtime',  label: 'リアルタイム監視',  href: '/iot/realtime' },
        ]
      }
    ]
  },
  {
    id: 'erp',
    label: '🏢 ERP・経営管理',
    icon: 'PieChart',
    sections: [
      {
        id: 'erp-finance',
        label: '経理・原価',
        icon: 'DollarSign',
        pages: [
          { id: 'erp-cost',       label: '原価管理',        href: '/erp/cost' },
          { id: 'erp-budget',     label: '予算管理',        href: '/erp/budget' },
          { id: 'erp-contracts',  label: '契約管理',        href: '/erp/contracts' },
          { id: 'erp-procurement',label: '購買管理',        href: '/erp/procurement' },
          { id: 'erp-labor',      label: '労務管理',        href: '/erp/labor' },
          { id: 'erp-inventory',  label: '在庫管理',        href: '/erp/inventory' },
        ]
      },
      {
        id: 'erp-ledger',
        label: '工事台帳・分析',
        icon: 'FileSpreadsheet',
        pages: [
          { id: 'erp-ledger',     label: '工事台帳',        href: '/erp/ledger' },
          { id: 'erp-sales',      label: '売上管理',        href: '/erp/sales',        roles: ['executive','admin','accountant'] },
          { id: 'erp-analysis',   label: '経営分析',        href: '/erp/analysis',     roles: ['executive','admin'] },
          { id: 'erp-bi',         label: 'BIレポート',      href: '/erp/bi',           roles: ['executive','admin'] },
        ]
      }
    ]
  },
  {
    id: 'security',
    label: '🛡 セキュリティ・監査',
    icon: 'ShieldCheck',
    sections: [
      {
        id: 'sec-monitor',
        label: '監視・監査',
        icon: 'ScanEye',
        pages: [
          { id: 'sec-siem',        label: 'SIEM',           href: '/security/siem',       roles: ['it_admin','admin'] },
          { id: 'sec-soc',         label: 'SOC',            href: '/security/soc',        roles: ['it_admin','admin'] },
          { id: 'sec-vpn',         label: 'VPN監視',        href: '/security/vpn',        roles: ['it_admin','admin'] },
          { id: 'sec-edr',         label: 'EDR',            href: '/security/edr',        roles: ['it_admin','admin'] },
          { id: 'sec-ot',          label: 'OT監視',         href: '/security/ot',         roles: ['it_admin','admin'] },
          { id: 'sec-access',      label: 'アクセス監査',    href: '/security/access-audit', roles: ['it_admin','admin'] },
          { id: 'sec-logs',        label: '操作ログ',        href: '/security/operation-logs', roles: ['it_admin','admin'] },
          { id: 'sec-incidents',   label: 'インシデント',    href: '/security/incidents' },
          { id: 'sec-vuln',        label: '脆弱性管理',      href: '/security/vulnerabilities', roles: ['it_admin','admin'] },
          { id: 'sec-reports',     label: '監査レポート',    href: '/security/audit-reports', roles: ['admin','it_admin'] },
        ]
      }
    ]
  },
  {
    id: 'workflow',
    label: '🔄 ワークフロー',
    icon: 'GitBranch',
    sections: [
      {
        id: 'wf-main',
        label: '承認ワークフロー',
        icon: 'CheckCheck',
        defaultOpen: true,
        pages: [
          { id: 'wf-ringi',      label: '稟議',           href: '/workflow/ringi' },
          { id: 'wf-approval',   label: '承認',           href: '/workflow/approvals' },
          { id: 'wf-permit',     label: '作業許可',        href: '/workflow/permits' },
          { id: 'wf-electronic', label: '電子決裁',        href: '/workflow/electronic' },
          { id: 'wf-change',     label: '変更管理',        href: '/workflow/change' },
          { id: 'wf-distribute', label: '配布管理',        href: '/workflow/distribution' },
          { id: 'wf-notify',     label: '通知',           href: '/workflow/notifications' },
          { id: 'wf-sla',        label: 'SLA管理',        href: '/workflow/sla',        roles: ['admin','it_admin'] },
        ]
      }
    ]
  },
  {
    id: 'mobile',
    label: '📱 モバイル・PWA',
    icon: 'Smartphone',
    sections: [
      {
        id: 'mob-features',
        label: 'モバイル機能',
        icon: 'Wifi',
        pages: [
          { id: 'mob-offline',   label: 'オフライン同期',  href: '/mobile/offline' },
          { id: 'mob-photos',    label: 'モバイル写真',    href: '/mobile/photos' },
          { id: 'mob-voice',     label: '音声入力',        href: '/mobile/voice' },
          { id: 'mob-qr',        label: 'QR/Barcode',     href: '/mobile/qr' },
          { id: 'mob-gps',       label: 'GPS',            href: '/mobile/gps' },
          { id: 'mob-push',      label: 'Push通知',       href: '/mobile/push' },
          { id: 'mob-site',      label: '現場モバイル',    href: '/mobile/site' },
        ]
      }
    ]
  },
  {
    id: 'automation',
    label: '🤖 自動化・ロボティクス',
    icon: 'Bot',
    sections: [
      {
        id: 'auto-main',
        label: '自律システム',
        icon: 'Cpu',
        pages: [
          { id: 'auto-construction', label: '自動施工',       href: '/automation/construction' },
          { id: 'auto-marine',       label: '海洋ロボット',    href: '/automation/marine',      roles: ['site_supervisor','executive'] },
          { id: 'auto-drone',        label: 'ドローン',        href: '/automation/drone' },
          { id: 'auto-rov',          label: 'ROV',            href: '/automation/rov',         roles: ['site_supervisor'] },
          { id: 'auto-ai-control',   label: 'AI制御',         href: '/automation/ai-control',  roles: ['it_admin','admin'] },
          { id: 'auto-nav',          label: '自律航行',        href: '/automation/navigation', roles: ['site_supervisor'] },
          { id: 'auto-optimize',     label: '自動最適化',      href: '/automation/optimize',   roles: ['admin','it_admin'] },
          { id: 'auto-digital-twin', label: 'デジタルツイン',  href: '/automation/digital-twin' },
        ]
      }
    ]
  },
  {
    id: 'system',
    label: '⚙ システム管理',
    icon: 'ServerCog',
    sections: [
      {
        id: 'sys-admin',
        label: '運用管理',
        icon: 'MonitorCog',
        pages: [
          { id: 'sys-server',    label: 'サーバ監視',      href: '/admin/servers',      roles: ['it_admin','admin'] },
          { id: 'sys-db',        label: 'DB管理',          href: '/admin/database',     roles: ['it_admin','admin'] },
          { id: 'sys-backup',    label: 'バックアップ',     href: '/admin/backup',       roles: ['it_admin','admin'] },
          { id: 'sys-batch',     label: 'バッチ管理',       href: '/admin/batch',        roles: ['it_admin','admin'] },
          { id: 'sys-api-status',label: 'API状態',          href: '/admin/api-status',   roles: ['it_admin','admin'] },
          { id: 'sys-license',   label: 'ライセンス',       href: '/admin/license',      roles: ['it_admin','admin'] },
          { id: 'sys-update',    label: '更新管理',         href: '/admin/updates',      roles: ['it_admin','admin'] },
          { id: 'sys-devops',    label: 'DevOps/CI-CD',    href: '/admin/devops',       roles: ['it_admin','admin'] },
        ]
      }
    ]
  },
];

/** 役割別デフォルト展開カテゴリ */
export const ROLE_DEFAULT_OPEN: Record<string, string[]> = {
  site_supervisor: ['field-dx', 'documents', 'gis', 'workflow'],
  site_worker:     ['field-dx', 'mobile'],
  executive:       ['dashboard', 'erp', 'ai'],
  accountant:      ['erp', 'partners'],
  it_admin:        ['foundation', 'security', 'system'],
  safety_officer:  ['field-dx', 'partners'],
  inspector:       ['documents', 'ai', 'field-dx'],
  admin:           ['dashboard', 'foundation', 'security', 'system'],
};
