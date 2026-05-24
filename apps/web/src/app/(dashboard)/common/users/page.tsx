"use client";

import { Users, UserPlus, UserCheck, Shield } from "lucide-react";

const USERS = [
  { id: 1, name: "田中 健一", email: "tanaka.k@construction-os.jp", title: "現場所長", role: "manager", lastLogin: "2024-11-30 09:12", status: "active" },
  { id: 2, name: "鈴木 次郎", email: "suzuki.j@construction-os.jp", title: "主任技術者", role: "manager", lastLogin: "2024-11-30 08:45", status: "active" },
  { id: 3, name: "佐藤 三郎", email: "sato.s@construction-os.jp", title: "現場監督", role: "field", lastLogin: "2024-11-29 17:22", status: "active" },
  { id: 4, name: "山田 五郎", email: "yamada.g@construction-os.jp", title: "施工管理", role: "field", lastLogin: "2024-11-30 07:55", status: "active" },
  { id: 5, name: "木村 七海", email: "kimura.n@construction-os.jp", title: "安全担当", role: "field", lastLogin: "2024-11-28 16:10", status: "active" },
  { id: 6, name: "中村 八郎", email: "nakamura.h@construction-os.jp", title: "職長", role: "field", lastLogin: "2024-11-27 14:30", status: "active" },
  { id: 7, name: "小林 九子", email: "kobayashi.k@construction-os.jp", title: "内装担当", role: "field", lastLogin: "2024-11-25 11:00", status: "active" },
  { id: 8, name: "加藤 十蔵", email: "kato.j@construction-os.jp", title: "設備技術者", role: "field", lastLogin: "2024-11-20 09:00", status: "inactive" },
  { id: 9, name: "伊藤 一郎", email: "ito.i@construction-os.jp", title: "経理担当", role: "viewer", lastLogin: "2024-11-30 10:00", status: "active" },
  { id: 10, name: "渡辺 管理", email: "watanabe.a@construction-os.jp", title: "システム管理者", role: "admin", lastLogin: "2024-11-30 08:00", status: "active" },
  { id: 11, name: "松本 花子", email: "matsumoto.h@construction-os.jp", title: "品質管理", role: "manager", lastLogin: "2024-11-10 15:00", status: "inactive" },
  { id: 12, name: "井上 太郎", email: "inoue.t@construction-os.jp", title: "現場補助", role: "field", lastLogin: "2024-10-01 09:00", status: "locked" },
];

const STATUS_STYLES: Record<string, string> = {
  active: "bg-green-100 text-green-800",
  inactive: "bg-gray-100 text-gray-700",
  locked: "bg-red-100 text-red-800",
};

const STATUS_LABELS: Record<string, string> = {
  active: "アクティブ",
  inactive: "非アクティブ",
  locked: "ロック",
};

const ROLE_STYLES: Record<string, string> = {
  admin: "bg-red-100 text-red-800",
  manager: "bg-purple-100 text-purple-800",
  field: "bg-blue-100 text-blue-800",
  viewer: "bg-gray-100 text-gray-700",
};

const ROLE_LABELS: Record<string, string> = {
  admin: "管理者",
  manager: "マネージャー",
  field: "現場担当",
  viewer: "閲覧のみ",
};

function Avatar({ name }: { name: string }) {
  const initials = name.split(" ").map((p) => p[0]).join("").slice(0, 2);
  return (
    <div className="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center text-xs font-bold flex-shrink-0">
      {initials}
    </div>
  );
}

export default function UsersPage() {
  const total = USERS.length;
  const active = USERS.filter((u) => u.status === "active").length;
  const inactive = USERS.filter((u) => u.status === "inactive").length;
  const locked = USERS.filter((u) => u.status === "locked").length;

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">ユーザー管理</h1>
          <p className="text-sm text-gray-500 mt-1">システム利用者の管理</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
          <UserPlus className="w-4 h-4" />
          ユーザー招待
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-blue-50 rounded-lg">
            <Users className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">総ユーザー数</p>
            <p className="text-2xl font-bold text-gray-900">{total}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-green-50 rounded-lg">
            <UserCheck className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">アクティブ</p>
            <p className="text-2xl font-bold text-gray-900">{active}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-gray-50 rounded-lg">
            <Users className="w-5 h-5 text-gray-500" />
          </div>
          <div>
            <p className="text-xs text-gray-500">非アクティブ</p>
            <p className="text-2xl font-bold text-gray-900">{inactive}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
          <div className="p-2 bg-red-50 rounded-lg">
            <Shield className="w-5 h-5 text-red-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">ロック</p>
            <p className="text-2xl font-bold text-gray-900">{locked}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left font-semibold text-gray-600">氏名</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">メール</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">役職</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">権限</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">最終ログイン</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600 whitespace-nowrap">ステータス</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {USERS.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                      <Avatar name={user.name} />
                      <span className="font-medium text-gray-900">{user.name}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{user.email}</td>
                  <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{user.title}</td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${ROLE_STYLES[user.role]}`}>
                      {ROLE_LABELS[user.role]}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500 whitespace-nowrap text-xs">{user.lastLogin}</td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_STYLES[user.status]}`}>
                      {STATUS_LABELS[user.status]}
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
