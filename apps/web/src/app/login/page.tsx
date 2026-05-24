import Link from 'next/link'
import { HardHat } from 'lucide-react'

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary-900 via-primary-800 to-primary-700 px-4">
      <div className="w-full max-w-md">
        {/* Branding */}
        <div className="mb-8 text-center">
          <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-white/10 backdrop-blur mb-4">
            <HardHat className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-black text-white">Construction-Enterprise-OS</h1>
          <p className="mt-2 text-primary-200 text-sm">
            建設業統合オペレーティングシステム
          </p>
        </div>

        {/* Login Card */}
        <div className="rounded-2xl bg-white p-8 shadow-2xl">
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            ログイン
          </h2>

          <form className="space-y-5">
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                メールアドレス
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="block w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition"
                placeholder="your@company.co.jp"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                パスワード
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="block w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              className="w-full rounded-lg bg-primary-600 px-4 py-3 text-sm font-bold text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition"
            >
              ログイン
            </button>
          </form>

          <div className="mt-6 text-center">
            <Link
              href="#"
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              パスワードをお忘れの方
            </Link>
          </div>
        </div>

        <p className="mt-8 text-center text-sm text-primary-300">
          <Link href="/" className="hover:text-white transition">
            ← トップページに戻る
          </Link>
        </p>
      </div>
    </div>
  )
}
