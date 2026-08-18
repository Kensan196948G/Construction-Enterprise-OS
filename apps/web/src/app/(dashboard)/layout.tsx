"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Building2,
  FileText,
  HardHat,
  Users,
  Map,
  Brain,
  Cpu,
  BarChart3,
  Shield,
  GitBranch,
  Bot,
  Settings,
  Menu,
  X,
  LogOut,
  ChevronDown,
  ChevronRight,
  Bell,
  Moon,
  Sun,
  UserCircle,
} from "lucide-react";
import { useAuthStore } from "@/lib/store/auth";
import { isAuthBypassEnabled } from "@/lib/auth-config";

// ────────────────────────────────────────────────────────────────────────────
// Types
// ────────────────────────────────────────────────────────────────────────────

interface NavPage {
  label: string;
  href: string;
  badge?: string;
}

interface NavSection {
  id: string;
  label: string;
  roles?: string[];
  pages: NavPage[];
  defaultOpen?: boolean;
}

interface NavCategory {
  id: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  sections: NavSection[];
}

// ────────────────────────────────────────────────────────────────────────────
// Role definitions (matching design)
// ────────────────────────────────────────────────────────────────────────────

const ROLES = {
  "": { label: "全表示（管理者）", color: "#7c3aed" },
  admin: { label: "IT管理者", color: "#7c3aed" },
  field: { label: "現場監督", color: "#f97316" },
  exec: { label: "経営層", color: "#1a56db" },
  partner: { label: "協力会社", color: "#16a34a" },
  safety: { label: "安全管理者", color: "#dc2626" },
  maintain: { label: "維持管理", color: "#92400e" },
} as const;

type RoleKey = keyof typeof ROLES;

// ────────────────────────────────────────────────────────────────────────────
// Menu structure (3-level: category → section → page)
// ────────────────────────────────────────────────────────────────────────────

