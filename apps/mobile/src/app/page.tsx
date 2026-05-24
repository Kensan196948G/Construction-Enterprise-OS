'use client';

import { useState } from 'react';
import {
  Camera,
  ClipboardList,
  AlertTriangle,
  ClipboardCheck,
  Wrench,
  FileText,
  CameraIcon,
  Settings,
  Wifi,
  WifiOff,
  Sun,
  Users,
  MapPin,
  ChevronRight,
} from 'lucide-react';
import { useNetworkStatus } from '@/lib/network-status';

type Tab = 'gemba' | 'report' | 'photo' | 'inspection' | 'settings';

const tabs: { key: Tab; label: string; icon: React.ElementType }[] = [
  { key: 'gemba', label: '現場', icon: Wrench },
  { key: 'report', label: '報告', icon: ClipboardList },
  { key: 'photo', label: '写真', icon: CameraIcon },
  { key: 'inspection', label: '点検', icon: ClipboardCheck },
  { key: 'settings', label: '設定', icon: Settings },
];

export default function MobileHome() {
  const [activeTab, setActiveTab] = useState<Tab>('gemba');
  const { isOnline } = useNetworkStatus();

  return (
    <div className="flex flex-col min-h-screen pb-16">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-primary text-white shadow-md">
        <div className="flex items-center justify-between px-4 h-14">
          <h1 className="text-lg font-bold">CEO-OS</h1>
          <div className="flex items-center gap-2">
            <span className="text-xs opacity-80">現場モバイル</span>
            {isOnline ? (
              <Wifi className="w-4 h-4 text-green-300" />
            ) : (
              <WifiOff className="w-4 h-4 text-red-300" />
            )}
            <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-400' : 'bg-red-400'}`} />
          </div>
        </div>
      </header>

      {/* Offline Banner */}
      {!isOnline && (
        <div className="bg-yellow-100 border-b border-yellow-200 px-4 py-2 text-sm text-yellow-800 text-center">
          オフラインモード - データは復帰時に自動同期されます
        </div>
      )}

      {/* Main Content */}
      <main className="flex-1 px-4 py-4 space-y-4">
        {/* Today's Work Card */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="bg-primary/5 px-4 py-3 border-b border-gray-100 flex items-center gap-2">
            <Sun className="w-5 h-5 text-primary" />
            <h2 className="font-bold text-gray-900">本日の作業</h2>
          </div>
          <div className="p-4 space-y-3">
            <div className="flex items-center gap-3 text-sm text-gray-600">
              <Users className="w-4 h-4 text-primary/70" />
              <span>作業員: <strong className="text-gray-900">12名</strong></span>
            </div>
            <div className="flex items-center gap-3 text-sm text-gray-600">
              <MapPin className="w-4 h-4 text-primary/70" />
              <span>現場: <strong className="text-gray-900">渋谷駅前再開発 C工区</strong></span>
            </div>
            <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-700">
              <p className="font-medium mb-1">躯体工事 3F 壁配筋</p>
              <p className="text-xs text-gray-500">8:00〜17:00 / 進捗 65%</p>
            </div>
            <button className="flex items-center justify-between w-full text-sm text-primary font-medium pt-1 border-t border-gray-100">
              <span>詳細を見る</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </section>

        {/* Quick Actions */}
        <section>
          <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wide mb-3">クイック操作</h2>
          <div className="grid grid-cols-2 gap-3">
            <QuickAction
              icon={Camera}
              label="写真撮影"
              color="bg-blue-500"
              onClick={() => {}}
            />
            <QuickAction
              icon={FileText}
              label="日報作成"
              color="bg-green-500"
              onClick={() => {}}
            />
            <QuickAction
              icon={AlertTriangle}
              label="危険報告"
              color="bg-safety"
              onClick={() => {}}
            />
            <QuickAction
              icon={ClipboardCheck}
              label="点検開始"
              color="bg-purple-500"
              onClick={() => {}}
            />
          </div>
        </section>

        {/* Recent Reports */}
        <section>
          <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wide mb-3">最近の報告</h2>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 divide-y divide-gray-100">
            {[
              { type: '日報', title: '2024-05-24 躯体工事', time: '17:30', status: 'synced' },
              { type: '写真', title: '配筋検査写真 (12枚)', time: '14:15', status: 'synced' },
              { type: '危険', title: '足場ぐらつき報告', time: '10:45', status: 'pending' },
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-3 px-4 py-3">
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  item.type === '日報' ? 'bg-blue-100 text-blue-700' :
                  item.type === '写真' ? 'bg-purple-100 text-purple-700' :
                  'bg-safety/10 text-safety'
                }`}>
                  {item.type}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{item.title}</p>
                  <p className="text-xs text-gray-400">{item.time}</p>
                </div>
                {item.status === 'pending' && (
                  <span className="text-xs text-yellow-600 bg-yellow-50 px-2 py-0.5 rounded-full">未同期</span>
                )}
              </div>
            ))}
          </div>
        </section>
      </main>

      {/* Bottom Tab Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-10 safe-area-bottom">
        <div className="flex items-center justify-around h-16">
          {tabs.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`flex flex-col items-center justify-center gap-0.5 min-h-[44px] min-w-[44px] px-3 py-1 rounded-lg transition-colors ${
                activeTab === key
                  ? 'text-primary'
                  : 'text-gray-400 hover:text-gray-600'
              }`}
            >
              <Icon className="w-6 h-6" />
              <span className="text-[10px] font-medium">{label}</span>
            </button>
          ))}
        </div>
      </nav>
    </div>
  );
}

function QuickAction({
  icon: Icon,
  label,
  color,
  onClick,
}: {
  icon: React.ElementType;
  label: string;
  color: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex flex-col items-center justify-center gap-2 ${color} text-white rounded-xl p-4 min-h-[88px] shadow-sm active:scale-95 transition-transform`}
    >
      <Icon className="w-7 h-7" />
      <span className="text-sm font-bold">{label}</span>
    </button>
  );
}
