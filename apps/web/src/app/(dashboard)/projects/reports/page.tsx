"use client";

import { FileText, BarChart3, Send, Eye } from "lucide-react";

const REPORTS = [
  { id: 1, name: "2024年11月 月次工事報告書", type: "月次報告", project: "品川タワー新築工事", created: "2024-11-30", author: "田中 健一", status: "approved" },
  { id: 2, name: "2024年11月第4週 週次報告", type: "週次報告", project: "品川タワー新築工事", created: "2024-11-29", author: "田中 健一", status: "sent" },
  { id: 3, name: "2024年11月第3週 週次報告", type: "週次報告", project: "品川タワー新築工事", created: "2024-11-22", author: "田中 健一", status: "sent" },
  { id: 4, name: "横浜マンション 中間報告書", type: "中間報告", project: "横浜分譲マンション建設", created: "2024-11-15", author: "鈴木 次郎", status: "approved" },
  { id: 5, name: "大田区道路改良 完工報告書", type: "完工報告", project: "大田区道路改良工事", created: "2024-11-10", author: "佐藤 三郎", status: "approved" },
  { id: 6, name: "2024年10月 月次工事報告書", type: "月次報告", project: "品川タワー新築工事", created: "2024-10-31", author: "田中 健一", status: "sent" },
  { id: 7, name: "竣工写真集 Vol.1", type: "竣工写真集", project: "大田区道路改良工事", created: "2024-10-25", author: "中村 八郎", status: "draft" },
  { id: 8, name: "横浜マンション 週次報告 第12週", type: "週次報告", project: "横浜分譲マンション建設", created: "2024-10-18", author: "鈴木 次郎", status: "sent" },
  { id: 9, name: "川崎工場 中間報告書", type: "中間報告", project: "川崎工場改修工事", created: "2024-10-05", author: "木村 七海", status: "draft" },
  { id: 10, name: "2024年9月 月次工事報告書", type: "月次報告", project: "品川タワー新築工事", created: "2024-09-30", author: "田中 健一", status: "sent" },
];

const STATUS_STYLES: Record<string, string> = {
  approved: "bg-green-100 text-green-800",
  sent: "bg-blue-100 text-blue-800",
  draft: "bg-gray-100 text-gray-700",
};

const STATUS_LABELS: Record<string, string> = {
  approved: "承認済み",
  sent: "配信済み",
  draft: "下書き",
};

const TYPE_STYLES: Record<string, string> = {
  月次報告: "bg-purple-100 text-purple-800",
  週次報告: "bg-blue-100 text-blue-800",
  完工報告: "bg-green-100 text-green-800",
  中間報告: "bg-orange-100 text-orange-800",
  竣工写真集: "bg-pink-100 text-pink-800",
};

export default function ReportsPage() {
  const thisMonth = REPORTS.filter((r) => r.created.startsWith("2024-11")).length;
  const approved = REPORTS.filter((r) => r.status === "approved").length;
  const draft = REPORTS.filter((r) => r.status === "draft").length;
  const sent = REPORTS.filter((r) => r.status === "sent").length;

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">プロジェクトレポート</h1>
          <p className="text-sm text-gray-500 mt-1">工事報告書・週次月次レポートの管理</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
          レポート作成
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-blue-50 rounded-lg">
            <FileText className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">今月作成数</p>
            <p className="text-2xl font-bold text-gray-900">{thisMonth}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-green-50 rounded-lg">
            <BarChart3 className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">承認済み</p>
            <p className="text-2xl font-bold text-gray-900">{approved}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-gray-50 rounded-lg">
            <Eye className="w-5 h-5 text-gray-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">下書き</p>
            <p className="text-2xl font-bold text-gray-900">{draft}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-purple-50 rounded-lg">
            <Send className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">配信済み</p>
            <p className="text-2xl font-bold text-gray-900">{sent}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left font-semibold text-gray-600">レポート名</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">種別</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">対象プロジェクト</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">作成日</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">作成者</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">ステータス</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {REPORTS.map((report) => (
                <tr key={report.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-blue-700 hover:underline cursor-pointer">
                    {report.name}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${TYPE_STYLES[report.type] ?? "bg-gray-100 text-gray-700"}`}>
                      {report.type}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{report.project}</td>
                  <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{report.created}</td>
                  <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{report.author}</td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_STYLES[report.status]}`}>
                      {STATUS_LABELS[report.status]}
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