const MENU_STRUCTURE: NavCategory[] = [
  {
    id: "dashboard",
    icon: LayoutDashboard,
    label: "ダッシュボード",
    sections: [
      {
        id: "dash-main",
        label: "統合ダッシュボード",
        defaultOpen: true,
        pages: [
          { label: "全社統合", href: "/dashboard" },
          { label: "現場ダッシュボード", href: "/dashboard/field" },
          { label: "経営ダッシュボード", href: "/dashboard/exec" },
          { label: "AI分析", href: "/dashboard/ai" },
          { label: "KPI/アラート", href: "/dashboard/kpi", badge: "3" },
        ],
      },
    ],
  },
  {
    id: "common",
    icon: Building2,
    label: "共通基盤",
    sections: [
      {
        id: "auth",
        label: "認証管理",
        roles: ["admin"],
        pages: [
          { label: "Entra ID", href: "/common/auth/entra" },
          { label: "AD連携", href: "/common/auth/ad" },
          { label: "MFA", href: "/common/auth/mfa" },
          { label: "SSO", href: "/common/auth/sso" },
        ],
      },
      {
        id: "user-mgmt",
        label: "ユーザー管理",
        roles: ["admin"],
        pages: [
          { label: "ユーザー一覧", href: "/common/users" },
          { label: "ロール管理", href: "/common/roles" },
          { label: "組織管理", href: "/common/org" },
        ],
      },
      {
        id: "api-mgmt",
        label: "API管理",
        roles: ["admin"],
        pages: [
          { label: "APIクライアント", href: "/common/api/clients" },
          { label: "Webhook", href: "/common/api/webhooks" },
        ],
      },
      {
        id: "master",
        label: "マスタ管理",
        roles: ["admin"],
        pages: [
          { label: "工種マスタ", href: "/common/master/work-types" },
          { label: "材料マスタ", href: "/common/master/materials" },
          { label: "単価マスタ", href: "/common/master/prices" },
        ],
      },
    ],
  },
  {
    id: "documents",
    icon: FileText,
    label: "文書・図面管理",
    sections: [
      {
        id: "docs-main",
        label: "文書管理",
        pages: [
          { label: "文書一覧", href: "/documents" },
          { label: "図面管理", href: "/documents/drawings" },
          { label: "承認ワークフロー", href: "/documents/approval" },
          { label: "BIM/CIM", href: "/documents/bim" },
        ],
      },
    ],
  },
  {
    id: "field-dx",
    icon: HardHat,
    label: "現場DX",
    sections: [
      {
        id: "projects",
        label: "工事管理",
        pages: [
          { label: "工事一覧", href: "/projects" },
          { label: "工程管理", href: "/projects/schedule" },
          { label: "WBS", href: "/projects/wbs" },
          { label: "日報・週報", href: "/projects/reports" },
        ],
      },
      {
        id: "field-ops",
        label: "現場作業",
        pages: [
          { label: "作業指示", href: "/field/instructions" },
          { label: "進捗入力", href: "/field/progress" },
          { label: "写真管理", href: "/field/photos" },
          { label: "品質チェック", href: "/field/quality" },
        ],
      },
    ],
  },
  {
    id: "partner",
    icon: Users,
    label: "協力会社連携",
    sections: [
      {
        id: "partner-main",
        label: "協力会社",
        pages: [
          { label: "協力会社一覧", href: "/partner/companies" },
          { label: "発注管理", href: "/partner/orders" },
          { label: "実績評価", href: "/partner/evaluation" },
          { label: "ポータル", href: "/partner/portal" },
        ],
      },
    ],
  },
  {
    id: "gis",
    icon: Map,
    label: "GIS/地図",
    sections: [
      {
        id: "gis-main",
        label: "地図・GIS",
        pages: [
          { label: "施工現場マップ", href: "/gis" },
          { label: "路線管理", href: "/gis/routes" },
          { label: "3Dビュー", href: "/gis/3d" },
          { label: "UAV/ドローン", href: "/gis/uav" },
        ],
      },
    ],
  },
  {
    id: "ai",
    icon: Brain,
    label: "AI・分析基盤",
    sections: [
      {
        id: "ai-main",
        label: "AI分析",
        pages: [
          { label: "施工AI", href: "/ai/construction" },
          { label: "予知保全", href: "/ai/predictive" },
          { label: "点検AI", href: "/ai/inspection" },
          { label: "OCR/画像認識", href: "/ai/ocr" },
          { label: "レポート生成", href: "/ai/reports" },
        ],
      },
    ],
  },
  {
    id: "iot",
    icon: Cpu,
    label: "IoT・リアルタイム監視",
    sections: [
      {
        id: "iot-main",
        label: "IoT監視",
        pages: [
          { label: "センサーダッシュボード", href: "/iot" },
          { label: "機械稼働監視", href: "/iot/machines" },
          { label: "環境モニタリング", href: "/iot/environment" },
          { label: "アラート管理", href: "/iot/alerts" },
        ],
      },
    ],
  },
  {
    id: "erp",
    icon: BarChart3,
    label: "ERP・経営管理",
    sections: [
      {
        id: "erp-main",
        label: "経営管理",
        roles: ["exec", "admin"],
        pages: [
          { label: "ERP概要", href: "/erp" },
          { label: "原価管理", href: "/erp/cost" },
          { label: "請求・支払", href: "/erp/invoices" },
          { label: "予算管理", href: "/erp/budget" },
          { label: "財務レポート", href: "/erp/finance" },
        ],
      },
    ],
  },
  {
    id: "security",
    icon: Shield,
    label: "セキュリティ・監査",
    sections: [
      {
        id: "security-main",
        label: "セキュリティ",
        roles: ["admin"],
        pages: [
          { label: "安全管理", href: "/safety" },
          { label: "監査ログ", href: "/security/audit" },
          { label: "脆弱性管理", href: "/security/vulnerabilities" },
          { label: "ISMS", href: "/security/isms" },
        ],
      },
    ],
  },
  {
    id: "workflow",
    icon: GitBranch,
    label: "ワークフロー",
    sections: [
      {
        id: "workflow-main",
        label: "承認・ワークフロー",
        pages: [
          { label: "ワークフロー一覧", href: "/workflows" },
          { label: "申請一覧", href: "/workflows/requests" },
          { label: "承認待ち", href: "/workflows/pending", badge: "5" },
          { label: "テンプレート", href: "/workflows/templates" },
        ],
      },
    ],
  },
  {
    id: "robotics",
    icon: Bot,
    label: "自動化・ロボティクス",
    sections: [
      {
        id: "robotics-main",
        label: "自律化",
        pages: [
          { label: "自律施工", href: "/robotics/autonomous" },
          { label: "ドローン制御", href: "/robotics/drone" },
          { label: "デジタルツイン", href: "/robotics/twin" },
          { label: "RPA", href: "/robotics/rpa" },
        ],
      },
    ],
  },
  {
    id: "system",
    icon: Settings,
    label: "システム管理",
    sections: [
      {
        id: "system-main",
        label: "設定・管理",
        roles: ["admin"],
        pages: [
          { label: "システム設定", href: "/settings" },
          { label: "通知設定", href: "/settings/notifications" },
          { label: "インテグレーション", href: "/settings/integrations" },
          { label: "バックアップ", href: "/settings/backup" },
        ],
      },
    ],
  },
];

