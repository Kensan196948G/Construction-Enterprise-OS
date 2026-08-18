import { defineConfig } from "@playwright/test";

/**
 * Browser E2E — Construction Enterprise OS MVP (Cloudflare Pages プレビュー)
 *
 * 対象: https://construction-os-mvp.mirai-dx-platform.com
 * (OpenDesign WebUI 単一HTML を Pages で配信。SPA フォールバック _redirects 対応済み)
 *
 * 実行:
 *   npx playwright test            # ローカル(プレビューURL 直叩き)
 *   npx playwright test --ui       # UI モード
 */
export default defineConfig({
  testDir: "./e2e",
  timeout: 45_000,
  fullyParallel: false,
  retries: 1,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: process.env.E2E_BASE_URL || "https://construction-os-mvp.mirai-dx-platform.com",
    channel: "chromium",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    viewport: { width: 1440, height: 900 },
  },
  projects: [
    { name: "desktop", use: { viewport: { width: 1440, height: 900 } } },
    { name: "mobile", use: { viewport: { width: 390, height: 844 } } },
  ],
});
