"use client";

import React, { useState, useCallback, useMemo } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "../../lib/utils";
import type { MenuCategory, RoleId } from "@construction-enterprise-os/core/menu-structure";
import { MENU_STRUCTURE, ROLES, ROLE_DEFAULT_OPEN } from "@construction-enterprise-os/core/menu-structure";

// ============================================
// 型定義
// ============================================
interface SidebarProps {
  userRoles: RoleId[];
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

// ============================================
// アイコン (シンプルなSVG代替)
// ============================================
const IconPlaceholder: React.FC<{ className?: string }> = ({ className }) => (
  <span className={cn("w-4 h-4 flex-shrink-0", className)} />
);

// ============================================
// 小項目 (第3階層: ページリンク)
// ============================================
const MenuItem: React.FC<{
  label: string;
  href: string;
  badge?: string;
  isActive: boolean;
  collapsed: boolean;
}> = ({ label, href, badge, isActive, collapsed }) => {
  if (collapsed) {
    return (
      <Link
        href={href}
        className={cn(
          "flex items-center justify-center w-10 h-10 rounded-lg mx-auto mb-1",
          "transition-colors duration-150",
          isActive
            ? "bg-primary text-white"
            : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
        )}
        title={label}
      >
        <span className="text-xs font-medium">{label.slice(0, 2)}</span>
      </Link>
    );
  }

  return (
    <Link
      href={href}
      className={cn(
        "flex items-center gap-2 px-3 py-1.5 ml-8 rounded-md text-sm",
        "transition-colors duration-150",
        isActive
          ? "bg-primary/10 text-primary font-medium"
          : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
      )}
    >
      <span className="w-1 h-1 rounded-full bg-current flex-shrink-0" />
      <span className="truncate">{label}</span>
      {badge && (
        <span className="ml-auto bg-red-500 text-white text-xs px-1.5 py-0.5 rounded-full">
          {badge}
        </span>
      )}
    </Link>
  );
};

// ============================================
// 中項目 (第2階層: セクションアコーディオン)
// ============================================
const SectionAccordion: React.FC<{
  section: MenuCategory["sections"][0];
  pathname: string;
  userRoles: RoleId[];
  collapsed: boolean;
}> = ({ section, pathname, userRoles, collapsed }) => {
  const hasActiveChild = section.pages.some((p) => pathname.startsWith(p.href));
  const [isOpen, setIsOpen] = useState(section.defaultOpen || hasActiveChild);

  if (collapsed) {
    return (
      <div className="mb-1">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            "flex items-center justify-center w-10 h-10 rounded-lg mx-auto",
            "transition-colors duration-150",
            hasActiveChild
              ? "bg-primary/10 text-primary"
              : "text-gray-500 hover:bg-gray-100 hover:text-gray-700"
          )}
          title={section.label}
        >
          <span className="text-xs font-bold">{section.label.slice(0, 2)}</span>
        </button>
      </div>
    );
  }

  return (
    <div className="mb-0.5">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center gap-2 w-full px-3 py-2 rounded-md text-sm font-medium",
          "transition-colors duration-150",
          hasActiveChild
            ? "text-primary bg-primary/5"
            : "text-gray-700 hover:bg-gray-100"
        )}
      >
        <svg
          className={cn(
            "w-3 h-3 flex-shrink-0 transition-transform duration-200",
            isOpen && "rotate-90"
          )}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
        </svg>
        <span className="truncate">{section.label}</span>
      </button>
      {isOpen && (
        <div className="mt-0.5 space-y-0.5">
          {section.pages.map((page) => (
            <MenuItem
              key={page.id}
              label={page.label}
              href={page.href}
              badge={page.badge}
              isActive={pathname === page.href || pathname.startsWith(page.href + "/")}
              collapsed={collapsed}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// ============================================
// 大項目 (第1階層: カテゴリアコーディオン)
// ============================================
const CategoryAccordion: React.FC<{
  category: MenuCategory;
  pathname: string;
  userRoles: RoleId[];
  defaultOpen: boolean;
  collapsed: boolean;
}> = ({ category, pathname, userRoles, defaultOpen, collapsed }) => {
  const hasActiveChild = category.sections.some((s) =>
    s.pages.some((p) => pathname.startsWith(p.href))
  );
  const [isOpen, setIsOpen] = useState(defaultOpen || hasActiveChild);

  // このカテゴリに表示可能なセクションがあるか
  const visibleSections = category.sections.filter((section) => {
    if (userRoles.includes("admin")) return true;
    const sectionRoles = section.roles;
    if (!sectionRoles) return true;
    return sectionRoles.some((r) => userRoles.includes(r as RoleId));
  });

  if (visibleSections.length === 0) return null;

  if (collapsed) {
    return (
      <div className="mb-2">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            "flex items-center justify-center w-12 h-12 rounded-xl mx-auto",
            "transition-all duration-150",
            hasActiveChild
              ? "bg-primary text-white shadow-md"
              : "text-gray-500 hover:bg-gray-100 hover:text-gray-700"
          )}
          title={category.label}
        >
          <span className="text-lg">{category.label.slice(0, 2)}</span>
        </button>
        {isOpen && (
          <div className="mt-1">
            {visibleSections.map((section) => (
              <SectionAccordion
                key={section.id}
                section={section}
                pathname={pathname}
                userRoles={userRoles}
                collapsed={collapsed}
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="mb-1">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center gap-2 w-full px-3 py-2.5 rounded-lg",
          "text-sm font-semibold transition-all duration-150",
          hasActiveChild
            ? "bg-primary/10 text-primary"
            : "text-gray-800 hover:bg-gray-100"
        )}
      >
        <svg
          className={cn(
            "w-4 h-4 flex-shrink-0 transition-transform duration-200",
            isOpen && "rotate-90"
          )}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2.5}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
        </svg>
        <span className="truncate">{category.label}</span>
        {hasActiveChild && (
          <span className="ml-auto w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />
        )}
      </button>
      {isOpen && (
        <div className="mt-1 ml-1">
          {visibleSections.map((section) => (
            <SectionAccordion
              key={section.id}
              section={section}
              pathname={pathname}
              userRoles={userRoles}
              collapsed={collapsed}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// ============================================
// 役割セレクター (開発用)
// ============================================
const RoleSelector: React.FC<{
  userRoles: RoleId[];
  onChangeRoles: (roles: RoleId[]) => void;
}> = ({ userRoles, onChangeRoles }) => {
  const [open, setOpen] = useState(false);

  const toggleRole = (roleId: RoleId) => {
    if (userRoles.includes(roleId)) {
      onChangeRoles(userRoles.filter((r) => r !== roleId));
    } else {
      onChangeRoles([...userRoles, roleId]);
    }
  };

  return (
    <div className="relative px-3 py-2">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 w-full px-2 py-1.5 rounded-md text-xs text-gray-500 hover:bg-gray-100"
      >
        <span>👤 役割切替</span>
        <span className="ml-auto text-gray-400">
          {userRoles.length > 0 ? userRoles.length : "ALL"}
        </span>
      </button>
      {open && (
        <div className="absolute bottom-full left-3 mb-1 bg-white rounded-lg shadow-lg border p-2 w-48 z-50">
          <div className="text-xs text-gray-400 mb-1 px-1">役割を選択</div>
          {Object.entries(ROLES).map(([id, role]) => (
            <label
              key={id}
              className="flex items-center gap-2 px-2 py-1 rounded hover:bg-gray-50 cursor-pointer text-xs"
            >
              <input
                type="checkbox"
                checked={userRoles.includes(id as RoleId)}
                onChange={() => toggleRole(id as RoleId)}
                className="w-3 h-3"
              />
              <span
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ backgroundColor: role.color }}
              />
              <span>{role.label}</span>
            </label>
          ))}
          <button
            onClick={() => onChangeRoles([])}
            className="w-full mt-1 text-xs text-primary hover:underline"
          >
            全表示に戻す
          </button>
        </div>
      )}
    </div>
  );
};

// ============================================
// メイン サイドバーコンポーネント
// ============================================
export const Sidebar: React.FC<SidebarProps> = ({
  userRoles: initialRoles = [],
  collapsed = false,
  onToggleCollapse,
}) => {
  const pathname = usePathname() || "/";
  const [userRoles, setUserRoles] = useState<RoleId[]>(initialRoles);

  // 役割に基づいてフィルタリングされたメニュー
  const filteredMenu = useMemo(() => {
    if (userRoles.length === 0 || userRoles.includes("admin")) {
      return MENU_STRUCTURE;
    }
    return MENU_STRUCTURE.filter((category) => {
      return category.sections.some((section) => {
        const sectionRoles = section.roles;
        if (!sectionRoles) {
          // セクションに役割制限なし → ページの役割をチェック
          return section.pages.some((page) => {
            if (!page.roles) return true;
            return page.roles.some((r) => userRoles.includes(r as RoleId));
          });
        }
        return sectionRoles.some((r) => userRoles.includes(r as RoleId));
      });
    });
  }, [userRoles]);

  // 役割に基づくデフォルト展開カテゴリ
  const defaultOpenCategories = useMemo(() => {
    if (userRoles.length === 0) return [];
    const categories = new Set<string>();
    userRoles.forEach((role) => {
      ROLE_DEFAULT_OPEN[role]?.forEach((cat) => categories.add(cat));
    });
    return [...categories];
  }, [userRoles]);

  return (
    <aside
      className={cn(
        "flex flex-col h-full bg-white border-r border-gray-200 transition-all duration-300 overflow-hidden",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* ヘッダー */}
      <div className={cn(
        "flex items-center border-b border-gray-100",
        collapsed ? "justify-center px-2 py-3" : "justify-between px-4 py-3"
      )}>
        {!collapsed && (
          <div className="flex items-center gap-2">
            <span className="text-lg">🏗️</span>
            <span className="font-bold text-sm text-gray-900 truncate">
              Construction-Enterprise-OS
            </span>
          </div>
        )}
        {collapsed && <span className="text-lg">🏗️</span>}
        <button
          onClick={onToggleCollapse}
          className={cn(
            "p-1 rounded-md hover:bg-gray-100 text-gray-400 transition-colors",
            collapsed && "mt-2"
          )}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            {collapsed ? (
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" d="M11 19l-7-7 7-7M19 19l-7-7 7-7" />
            )}
          </svg>
        </button>
      </div>

      {/* 役割セレクター (折りたたみ時は非表示) */}
      {!collapsed && (
        <RoleSelector userRoles={userRoles} onChangeRoles={setUserRoles} />
      )}

      {/* メニュー本体 (スクロール可能) */}
      <nav className="flex-1 overflow-y-auto py-2 px-1 scrollbar-thin">
        {filteredMenu.map((category) => (
          <CategoryAccordion
            key={category.id}
            category={category}
            pathname={pathname}
            userRoles={userRoles}
            defaultOpen={defaultOpenCategories.includes(category.id)}
            collapsed={collapsed}
          />
        ))}
      </nav>

      {/* フッター */}
      <div className={cn(
        "border-t border-gray-100 p-3",
        collapsed ? "text-center" : ""
      )}>
        <div className={cn(
          "flex items-center gap-2 text-xs text-gray-400",
          collapsed && "justify-center flex-col"
        )}>
          {!collapsed && (
            <>
              <span className="w-2 h-2 rounded-full bg-green-500 flex-shrink-0" />
              <span>451 tests PASS</span>
              <span className="ml-auto">v0.1.0</span>
            </>
          )}
          {collapsed && (
            <>
              <span className="w-2 h-2 rounded-full bg-green-500" />
              <span className="text-[10px]">v0.1</span>
            </>
          )}
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
