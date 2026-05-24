"use client";

import { Building, Users, Network, TreePine } from "lucide-react";

const DEPARTMENTS = [
  { id: 1, code: "D001", name: "経営本部", manager: "渡辺 管理", members: 5, parent: null, work: "経営企画・全社統括", level: 0 },
  { id: 2, code: "D002", name: "建設事業部", manager: "田中 健一", members: 48, parent: "経営本部", work: "建設工事全般の施工管理", level: 1 },
  { id: 3, code: "D003", name: "第一工事部", manager: "鈴木 次郎", members: 20, parent: "建設事業部", work: "RC造・SRC造建築工事", level: 2 },
  { id: 4, code: "D004", name: "第二工事部", manager: "佐藤 三郎", members: 18, parent: "建設事業部", work: "土木・道路工事", level: 2 },
  { id: 5, code: "D005", name: "設備工事部", manager: "加藤 十蔵", members: 10, parent: "建設事業部", work: "電気・機械設備工事", level: 2 },
  { id: 6, code: "D006", name: "安全管理部", manager: "木村 七海", members: 6, parent: "建設事業部", work: "現場安全・法令遵守", level: 2 },
  { id: 7, code: "D007", name: "品質管理部", manager: "松本 花子", members: 4, parent: "建設事業部", work: "品質検査・ISO管理", level: 2 },
  { id: 8, code: "D008", name: "技術開発部", manager: "山田 五郎", members: 8, parent: "経営本部", work: "新技術導入・R&D", level: 1 },
  { id: 9, code: "D009", name: "管理部", manager: "伊藤 一郎", members: 6, parent: "経営本部", work: "総務・人事・経理", level: 1 },
  { id: 10, code: "D010", name: "DX推進室", manager: "中村 八郎", members: 4, parent: "技術開発部", work: "デジタル化・システム導入", level: 2 },
];

const INDENT_CLASSES: Record<number, string> = {
  0: "",
  1: "pl-6",
  2: "pl-12",
};

export default function OrgPage() {
  const totalDept = DEPARTMENTS.length;
  const totalMembers = DEPARTMENTS.filter((d) => d.level === 0 || d.level === 1).reduce((s, d) => s + (d.level === 1 ? d.members : 0), 0) + DEPARTMENTS.find((d) => d.level === 0)!.members;
  const executives = DEPARTMENTS.filter((d) => d.level === 0).reduce((s, d) => s + d.members, 0);
  const offices = DEPARTMENTS.filter((d) => d.code.startsWith("D00")).length;

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">組織管理</h1>
          <p className="text-sm text-gray-500 mt-1">部署・チームの組織ツリー管理</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
          部署追加
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-blue-50 rounded-lg">
            <Building className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">総部署数</p>
            <p className="text-2xl font-bold text-gray-900">{totalDept}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-green-50 rounded-lg">
            <Users className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">総人員数</p>
            <p className="text-2xl font-bold text-gray-900">{totalMembers}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-purple-50 rounded-lg">
            <Network className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">役員数</p>
            <p className="text-2xl font-bold text-gray-900">{executives}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-orange-50 rounded-lg">
            <TreePine className="w-5 h-5 text-orange-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">事業所数</p>
            <p className="text-2xl font-bold text-gray-900">{offices}</p>
          </div>
        </div>
      </div>

      {/* 組織ツリーテーブル */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-200">
          <h2 className="text-base font-semibold text-gray-900">組織ツリー</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">部署コード</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600">部署名</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">責任者</th>
                <th className="px-4 py-3 text-right font-semibold text-gray-600 whitespace-nowrap">人数</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">上位部署</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {DEPARTMENTS.map((dept) => (
                <tr key={dept.id} className={`hover:bg-gray-50 ${dept.level === 0 ? "bg-gray-50 font-semibold" : ""}`}>
                  <td className="px-4 py-2.5 text-gray-500 whitespace-nowrap text-xs">{dept.code}</td>
                  <td className={`px-4 py-2.5 text-gray-900 whitespace-nowrap ${INDENT_CLASSES[dept.level] ?? ""}`}>
                    {dept.name}
                  </td>
                  <td className="px-4 py-2.5 text-gray-600 whitespace-nowrap">{dept.manager}</td>
                  <td className="px-4 py-2.5 text-gray-600 whitespace-nowrap text-right">{dept.members}名</td>
                  <td className="px-4 py-2.5 text-gray-500 whitespace-nowrap">{dept.parent ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 部署カード */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {DEPARTMENTS.filter((d) => d.level <= 1).map((dept) => (
          <div key={dept.id} className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-gray-900">{dept.name}</h3>
                <p className="text-xs text-gray-400 mt-0.5">{dept.code}</p>
              </div>
              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full font-medium">
                {dept.members}名
              </span>
            </div>
            <div className="mt-3 space-y-1">
              <p className="text-sm text-gray-600"><span className="text-gray-400">責任者:</span> {dept.manager}</p>
              <p className="text-sm text-gray-600"><span className="text-gray-400">業務:</span> {dept.work}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
