"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Camera,
  Image,
  Tag,
  Upload,
  RefreshCw,
  AlertCircle,
} from "lucide-react";

interface SitePhoto {
  id: string;
  filename: string;
  taken_at: string;
  zone: string;
  tags: string[];
  uploader: string;
  needs_review: boolean;
  description: string;
}

const MOCK_PHOTOS: SitePhoto[] = [
  {
    id: "p01",
    filename: "IMG_0101.jpg",
    taken_at: "2026-05-24",
    zone: "B工区",
    tags: ["進捗"],
    uploader: "鈴木 健太",
    needs_review: false,
    description: "3Fスラブ コンクリート打設完了",
  },
  {
    id: "p02",
    filename: "IMG_0102.jpg",
    taken_at: "2026-05-24",
    zone: "D工区",
    tags: ["問題"],
    uploader: "山田 浩二",
    needs_review: true,
    description: "排水管埋設 — 地盤沈下懸念箇所",
  },
  {
    id: "p03",
    filename: "IMG_0103.jpg",
    taken_at: "2026-05-24",
    zone: "C工区",
    tags: ["進捗"],
    uploader: "佐藤 誠",
    needs_review: false,
    description: "内装ボード張り作業状況",
  },
  {
    id: "p04",
    filename: "IMG_0104.jpg",
    taken_at: "2026-05-24",
    zone: "全工区",
    tags: ["安全"],
    uploader: "田中 一郎",
    needs_review: false,
    description: "朝礼 安全確認の様子",
  },
  {
    id: "p05",
    filename: "IMG_0105.jpg",
    taken_at: "2026-05-23",
    zone: "B工区",
    tags: ["進捗"],
    uploader: "渡辺 大輔",
    needs_review: false,
    description: "型枠設置状況（3F）",
  },
  {
    id: "p06",
    filename: "IMG_0106.jpg",
    taken_at: "2026-05-23",
    zone: "A工区",
    tags: ["完了"],
    uploader: "伊藤 隆",
    needs_review: false,
    description: "A工区 基礎工事完成写真",
  },
  {
    id: "p07",
    filename: "IMG_0107.jpg",
    taken_at: "2026-05-23",
    zone: "D工区",
    tags: ["問題"],
    uploader: "中村 修",
    needs_review: true,
    description: "配管接続部 — 要確認箇所マーキング済み",
  },
  {
    id: "p08",
    filename: "IMG_0108.jpg",
    taken_at: "2026-05-23",
    zone: "C工区",
    tags: ["安全"],
    uploader: "佐藤 誠",
    needs_review: false,
    description: "足場手すり点検結果（C工区）",
  },
  {
    id: "p09",
    filename: "IMG_0109.jpg",
    taken_at: "2026-05-22",
    zone: "B工区",
    tags: ["進捗"],
    uploader: "鈴木 健太",
    needs_review: false,
    description: "鉄筋配筋検査立会い（2F）",
  },
  {
    id: "p10",
    filename: "IMG_0110.jpg",
    taken_at: "2026-05-22",
    zone: "A工区",
    tags: ["完了"],
    uploader: "田中 一郎",
    needs_review: false,
    description: "A工区 完成検査 立会い写真",
  },
  {
    id: "p11",
    filename: "IMG_0111.jpg",
    taken_at: "2026-05-22",
    zone: "D工区",
    tags: ["進捗"],
    uploader: "山田 浩二",
    needs_review: false,
    description: "外構 境界杭確認作業",
  },
  {
    id: "p12",
    filename: "IMG_0112.jpg",
    taken_at: "2026-05-21",
    zone: "C工区",
    tags: ["進捗"],
    uploader: "伊藤 隆",
    needs_review: false,
    description: "防水下地処理 完了状況",
  },
];

const TAG_COLORS: Record<string, string> = {
  安全: "bg-green-100 text-green-700",
  進捗: "bg-blue-100 text-blue-700",
  完了: "bg-purple-100 text-purple-700",
  問題: "bg-red-100 text-red-700",
};

const ALL_ZONES = ["全工区", "A工区", "B工区", "C工区", "D工区"];
const ALL_TAGS = ["安全", "進捗", "完了", "問題"];

