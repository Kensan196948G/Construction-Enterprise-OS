/**
 * Browser E2E — Construction Enterprise OS MVP (Cloudflare Pages プレビュー)
 *
 * 対象: https://construction-os-mvp.mirai-dx-platform.com
 * OpenDesign 設計プロトタイプ(単一HTML React SPA)の主要業務フローを検証する。
 * 正常系・ルーティング・ロール切替・通知・モバイル・キーボード操作をカバー。
 */

import { test, expect } from "@playwright/test";

test.describe("Construction Enterprise OS MVP WebUI", () => {
  test("ホーム: タイトル・サイドバー・ダッシュボードKPIが表示される", async ({
    page,
  }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/Construction Enterprise OS/);

    // サイドバー(ロゴ + カテゴリメニュー)
    await expect(page.getByText("Enterprise OS").first()).toBeVisible();
    await expect(
      page.getByRole("button", { name: "ダッシュボード" }).first(),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "現場DX" }).first(),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "ワークフロー" }).first(),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "ERP・経営管理" }).first(),
    ).toBeVisible();

    // ダッシュボード KPI/カード(実ダミーデータ)
    await expect(
      page.getByText("おかえりなさい、田中さん").first(),
    ).toBeVisible();
    await expect(page.getByText("進行中工事").first()).toBeVisible();
    await expect(page.getByText("要承認").first()).toBeVisible();
    await expect(page.getByText("品川タワー新築工事").first()).toBeVisible();
  });

  test("SPAフォールバック: 直接URLでもアプリが起動する", async ({ page }) => {
    // プロトタイプは state ベースルーティング(URL同期なし)のため、
    // 直接URLではホームが表示されることを確認する(SPA フォールバック _redirects)
    await page.goto("/workflow/approval");
    await expect(page).toHaveTitle(/Construction Enterprise OS/);
    await expect(page.getByText("進行中工事").first()).toBeVisible();
  });

  test("ワークフロー画面: 承認一覧のダミーデータが表示される", async ({
    page,
  }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "ワークフロー" }).first().click();
    // 注: プロトタイプのサイドバーは展開時に他要素がポインタイベントを横取りする
    // (既知のUI課題)ため、フォーカス+Enter で操作する
    const ringiBtn = page.getByRole("button", { name: "稟議" }).first();
    await ringiBtn.focus();
    await page.keyboard.press("Enter");
    await expect(page.getByText("承認待ち").first()).toBeVisible();
    await expect(page.getByText("SLA達成率").first()).toBeVisible();
    await expect(
      page.getByText("施工計画書（躯体工事）承認依頼").first(),
    ).toBeVisible();
  });

  test("現場DX画面: 工事一覧のダミーデータが表示される", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "現場DX" }).first().click();
    const projectsBtn = page.getByRole("button", { name: "工事一覧" }).first();
    await projectsBtn.focus();
    await page.keyboard.press("Enter");
    await expect(page.getByText("品川タワー新築工事").first()).toBeVisible();
  });

  test("ロール切替: 現場監督ビュー→経営層ビュー", async ({ page }) => {
    await page.goto("/");
    // ヘッダーのロール切替ボタン(初期状態: 全表示)
    await page.locator("header button", { hasText: "全表示" }).first().click();
    await page.getByRole("button", { name: "現場監督" }).click();
    // サイドバーにロールバッジが表示される
    await expect(page.getByText("現場監督ビュー").first()).toBeVisible();

    // 経営層に切替
    await page
      .locator("header button", { hasText: "現場監督" })
      .first()
      .click();
    await page.getByRole("button", { name: "経営層", exact: true }).click();
    await expect(page.getByText("経営層ビュー").first()).toBeVisible();
  });

  test("通知パネル: 承認依頼・すべて既読が表示される", async ({ page }) => {
    await page.goto("/");
    // ヘッダーの通知ボタン(未読バッジ「2」が表示名)
    await page.getByRole("button", { name: "2", exact: true }).click();
    await expect(page.getByText("すべて既読").first()).toBeVisible();
    await expect(page.getByText("承認依頼").first()).toBeVisible();
  });
});

test.describe("モバイル / アクセシビリティ", () => {
  test("モバイル: ハンバーガーメニューでサイドバーを操作できる", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("/");
    await page.waitForTimeout(1500);

    // サイドバー閉時: 本文がビューポート幅の大半を使えること
    // (サイドバー264pxが常時flex領域を占有する回帰の再発防止)
    const closedMainWidth = await page
      .locator("main")
      .evaluate((el) => el.getBoundingClientRect().width);
    expect(closedMainWidth).toBeGreaterThan(350);

    const menuBtn = page.locator(".mobile-menu-btn");
    await expect(menuBtn).toBeVisible();
    await menuBtn.click();
    await expect(page.getByText("Enterprise OS").first()).toBeVisible();

    // サイドバー開時: オーバーレイとして表示される(本文幅の分割ではない)
    const openedSidebarWidth = await page
      .locator("aside")
      .evaluate((el) => el.getBoundingClientRect().width);
    expect(openedSidebarWidth).toBeGreaterThan(200);
  });

  test("キーボード: Tab で最初の操作可能要素にフォーカスが移動する", async ({
    page,
  }) => {
    await page.goto("/");
    await page.keyboard.press("Tab");
    const tag = await page.evaluate(
      () => document.activeElement?.tagName ?? "",
    );
    expect(["BUTTON", "A", "INPUT", "SELECT"]).toContain(tag);
  });

  test("ダークモード: テーマ変数切替後も主要コンテンツが表示される", async ({
    page,
  }) => {
    await page.goto("/");
    const before = await page.evaluate(() =>
      getComputedStyle(document.documentElement).getPropertyValue("--bg"),
    );
    await page.evaluate(() => {
      document.documentElement.style.setProperty("--bg", "#0f172a");
      document.documentElement.style.setProperty("--text", "#e2e8f0");
    });
    const after = await page.evaluate(() =>
      document.documentElement.style.getPropertyValue("--bg"),
    );
    expect(before).not.toBe(after);
    await expect(page.getByText("進行中工事").first()).toBeVisible();
  });
});
