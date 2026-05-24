"use client";

import { useState } from "react";
import {
  Building2,
  Users,
  Star,
  Phone,
  Search,
  Filter,
  Plus,
} from "lucide-react";

interface Company {
  id: string;
  name: string;
  industry: string;
  registrationNo: string;
  rating: number;
  contractStatus: "active" | "suspended" | "pending";
  contactPerson: string;
  phone: string;
}

const MOCK_COMPANIES: Company[] = [
  {
    id: "C-001",
    name: "山田建設株式会社",
    industry: "土木",
    registrationNo: "国土交通省-12345",
    rating: 4.5,
    contractStatus: "active",
    contactPerson: "山田太郎",
    phone: "03-1234-5678",
  },
  {
    id: "C-002",
    name: "鈴木電気工業",
    industry: "電気",
    registrationNo: "国土交通省-23456",
    rating: 4.2,
    contractStatus: "active",
    contactPerson: "鈴木一郎",
    phone: "03-2345-6789",
  },
  {
    id: "C-003",
    name: "田中設備工業",
    industry: "設備",
    registrationNo: "国土交通省-34567",
    rating: 3.8,
    contractStatus: "active",
    contactPerson: "田中次郎",
    phone: "03-3456-7890",
  },
  {
    id: "C-004",
    name: "佐藤建築工業",
    industry: "建築",
    registrationNo: "国土交通省-45678",
    rating: 4.7,
    contractStatus: "active",
    contactPerson: "佐藤三郎",
    phone: "03-4567-8901",
  },
  {
    id: "C-005",
    name: "高橋解体工業",
    industry: "解体",
    registrationNo: "国土交通省-56789",
    rating: 3.5,
    contractStatus: "suspended",
    contactPerson: "高橋四郎",
    phone: "03-5678-9012",
  },
  {
    id: "C-006",
    name: "伊藤土木建設",
    industry: "土木",
    registrationNo: "国土交通省-67890",
    rating: 4.1,
    contractStatus: "active",
    contactPerson: "伊藤五郎",
    phone: "03-6789-0123",
  },
  {
    id: "C-007",
    name: "渡辺建設工業",
    industry: "建築",
    registrationNo: "国土交通省-78901",
    rating: 3.9,
    contractStatus: "pending",
    contactPerson: "渡辺六郎",
    phone: "03-7890-1234",
  },
  {
    id: "C-008",
    name: "中村電設工業",
    industry: "電気",
    registrationNo: "国土交通省-89012",
    rating: 4.3,
    contractStatus: "active",
    contactPerson: "中村七郎",
    phone: "03-8901-2345",
  },
  {
    id: "C-009",
    name: "小林管工事",
    industry: "設備",
    registrationNo: "国土交通省-90123",
    rating: 4.0,
    contractStatus: "active",
    contactPerson: "小林八郎",
    phone: "03-9012-3456",
  },
  {
    id: "C-010",
    name: "加藤総合工業",
    industry: "その他",
    registrationNo: "国土交通省-01234",
    rating: 3.6,
    contractStatus: "pending",
    contactPerson: "加藤九郎",
    phone: "03-0123-4567",
  },
];

const STATUS_LABELS: Record<Company["contractStatus"], string> = {
  active: "契約中",
  suspended: "停止中",
  pending: "審査中",
};

const STATUS_COLORS: Record<Company["contractStatus"], string> = {
  active: "bg-green-100 text-green-800",
  suspended: "bg-red-100 text-red-800",
  pending: "bg-yellow-100 text-yellow-800",
};

const INDUSTRIES = ["すべて", "土木", "建築", "設備", "電気", "解体", "その他"];

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <Star
          key={star}
          className={`w-4 h-4 ${
            star <= Math.round(rating)
              ? "text-yellow-400 fill-yellow-400"
              : "text-gray-300"
          }`}
        />
      ))}
      <span className="text-sm text-gray-600 ml-1">{rating.toFixed(1)}</span>
    </div>
  );
}

export default function PartnerCompaniesPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedIndustry, setSelectedIndustry] = useState("すべて");

  const filtered = MOCK_COMPANIES.filter((c) => {
    const matchSearch =
      c.name.includes(searchQuery) ||
      c.contactPerson.includes(searchQuery) ||
      c.registrationNo.includes(searchQuery);
    const matchIndustry =
      selectedIndustry === "すべて" || c.industry === selectedIndustry;
    return matchSearch && matchIndustry;
  });

  const stats = {
    total: MOCK_COMPANIES.length,
    active: MOCK_COMPANIES.filter((c) => c.contractStatus === "active").length,
    pending: MOCK_COMPANIES.filter((c) => c.contractStatus === "pending")
      .length,
    newThisMonth: 2,
  };

  return (
    <div className="p-6 space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">協力会社一覧</h1>
          <p className="text-sm text-gray-500 mt-1">
            登録済み協力会社の管理・評価
          </p>
        </div>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
          <Plus className="w-4 h-4" />
          新規登録
        </button>
      </div>

      {/* 統計カード */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-50 rounded-lg">
              <Building2 className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">登録会社数</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-50 rounded-lg">
              <Users className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">契約中</p>
              <p className="text-2xl font-bold text-gray-900">{stats.active}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-50 rounded-lg">
              <Star className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">評価待ち</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.pending}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-50 rounded-lg">
              <Phone className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">今月新規</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.newThisMonth}
              </p>
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
              placeholder="会社名・担当者名・登録番号で検索..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={selectedIndustry}
              onChange={(e) => setSelectedIndustry(e.target.value)}
              className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {INDUSTRIES.map((ind) => (
                <option key={ind} value={ind}>
                  {ind}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* テーブル */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  会社名
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  業種
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  登録番号
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  評価スコア
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  契約状況
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  担当者
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  電話番号
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((company) => (
                <tr
                  key={company.id}
                  className="hover:bg-gray-50 transition-colors cursor-pointer"
                >
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <Building2 className="w-4 h-4 text-gray-400" />
                      <span className="font-medium text-gray-900">
                        {company.name}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="bg-gray-100 text-gray-700 px-2 py-0.5 rounded text-xs">
                      {company.industry}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-600 font-mono text-xs">
                    {company.registrationNo}
                  </td>
                  <td className="px-4 py-3">
                    <StarRating rating={company.rating} />
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[company.contractStatus]}`}
                    >
                      {STATUS_LABELS[company.contractStatus]}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-700">
                    {company.contactPerson}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1 text-gray-600">
                      <Phone className="w-3 h-3" />
                      {company.phone}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-4 py-3 border-t border-gray-100 text-sm text-gray-500">
          {filtered.length}件表示 / 全{MOCK_COMPANIES.length}件
        </div>
      </div>
    </div>
  );
}