function PhotoCard({ photo }: { photo: SitePhoto }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white overflow-hidden hover:shadow-md transition-shadow">
      {/* Placeholder image area */}
      <div className="relative aspect-video bg-gray-200 flex items-center justify-center">
        <Image className="h-10 w-10 text-gray-400" />
        {photo.needs_review && (
          <span className="absolute top-2 right-2 inline-flex items-center gap-1 rounded-full bg-red-500 px-2 py-0.5 text-xs font-semibold text-white shadow">
            <AlertCircle className="h-3 w-3" />
            要確認
          </span>
        )}
        <span className="absolute bottom-2 left-2 rounded bg-black/50 px-2 py-0.5 text-xs text-white">
          {photo.zone}
        </span>
      </div>

      {/* Card body */}
      <div className="p-3 space-y-2">
        <p className="text-xs font-medium text-gray-800 line-clamp-2 leading-snug">
          {photo.description}
        </p>
        <div className="flex flex-wrap gap-1">
          {photo.tags.map((tag) => (
            <span
              key={tag}
              className={`inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-xs font-medium ${TAG_COLORS[tag] ?? "bg-gray-100 text-gray-600"}`}
            >
              <Tag className="h-2.5 w-2.5" />
              {tag}
            </span>
          ))}
        </div>
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>{photo.taken_at}</span>
          <span>{photo.uploader}</span>
        </div>
      </div>
    </div>
  );
}

export default function FieldPhotosPage() {
  const [photos, setPhotos] = useState<SitePhoto[]>(MOCK_PHOTOS);
  const [filterZone, setFilterZone] = useState<string>("all");
  const [filterTag, setFilterTag] = useState<string>("all");
  const [loading, setLoading] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    const res = await fetch("/api/v1/field/photos").catch(() => null);
    if (res?.ok) {
      const json = await res.json().catch(() => null);
      if (Array.isArray(json?.data)) setPhotos(json.data as SitePhoto[]);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const filtered = photos.filter((p) => {
    const zoneOk = filterZone === "all" || p.zone === filterZone;
    const tagOk = filterTag === "all" || p.tags.includes(filterTag);
    return zoneOk && tagOk;
  });

  const thisWeek = photos.filter((p) => p.taken_at >= "2026-05-18").length;
  const total = photos.length;
  const needsReview = photos.filter((p) => p.needs_review).length;

  const statCards = [
    {
      label: "今週アップロード",
      value: thisWeek,
      sub: "5/18〜5/24",
      icon: Upload,
      color: "text-blue-500 bg-blue-50",
    },
    {
      label: "総写真数",
      value: total,
      sub: "全期間",
      icon: Camera,
      color: "text-purple-500 bg-purple-50",
    },
    {
      label: "要確認",
      value: needsReview,
      sub: "レビュー待ち",
      icon: AlertCircle,
      color:
        needsReview > 0
          ? "text-red-500 bg-red-50"
          : "text-green-500 bg-green-50",
    },
  ];

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">現場写真管理</h1>
          <p className="mt-1 text-sm text-gray-500">
            工区別の現場写真をアップロード・閲覧・管理します
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={loadData}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            更新
          </button>
          <button className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 transition-colors">
            <Upload className="h-4 w-4" />
            写真をアップロード
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {statCards.map((card) => {
          const Icon = card.icon;
          const [iconColor, bgColor] = card.color.split(" ");
          return (
            <div
              key={card.label}
              className="rounded-xl border border-gray-200 bg-white p-5 hover:shadow-md transition-shadow"
            >
              <div className={`inline-flex rounded-lg p-2.5 ${bgColor}`}>
                <Icon className={`h-5 w-5 ${iconColor}`} />
              </div>
              <p className="mt-4 text-3xl font-bold text-gray-900">
                {card.value}
              </p>
              <p className="mt-1 text-sm font-medium text-gray-600">
                {card.label}
              </p>
              <p className="mt-2 text-xs text-gray-400">{card.sub}</p>
            </div>
          );
        })}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 items-center">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-medium text-gray-500">工区:</span>
          <button
            onClick={() => setFilterZone("all")}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${filterZone === "all" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}
          >
            すべて
          </button>
          {ALL_ZONES.map((z) => (
            <button
              key={z}
              onClick={() => setFilterZone(z)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${filterZone === z ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}
            >
              {z}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-medium text-gray-500 flex items-center gap-1">
            <Tag className="h-3 w-3" />
            タグ:
          </span>
          <button
            onClick={() => setFilterTag("all")}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${filterTag === "all" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}
          >
            すべて
          </button>
          {ALL_TAGS.map((t) => (
            <button
              key={t}
              onClick={() => setFilterTag(t)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${filterTag === t ? "bg-blue-600 text-white" : `${TAG_COLORS[t] ?? "bg-gray-100 text-gray-600"} hover:opacity-80`}`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Photo Grid */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-bold text-gray-900 flex items-center gap-2">
            <Camera className="h-4 w-4 text-purple-500" />
            写真一覧
          </h2>
          <span className="text-xs text-gray-500">
            {filtered.length} 件表示
          </span>
        </div>
        {filtered.length === 0 ? (
          <div className="rounded-xl border border-gray-200 bg-white py-16 text-center text-sm text-gray-400">
            該当する写真はありません
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {filtered.map((photo) => (
              <PhotoCard key={photo.id} photo={photo} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
