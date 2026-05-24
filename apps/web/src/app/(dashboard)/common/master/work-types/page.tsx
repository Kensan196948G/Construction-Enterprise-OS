"use client";

import { Layers, Clock, CheckSquare } from "lucide-react";

const WORK_TYPES = [
  { id: 1, code: "WT-001", name: "機械掘削工", category: "土工", stdHours: 8, safetyReq: true, qualReq: "建設機械運転技能講習", cert: "車両系建設機械" },
  { id: 2, code: "WT-002", name: "人力掘削工", category: "土工", stdHours: 4, safetyReq: false, qualReq: null, cert: null },
  { id: 3, code: "WT-003", name: "場所打ちコンクリート杭工", category: "基礎工", stdHours: 16, safetyReq: true, qualReq: "杭基礎施工管理技術者", cert: "アースドリル工法" },
  { id: 4, code: "WT-004", name: "既製コンクリート杭打設工", category: "基礎工", stdHours: 12, safetyReq: true, qualReq: "杭基礎施工管理技術者", cert: "プレボーリング工法" },
  { id: 5, code: "WT-005", name: "鉄筋組立工", category: "躯体工", stdHours: 6, safetyReq: false, qualReq: "鉄筋施工技能士", cert: null },
  { id: 6, code: "WT-006", name: "型枠組立工", category: "躯体工", stdHours: 6, safetyReq: false, qualReq: "型枠施工技能士", cert: null },
  { id: 7, code: "WT-007", name: "コンクリート打設工", category: "躯体工", stdHours: 8, safetyReq: true, qualReq: "コンクリート主任技士", cert: "ポンプ車使用" },
  { id: 8, code: "WT-008", name: "タイル工", category: "仕上工", stdHours: 5, safetyReq: false, qualReq: "タイル張り技能士", cert: null },
  { id: 9, code: "WT-009", name: "左官工", category: "仕上工", stdHours: 5, safetyReq: false, qualReq: "左官技能士", cert: null },
  { id: 10, code: "WT-010", name: "電気設備工事", category: "設備工", stdHours: 8, safetyReq: true, qualReq: "電気工事士（第2種以上）", cert: "第2種電気工事士" },
  { id: 11, code: "WT-011", name: "給排水設備工事", category: "設備工", stdHours: 8, safetyReq: false, qualReq: "管工事施工管理技士", cert: null },
  { id: 12, code: "WT-012", name: "アスファルト舗装工", category: "外構", stdHours: 10, safetyReq: true, qualReq: null, cert: "ローラー運転技能講習" },
];

const CATEGORY_COLORS: Record<string, string> = {
  土工: "bg-yellow-100 text-yellow-800",
  基礎工: "bg-orange-100 text-orange-800",
  躯体工: "bg-blue-100 text-blue-800",
  仕上工: "bg-green-100 text-green-800",
  設備工: "bg-purple-100 text-purple-800",
  外構: "bg-teal-100 text-teal-800",
};

export default function WorkTypesPage() {
  const totalTypes = WORK_TYPES.length;
  const categories = [...new Set(WORK_TYPES.map((w) => w.category))].length;
  const safetyRequired = WORK_TYPES.filter((w) => w.safetyReq).length;

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">作業種別マスタ</h1>
          <p className="text-sm text-gray-500 mt-1">工事作業の種別・資格・安全要件管理</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
          <Layers className="w-4 h-4" />
          種別追加
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-blue-50 rounded-lg">
            <Layers className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">登録種別数</p>
            <p className="text-2xl font-bold text-gray-900">{totalTypes}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-green-50 rounded-lg">
            <Clock className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">カテゴリ数</p>
            <p className="text-2xl font-bold text-gray-900">{categories}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-orange-50 rounded-lg">
            <CheckSquare className="w-5 h-5 text-orange-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">安全要件あり</p>
            <p className="text-2xl font-bold text-gray-900">{safetyRequired}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">種別コード</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600">種別名</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">カテゴリ</th>
                <th className="px-4 py-3 text-right font-semibold text-gray-600 whitespace-nowrap">標準工数(h)</th>
                <th className="px-4 py-3 text-center font-semibold text-gray-600 whitespace-nowrap">安全要件</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600">資格要件</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {WORK_TYPES.map((wt) => (
                <tr key={wt.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-500 whitespace-nowrap text-xs font-mono">{wt.code}</td>
                  <td className="px-4 py-3 font-medium text-gray-900">{wt.name}</td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${CATEGORY_COLORS[wt.category] ?? "bg-gray-100 text-gray-700"}`}>
                      {wt.category}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-600 whitespace-nowrap text-right">{wt.stdHours}h</td>
                  <td className="px-4 py-3 text-center">
                    {wt.safetyReq ? (
                      <CheckSquare className="w-4 h-4 text-orange-500 mx-auto" />
                    ) : (
                      <span className="text-gray-300">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-gray-600 text-xs">
                    {wt.qualReq ?? <span className="text-gray-400">不要</span>}
                    {wt.cert && <span className="ml-2 px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">{wt.cert}</span>}
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
