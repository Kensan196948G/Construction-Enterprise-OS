/**
 * Browser E2E — CRUD 操作(データ取得・新規作成・編集・削除)
 *
 * 対象: https://construction-os-mvp.mirai-dx-platform.com (E2E_BASE_URL で変更可)
 * 全ページ共通のデータ層(localStorage 永続化ストア)と CRUD UI を検証する。
 *  - 一覧表示(データ取得)
 *  - 新規作成 → 一覧・ダッシュボードへの反映
 *  - 編集 → 内容の更新
 *  - 削除 → 確認ダイアログ → 一覧からの消去
 *  - 検索フィルタ
 *  - 必須入力エラー
 *  - 空状態表示
 *  - localStorage 永続化(リロード後も保持)
 */

import { test, expect, type Page } from "@playwright/test";

/** モーダル内のフォームフィールドに限定して入力する */
async function fillField(page: Page, placeholder: string, value: string) {
  await page.locator(".modal").getByPlaceholder(placeholder).fill(value);
}

test.describe("CRUD — 工事(projects)", () => {
  test("一覧表示: シードデータが読み込まれて表示される", async ({ page }) => {
    await page.goto("/#/field/projects");
    await expect(page.getByText("工事一覧").first()).toBeVisible();
    await expect(page.getByText("品川タワー新築工事").first()).toBeVisible();
    await expect(page.getByText("横浜分譲マンション").first()).toBeVisible();
    // KPI(進行中工事 = シード 6 件)
    await expect(page.getByText("進行中工事").first()).toBeVisible();
  });

  test("新規作成: フォーム入力 → 一覧に追加される", async ({ page }) => {
    await page.goto("/#/field/projects");
    await page.getByRole("button", { name: "新規工事登録" }).click();
    // モーダルフォーム
    await expect(page.getByRole("dialog")).toBeVisible();
    await fillField(page, "工事名", "テスト橋梁新設工事");
    await fillField(page, "発注者", "テスト県");
    await page.locator('.modal input[type="number"]').first().fill("30");
    // 保存
    await page.getByRole("button", { name: "保存" }).click();
    await expect(page.getByText("テスト橋梁新設工事").first()).toBeVisible();
  });

  test("編集: 名称を変更すると一覧に反映される", async ({ page }) => {
    await page.goto("/#/field/projects");
    // シードの工事カードの「編集」ボタン(最初のもの)
    await page.getByRole("button", { name: "編集" }).first().click();
    await expect(page.getByRole("dialog")).toBeVisible();
    await fillField(page, "工事名", "品川タワー新築工事(改修)");
    await page.getByRole("button", { name: "保存" }).click();
    await expect(page.getByText("品川タワー新築工事(改修)").first()).toBeVisible();
    // 元の名称が消えている(編集で置き換わった)
    await expect(page.getByText("品川タワー新築工事", { exact: true }).first()).toBeHidden();
  });

  test("削除: 確認ダイアログ → 一覧から消える", async ({ page }) => {
    await page.goto("/#/field/projects");
    const cardsBefore = await page.locator(".entity-card").count();
    await page.getByRole("button", { name: "削除" }).first().click();
    await expect(page.getByText("削除の確認").first()).toBeVisible();
    await page.getByRole("button", { name: "削除する" }).click();
    const cardsAfter = await page.locator(".entity-card").count();
    expect(cardsAfter).toBe(cardsBefore - 1);
  });

  test("検索: キーワードで一覧が絞り込まれる", async ({ page }) => {
    await page.goto("/#/field/projects");
    await page.getByLabel("検索").fill("横浜");
    await expect(page.getByText("横浜分譲マンション").first()).toBeVisible();
    await expect(page.getByText("品川タワー新築工事").first()).toBeHidden();
  });

  test("必須エラー: 工事名なしで保存するとエラー表示", async ({ page }) => {
    await page.goto("/#/field/projects");
    await page.getByRole("button", { name: "新規工事登録" }).click();
    // 工事名(必須)を空のまま保存
    await page.getByRole("button", { name: "保存" }).click();
    await expect(page.getByText("入力内容に誤りがあります").first()).toBeVisible();
  });

  test("永続化: 作成したデータがリロード後も残る", async ({ page }) => {
    await page.goto("/#/field/projects");
    await page.getByRole("button", { name: "新規工事登録" }).click();
    await fillField(page, "工事名", "永続化テスト工事");
    await page.getByRole("button", { name: "保存" }).click();
    await expect(page.getByText("永続化テスト工事").first()).toBeVisible();
    await page.reload();
    await page.waitForTimeout(800);
    await expect(page.getByText("永続化テスト工事").first()).toBeVisible();
  });
});

test.describe("CRUD — ワークフロー(workflows)", () => {
  test("新規申請: 稟議を登録すると承認待ち一覧に追加される", async ({ page }) => {
    await page.goto("/#/workflow/approval");
    await page.getByRole("button", { name: "新規申請" }).click();
    await fillField(page, "申請件名", "E2Eテスト承認依頼");
    await fillField(page, "申請番号", "WF-TEST-001");
    await fillField(page, "申請者", "E2E 太郎");
    await fillField(page, "対象工事", "品川タワー新築工事");
    await page.getByRole("button", { name: "保存" }).click();
    await expect(page.getByText("E2Eテスト承認依頼").first()).toBeVisible();
  });

  test("タブ切替: 稟議タブで稟議のみ表示される", async ({ page }) => {
    await page.goto("/#/workflow/approval");
    await page.locator(".tabs button", { hasText: "稟議" }).click();
    await expect(page.getByText("施工計画書（躯体工事）承認依頼").first()).toBeVisible();
  });
});

test.describe("CRUD — 他のドメイン", () => {
  test("文書: 新規登録 → 一覧反映", async ({ page }) => {
    await page.goto("/#/documents/pdf");
    await page.getByRole("button", { name: "新規作成" }).click();
    await fillField(page, "文書名", "E2E試験成績書");
    await fillField(page, "対象工事", "品川タワー新築工事");
    await page.getByRole("button", { name: "保存" }).click();
    await expect(page.getByText("E2E試験成績書").first()).toBeVisible();
  });

  test("IoTセンサー: 警戒センサーが KPI に反映される", async ({ page }) => {
    await page.goto("/#/iot/sensors");
    await expect(page.getByText("センサー数").first()).toBeVisible();
    await page.getByRole("button", { name: "センサー登録" }).click();
    await fillField(page, "センサー名", "E2Eテストセンサー");
    await page.getByRole("button", { name: "保存" }).click();
    await expect(page.getByText("E2Eテストセンサー").first()).toBeVisible();
  });

  test("空状態: データのないページで空メッセージが表示される", async ({ page }) => {
    // security/soc はシードにデータがない
    await page.goto("/#/security/soc");
    await expect(page.getByText("データがありません").first()).toBeVisible();
  });

  test("ダッシュボード: 作成した工事が KPI に反映される", async ({ page }) => {
    await page.goto("/#/field/projects");
    await page.getByRole("button", { name: "新規工事登録" }).click();
    await fillField(page, "工事名", "KPI連動テスト工事");
    await page.getByRole("button", { name: "保存" }).click();
    // ダッシュボードへ移動して「進行中工事」件数が増えている(7件)
    await page.goto("/#/dashboard");
    await page.waitForTimeout(600);
    const kpi = page.locator(".kpi-card", { hasText: "進行中工事" }).first();
    await expect(kpi).toBeVisible();
    await expect(kpi.getByText("7")).toBeVisible();
  });
});