// ────────────────────────────────────────────────────────────────────────────
// CSS variables for dark / light mode
// ────────────────────────────────────────────────────────────────────────────

const LIGHT_VARS: Record<string, string> = {
  "--bg": "#f8fafc",
  "--bg-page": "#f8fafc",
  "--bg-card": "#ffffff",
  "--bg-card-hover": "#f8fafc",
  "--bg-subtle": "#f8fafc",
  "--bg-input": "#f8fafc",
  "--border": "#e2e8f0",
  "--border-light": "#f1f5f9",
  "--text": "#0f172a",
  "--text-secondary": "#374151",
  "--text-muted": "#64748b",
  "--text-heading": "#0f172a",
  "--accent": "#1a56db",
  "--accent-light": "#eff6ff",
  "--shadow": "rgba(0,0,0,0.08)",
  "--sidebar-bg": "#0f172a",
  "--sidebar-border": "rgba(148,163,184,0.12)",
  "--header-bg": "#ffffff",
};

const DARK_VARS: Record<string, string> = {
  "--bg": "#0f172a",
  "--bg-page": "#0f172a",
  "--bg-card": "#1e293b",
  "--bg-card-hover": "#273549",
  "--bg-subtle": "#1e293b",
  "--bg-input": "#1e293b",
  "--border": "#334155",
  "--border-light": "#1e293b",
  "--text": "#e2e8f0",
  "--text-secondary": "#cbd5e1",
  "--text-muted": "#94a3b8",
  "--text-heading": "#f1f5f9",
  "--accent": "#3b82f6",
  "--accent-light": "#1e3a5f",
  "--shadow": "rgba(0,0,0,0.3)",
  "--sidebar-bg": "#020617",
  "--sidebar-border": "rgba(148,163,184,0.08)",
  "--header-bg": "#1e293b",
};

function applyTheme(dark: boolean) {
  const vars = dark ? DARK_VARS : LIGHT_VARS;
  const root = document.documentElement;
  Object.entries(vars).forEach(([k, v]) => root.style.setProperty(k, v));
}

