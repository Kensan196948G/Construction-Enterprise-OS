/**
 * Construction-Enterprise-OS 共通型定義
 */

// ============================================
// 共通 ID 型
// ============================================
export type UUID = string;
export type ISO8601 = string;

// ============================================
// API 共通レスポンス
// ============================================
export interface APIResponse<T = unknown> {
  success: boolean;
  data: T | null;
  error: APIError | null;
  meta: MetaInfo | null;
}

export interface APIError {
  code: string;
  message: string;
  details?: Record<string, unknown>[];
}

export interface MetaInfo {
  page?: number;
  per_page?: number;
  total?: number;
  total_pages?: number;
}

// ============================================
// 認証
// ============================================
export interface TokenPayload {
  sub: string;
  type: "user" | "client";
  org?: string;
  roles: string[];
  scopes: string[];
  device_id?: string;
  iat: number;
  exp: number;
  iss: string;
  jti: string;
}

export interface UserInfo {
  id: UUID;
  organizationId: UUID;
  email: string;
  username: string | null;
  displayName: string;
  phone: string | null;
  locale: string;
  status: UserStatus;
  roles: RoleSummary[];
}

export type UserStatus = "pending" | "active" | "suspended" | "deactivated";

export interface RoleSummary {
  id: UUID;
  name: string;
}

// ============================================
// 組織
// ============================================
export type OrganizationType = "company" | "department" | "site" | "partner";
export type OrganizationStatus = "active" | "inactive";

// ============================================
// プロジェクト/工事
// ============================================
export interface Project {
  id: UUID;
  code: string;
  name: string;
  type: ProjectType;
  status: ProjectStatus;
  startDate: ISO8601;
  endDate: ISO8601;
  location?: GeoPoint;
}

export type ProjectType = "building" | "civil" | "infrastructure" | "marine" | "other";
export type ProjectStatus = "planning" | "preparation" | "in_progress" | "suspended" | "completed";

// ============================================
// GIS
// ============================================
export interface GeoPoint {
  latitude: number;
  longitude: number;
  altitude?: number;
}

export interface GeoPolygon {
  type: "Polygon";
  coordinates: number[][][];
}

// ============================================
// ワークフロー
// ============================================
export type WorkflowStatus =
  | "draft"
  | "pending_approval"
  | "approved"
  | "rejected"
  | "recalled";

export interface ApprovalNode {
  id: UUID;
  approverId: UUID;
  approverName: string;
  status: "pending" | "approved" | "rejected";
  comment?: string;
  approvedAt?: ISO8601;
}

// ============================================
// 文書
// ============================================
export interface DocumentMeta {
  id: UUID;
  name: string;
  type: DocumentType;
  status: DocumentStatus;
  projectId?: UUID;
  version: number;
  fileSize: number;
  mimeType: string;
  uploadedBy: UUID;
  uploadedAt: ISO8601;
}

export type DocumentType = "pdf" | "cad" | "bim" | "photo" | "video" | "spreadsheet" | "other";
export type DocumentStatus = "draft" | "under_review" | "approved" | "obsolete";

// ============================================
// 通知
// ============================================
export type NotificationPriority = "low" | "normal" | "high" | "urgent";
export type NotificationCategory = "workflow" | "safety" | "system" | "iot" | "document";

export interface Notification {
  id: UUID;
  title: string;
  body: string;
  priority: NotificationPriority;
  category: NotificationCategory;
  read: boolean;
  createdAt: ISO8601;
}
