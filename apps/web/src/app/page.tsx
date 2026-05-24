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
  HardHat,
  Activity,
  Server,
  Database,
  Layers,
} from 'lucide-react'

const features = [
  {
    icon: Shield,
    title: '統合認証',
    description: 'SSOで全システムを一元管理。JWT/MFA/生体認証対応。',
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

const highlights = [
  { icon: Server, value: '22', label: 'マイクロサービス' },
  { icon: Layers, value: '5', label: 'アーキテクチャレイヤ' },
  { icon: Database, value: '451', label: 'テスト ALL PASS' },
  { icon: Activity, value: '99.9%', label: '稼働率' },
]

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero */}
      <header className="bg-gradient-to-br from-primary-900 via-primary-800 to-primary-700 text-white">
        <div className="max-w-6xl mx-auto px-4 py-20 sm:py-32">
          <div className="flex flex-col items-center text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-white/10 backdrop-blur mb-6">
              <HardHat className="h-8 w-8" />
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight">
              建設業統合OS
            </h1>
            <p className="mt-4 text-xl sm:text-2xl text-primary-200 font-light">
              Construction Enterprise OS
            </p>
            <p className="mt-6 max-w-2xl text-primary-100 text-lg leading-relaxed">
              建設・土木業界のデジタルトランスフォーメーションを加速する
              <br />
              統合業務プラットフォーム — 全業務・全データ・全プロセスを統合
            </p>
            <div className="flex flex-wrap justify-center gap-4 mt-10">
              <Link
                href="/login"
                className="inline-flex items-center gap-2 rounded-lg bg-white px-8 py-4 text-lg font-bold text-primary-700 shadow-lg hover:bg-primary-50 transition-colors"
              >
                ログイン
                <ArrowRight className="h-5 w-5" />
              </Link>
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 rounded-lg border-2 border-white/30 px-8 py-4 text-lg font-bold text-white hover:bg-white/10 transition-colors"
              >
                ダッシュボード
                <ArrowRight className="h-5 w-5" />
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Highlights */}
      <section className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-12">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {highlights.map((item) => {
              const Icon = item.icon
              return (
                <div key={item.label} className="text-center">
                  <Icon className="h-6 w-6 text-primary-600 mx-auto mb-2" />
                  <div className="text-3xl font-bold text-gray-900">{item.value}</div>
                  <div className="text-sm text-gray-500 mt-1">{item.label}</div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Features */}
      <main className="flex-1 max-w-6xl mx-auto px-4 py-20 w-full">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">
          主な機能
        </h2>
        <p className="text-center text-gray-500 mb-12 max-w-xl mx-auto">
          建設・土木業の全業務をカバーする統合プラットフォーム
        </p>
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

      {/* CTA */}
      <section className="bg-gradient-to-r from-primary-700 to-primary-800 text-white">
        <div className="max-w-6xl mx-auto px-4 py-16 text-center">
          <h2 className="text-2xl sm:text-3xl font-bold">
            建設DXを、今日から始めましょう
          </h2>
          <p className="mt-3 text-primary-200">
            オープンソース統合OSで、建設現場の未来を変える
          </p>
          <div className="mt-8 flex justify-center gap-4">
            <Link
              href="/login"
              className="inline-flex items-center gap-2 rounded-lg bg-white px-8 py-3 text-base font-bold text-primary-700 hover:bg-primary-50 transition-colors"
            >
              無料ではじめる
              <ArrowRight className="h-4 w-4" />
            </Link>
            <a
              href="https://github.com/Kensan196948G/Construction-Enterprise-OS"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-lg border-2 border-white/30 px-8 py-3 text-base font-bold text-white hover:bg-white/10 transition-colors"
            >
              GitHub
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-concrete-200 bg-white py-8">
        <div className="max-w-6xl mx-auto px-4 text-center text-sm text-gray-500">
          &copy; {new Date().getFullYear()} Construction Enterprise OS.
          All rights reserved.
        </div>
      </footer>
    </div>
  )
}