// ────────────────────────────────────────────────────────────────────────────
// Component
// ────────────────────────────────────────────────────────────────────────────

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [currentRole, setCurrentRole] = useState<RoleKey>("");
  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);
  // Track which sections are expanded: set of section ids
  const [expandedSections, setExpandedSections] = useState<Set<string>>(() => {
    const defaults = new Set<string>();
    MENU_STRUCTURE.forEach((cat) =>
      cat.sections.forEach((sec) => {
        if (sec.defaultOpen) defaults.add(sec.id);
      }),
    );
    return defaults;
  });
  // Track which categories are expanded
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    () => new Set(["dashboard"]),
  );

  const { user, token, logout, restoreSession } = useAuthStore();

  useEffect(() => {
    restoreSession();
  }, [restoreSession]);

  // Auth guard: redirect unauthenticated users to /login.
  // Bypassed only when NEXT_PUBLIC_AUTH_BYPASS=true (local dev demo). The guard
  // is enforced by default so production / staging stay secure (fail closed).
  useEffect(() => {
    if (isAuthBypassEnabled()) return;
    if (token === null && typeof window !== "undefined") {
      const stored = localStorage.getItem("auth_token");
      if (!stored) {
        router.replace("/login");
      }
    }
  }, [token, router]);

  // Auto-expand the category + section containing the current route
  useEffect(() => {
    MENU_STRUCTURE.forEach((cat) => {
      cat.sections.forEach((sec) => {
        if (
          sec.pages.some(
            (p) => pathname === p.href || pathname.startsWith(p.href + "/"),
          )
        ) {
          setExpandedCategories((prev) => new Set(prev).add(cat.id));
          setExpandedSections((prev) => new Set(prev).add(sec.id));
        }
      });
    });
  }, [pathname]);

  const toggleDarkMode = useCallback(() => {
    setDarkMode((prev) => {
      applyTheme(!prev);
      return !prev;
    });
  }, []);

  const toggleCategory = useCallback((id: string) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  const toggleSection = useCallback((id: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  // Filter sections based on current role
  const isSectionVisible = (sec: NavSection) => {
    if (!currentRole) return true;
    if (!sec.roles || sec.roles.length === 0) return true;
    return sec.roles.includes(currentRole);
  };

  const displayName = user?.name ?? user?.email ?? "田中 健一";
  const initials = displayName
    .split(/[\s　]/)
    .map((s: string) => s[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <div
      className="flex h-screen overflow-hidden"
      style={{ background: "var(--bg-page, #f8fafc)" }}
    >
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* ── Sidebar ── */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col transform transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
        style={{
          background: "var(--sidebar-bg, #0f172a)",
          borderRight:
            "1px solid var(--sidebar-border, rgba(148,163,184,0.12))",
        }}
      >
        {/* Sidebar header */}
        <div
          className="flex h-16 items-center gap-2 px-4 flex-shrink-0"
          style={{
            borderBottom:
              "1px solid var(--sidebar-border, rgba(148,163,184,0.12))",
          }}
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600">
            <span className="text-white text-xs font-bold">CE</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white text-sm font-bold truncate">
              Construction-OS
            </p>
            <p className="text-slate-400 text-xs truncate">
              Enterprise Platform
            </p>
          </div>
          <button
            className="lg:hidden text-slate-400 hover:text-white"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation — 3-level accordion */}
        <nav className="flex-1 overflow-y-auto py-3">
          {MENU_STRUCTURE.map((cat) => {
            const CategoryIcon = cat.icon;
            const isCatOpen = expandedCategories.has(cat.id);
            // Check if any section in this category is visible for current role
            const hasVisibleSections = cat.sections.some(isSectionVisible);
            if (!hasVisibleSections) return null;

            return (
              <div key={cat.id} className="mb-1">
                {/* Category row */}
                <button
                  className="w-full flex items-center gap-2.5 px-3 py-2 text-left group"
                  onClick={() => toggleCategory(cat.id)}
                >
                  <CategoryIcon className="h-4 w-4 text-slate-400 group-hover:text-slate-200 flex-shrink-0" />
                  <span className="flex-1 text-xs font-semibold uppercase tracking-wider text-slate-400 group-hover:text-slate-200">
                    {cat.label}
                  </span>
                  <ChevronRight
                    className={`h-3 w-3 text-slate-500 transition-transform ${
                      isCatOpen ? "rotate-90" : ""
                    }`}
                  />
                </button>

                {/* Sections */}
                {isCatOpen && (
                  <div className="ml-2">
                    {cat.sections.map((sec) => {
                      if (!isSectionVisible(sec)) return null;
                      const isSecOpen = expandedSections.has(sec.id);

                      return (
                        <div key={sec.id}>
                          {/* Section header */}
                          <button
                            className="w-full flex items-center gap-2 px-3 py-1.5 text-left group"
                            onClick={() => toggleSection(sec.id)}
                          >
                            <span className="flex-1 text-xs text-slate-500 group-hover:text-slate-300">
                              {sec.label}
                            </span>
                            <ChevronDown
                              className={`h-3 w-3 text-slate-600 transition-transform ${
                                isSecOpen ? "" : "-rotate-90"
                              }`}
                            />
                          </button>

                          {/* Pages */}
                          {isSecOpen && (
                            <ul className="ml-2 mb-1">
                              {sec.pages.map((page) => {
                                const isActive =
                                  pathname === page.href ||
                                  (page.href !== "/" &&
                                    page.href !== "/dashboard" &&
                                    pathname.startsWith(page.href + "/"));
                                return (
                                  <li key={page.href}>
                                    <Link
                                      href={page.href}
                                      className={`flex items-center gap-2 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                                        isActive
                                          ? "bg-blue-600/20 text-blue-400"
                                          : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
                                      }`}
                                      onClick={() => setSidebarOpen(false)}
                                    >
                                      <span className="flex-1">
                                        {page.label}
                                      </span>
                                      {page.badge && (
                                        <span className="inline-flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white">
                                          {page.badge}
                                        </span>
                                      )}
                                    </Link>
                                  </li>
                                );
                              })}
                            </ul>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </nav>

        {/* Sidebar footer — user info */}
        <div
          className="flex-shrink-0 p-3"
          style={{
            borderTop:
              "1px solid var(--sidebar-border, rgba(148,163,184,0.12))",
          }}
        >
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600/20 text-blue-400 text-xs font-bold flex-shrink-0">
              {initials}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-slate-200 truncate">
                {displayName}
              </p>
              <p className="text-xs text-slate-500">
                {user?.role ?? "現場監督"}
              </p>
            </div>
          </div>
        </div>
      </aside>

      {/* ── Main content ── */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top header */}
        <header
          className="flex h-14 items-center gap-3 px-4 lg:px-5 flex-shrink-0"
          style={{
            background: "var(--header-bg, #ffffff)",
            borderBottom: "1px solid var(--border, #e2e8f0)",
          }}
        >
          {/* Mobile hamburger */}
          <button
            className="lg:hidden text-slate-500 hover:text-slate-700"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </button>

          <div className="flex-1" />

          {/* Role selector */}
          <div className="relative">
            <button
              className="flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs font-medium transition-colors hover:bg-gray-50"
              style={{
                borderColor: "var(--border, #e2e8f0)",
                color: "var(--text, #0f172a)",
              }}
              onClick={() => setRoleDropdownOpen((v) => !v)}
            >
              <UserCircle className="h-3.5 w-3.5" />
              <span>{ROLES[currentRole].label}</span>
              <ChevronDown className="h-3 w-3 opacity-60" />
            </button>

            {roleDropdownOpen && (
              <div
                className="absolute right-0 top-full mt-1 z-50 w-44 rounded-xl shadow-lg overflow-hidden"
                style={{
                  background: "var(--bg-card, #ffffff)",
                  border: "1px solid var(--border, #e2e8f0)",
                }}
              >
                {Object.entries(ROLES).map(([key, { label, color }]) => (
                  <button
                    key={key}
                    className="w-full flex items-center gap-2 px-3 py-2 text-xs text-left transition-colors hover:bg-gray-50"
                    style={{ color: "var(--text, #0f172a)" }}
                    onClick={() => {
                      setCurrentRole(key as RoleKey);
                      setRoleDropdownOpen(false);
                    }}
                  >
                    <span
                      className="h-2 w-2 rounded-full flex-shrink-0"
                      style={{ background: color }}
                    />
                    {label}
                    {currentRole === key && (
                      <span className="ml-auto text-blue-500">✓</span>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Dark mode toggle */}
          <button
            className="flex h-8 w-8 items-center justify-center rounded-lg transition-colors hover:bg-gray-100"
            style={{ color: "var(--text-muted, #64748b)" }}
            onClick={toggleDarkMode}
            title={darkMode ? "ライトモード" : "ダークモード"}
          >
            {darkMode ? (
              <Sun className="h-4 w-4" />
            ) : (
              <Moon className="h-4 w-4" />
            )}
          </button>

          {/* Notifications */}
          <button
            className="relative flex h-8 w-8 items-center justify-center rounded-lg transition-colors hover:bg-gray-100"
            style={{ color: "var(--text-muted, #64748b)" }}
          >
            <Bell className="h-4 w-4" />
            <span className="absolute top-1 right-1 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-red-500 text-[9px] font-bold text-white">
              3
            </span>
          </button>

          {/* User avatar + name */}
          <div className="flex items-center gap-2">
            <div
              className="flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold"
              style={{
                background: "var(--accent-light, #eff6ff)",
                color: "var(--accent, #1a56db)",
              }}
            >
              {initials}
            </div>
            <span
              className="hidden sm:inline text-sm font-medium"
              style={{ color: "var(--text, #0f172a)" }}
            >
              {displayName}
            </span>
          </div>

          {/* Logout */}
          <button
            className="flex h-8 w-8 items-center justify-center rounded-lg transition-colors hover:bg-gray-100"
            style={{ color: "var(--text-muted, #64748b)" }}
            onClick={handleLogout}
            title="ログアウト"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </header>

        {/* Page content */}
        <main
          className="flex-1 overflow-y-auto"
          style={{ background: "var(--bg-page, #f8fafc)" }}
        >
          {children}
        </main>
      </div>

      {/* Close role dropdown on outside click */}
      {roleDropdownOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setRoleDropdownOpen(false)}
        />
      )}
    </div>
  );
}
