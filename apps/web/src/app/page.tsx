import Link from 'next/link'
import {
  Shield,
  Map,
  Building2,
  Cpu,
  Sparkles,
  FileText,
  GitBranch,
  BarChart3,
  ArrowRight,
} from 'lucide-react'

const features = [
  {
    icon: Shield,
    title: '統合認証',
    description: 'シングルサインオンで全システムを一元管理。生体認証対応。',
  },
  {
    icon: Map,
    title: 'GIS統合',
    description: '地理情報システムと工事情報をリアルタイム連携。',
  },
  {
    icon: Building2,
    title: 'BIM/CIM',
    description: '3Dモデルと施工管理の統合プラットフォーム。',
  },
  {
    icon: Cpu,
    title: 'IoT統合',
    description: '現場センサー・重機データの統合監視と予知保全。',
  },
  {
    icon: Sparkles,
    title: 'AI支援',
    description: '施工計画最適化、品質検査自動化、危険予測AI。',
  },
  {
    icon: FileText,
    title: '文書管理',
    description: '電子承認ワークフローと建設書類の一元管理。',
  },
  {
    icon: GitBranch,
    title: 'ワークフロー',
    description: '工程管理・承認フローの自動化と可視化。',
  },
  {
    icon: BarChart3,
    title: '経営管理',
    description: '原価管理、予実管理、KPIダッシュボード。',
  },
]

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero */}
      <header className="bg-gradient-to-br from-primary-900 via-primary-800 to-primary-700 text-white">
        <div className="max-w-6xl mx-auto px-4 py-20 sm:py-32">
          <div className="flex flex-col items-center text-center">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight">
              建設業統合OS
            </h1>
            <p className="mt-4 text-xl sm:text-2xl text-primary-200 font-light">
              Construction Enterprise OS
            </p>
            <p className="mt-6 max-w-2xl text-primary-100 text-lg">
              建設・土木業界のデジタルトランスフォーメーションを加速する
              <br />
              統合業務プラットフォーム
            </p>
            <Link
              href="/login"
              className="mt-10 inline-flex items-center gap-2 rounded-lg bg-white px-8 py-4 text-lg font-bold text-primary-700 shadow-lg hover:bg-primary-50 transition-colors"
            >
              ログイン
              <ArrowRight className="h-5 w-5" />
            </Link>
          </div>
        </div>
      </header>

      {/* Features */}
      <main className="flex-1 max-w-6xl mx-auto px-4 py-20 w-full">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          主な機能
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature) => {
            const Icon = feature.icon
            return (
              <div
                key={feature.title}
                className="group rounded-xl border border-concrete-200 bg-white p-6 hover:shadow-md hover:border-primary-300 transition-all"
              >
                <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary-50 text-primary-600 group-hover:bg-primary-100 transition-colors">
                  <Icon className="h-6 w-6" />
                </div>
                <h3 className="mt-4 font-bold text-gray-900">{feature.title}</h3>
                <p className="mt-2 text-sm text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            )
          })}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-concrete-200 bg-white py-8">
        <div className="max-w-6xl mx-auto px-4 text-center text-sm text-gray-500">
          &copy; {new Date().getFullYear()} CEO-OS Construction Enterprise OS.
          All rights reserved.
        </div>
      </footer>
    </div>
  )
}
