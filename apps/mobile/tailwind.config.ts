import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    '../../packages/ui/src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1a56db',
          50: '#eff6ff', 100: '#dbeafe', 200: '#bfdbfe',
          300: '#93c5fd', 400: '#60a5fa', 500: '#3b82f6',
          600: '#1a56db', 700: '#1e40af', 800: '#1e3a8a', 900: '#1e3a5f',
        },
        safety: { DEFAULT: '#f97316', 50: '#fff7ed', 500: '#f97316', 700: '#c2410c' },
        site: { DEFAULT: '#eab308', 50: '#fefce8', 500: '#eab308', 700: '#a16207' },
        danger: { DEFAULT: '#dc2626', 50: '#fef2f2', 500: '#ef4444', 700: '#b91c1c' },
        approve: { DEFAULT: '#16a34a', 50: '#f0fdf4', 500: '#22c55e', 700: '#15803d' },
        concrete: { DEFAULT: '#9ca3af', 50: '#f9fafb', 300: '#d1d5db', 500: '#6b7280', 700: '#374151' },
        soil: { DEFAULT: '#92400e', 100: '#fef3c7', 500: '#d97706', 700: '#92400e' },
      },
      fontFamily: {
        sans: ['Noto Sans JP', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
export default config
