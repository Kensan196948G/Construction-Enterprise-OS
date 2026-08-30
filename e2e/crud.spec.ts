/**
 * Browser E2E — CRUD 操作(データ取得・新規作成・編集・削除)
 *
 * 対象: https://construction-os-mvp.mirai-dx-platform.com (E2E_BASE_URL で変更可)
 * OpenDesign WebUI バンドル(正本スタイル)に組み込んだデータ層(localStorage ストア)と
 * CRUD UI を検証する。既存のダミーデータを引き継いだシードに、
 * 新規作成・編集・削除・永続化が機能することを確認する。
 */

import { test, expect, type Page } from "@playwright/test";

async function fillModal(page: Page, placeholder: string, value: string) {
  await page
    .locator(".ceos-crud-modal")
    .getByPlaceholder(placeholder)
    .fill(value);
}

test.describe("CRUD — ダッシュボード(projects)", () => {
  test("一覧表示: シードデータ(工事進捗)が表示される", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(2500);
    await expect(
      page.getByText("おかえりなさい、田中さん").first(),
    ).toBeVisible();
    await expect(page.getByText("品川タワー新築工事").first()).toBeVisible();
    await expect(page.getByText("工事進捗").first()).toBeVisible();
  });

  test("新規作成: 新規工事 → 工事進捗に追加される", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(2500);
    await page.getByRole("button", { name: "新規工事" }).first().click();
    await expect(page.locator(".ceos-crud-modal")).toBeVisible();
    await fillModal(page, "工事名", "CRUDテスト橋梁工事");
    await page.getByRole("button", { name: "保存" }).click();
    await page.waitForTimeout(800);
    await expect(page.getByText("CRUDテスト橋梁工事").first()).toBeVisible();
  });

  test("編集: 一覧の項目を編集 → 反映される", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(2500);
    // 最初の編集ボタン(最近のアクティビティ)で編集 → 反映
    await page.getByRole("button", { name: "編集" }).first().click();
    await page.waitForTimeout(500);
    await fillModal(page, "活動内容", "編集後のアクティビティ");
    await page.getByRole("button", { name: "保存" }).click();
    await page.waitForTimeout(800);
    await expect(
      page.getByText("編集後のアクティビティ").first(),
    ).toBeVisible();
  });

  test("削除: 確認ダイアログ → 一覧から消える", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(2500);
    // 最初のアクティビティを削除 → 表示から消える
    await expect(
      page.getByText("安全パトロール報告書が提出されました").first(),
    ).toBeVisible();
    await page.getByRole("button", { name: "削除" }).first().click();
    await expect(page.getByText("削除の確認").first()).toBeVisible();
    await page.getByRole("button", { name: "削除する" }).click();
    await page.waitForTimeout(800);
    await expect(
      page.getByText("安全パトロール報告書が提出されました").first(),
    ).toBeHidden();
  });

  test("永続化: 作成したデータがリロード後も残る", async ({ page }) => {
    // 約9MBの単一HTMLバンドル+実行時Babel変換のため、reload後の再初期化に
    // デフォルトの45秒タイムアウトでは不足する場合がある。このテストのみ延長する。
    test.setTimeout(90_000);
    await page.goto("/");
    await page.waitForTimeout(2500);
    await page.getByRole("button", { name: "新規工事" }).first().click();
    await fillModal(page, "工事名", "永続化テスト工事");
    await page.getByRole("button", { name: "保存" }).click();
    await page.waitForTimeout(800);
    await expect(page.getByText("永続化テスト工事").first()).toBeVisible();
    await page.reload();
    await expect(page.getByText("永続化テスト工事").first()).toBeVisible({
      timeout: 60_000,
    });
  });
});

test.describe("CRUD — ワークフロー(workflows)", () => {
  test("新規申請: 申請を登録すると一覧に追加される", async ({ page }) => {
    await page.goto("/#/workflow/approval");
    await page.waitForTimeout(3500);
    await page.getByRole("button", { name: "新規申請" }).click();
    await expect(page.locator(".ceos-crud-modal")).toBeVisible();
    await fillModal(page, "申請件名", "E2Eテスト承認依頼");
    await page.getByRole("button", { name: "保存" }).click();
    await page.waitForTimeout(800);
    await expect(page.getByText("E2Eテスト承認依頼").first()).toBeVisible();
  });

  test("タブ切替: 稟議タブで稟議データが表示される", async ({ page }) => {
    await page.goto("/#/workflow/approval");
    await page.waitForTimeout(3500);
    await page
      .locator("main")
      .getByRole("button", { name: "稟議", exact: true })
      .click();
    await page.waitForTimeout(800);
    await expect(
      page.getByText("施工計画書（躯体工事）承認依頼").first(),
    ).toBeVisible();
  });
});

test.describe("CRUD — 現場DX・文書・IoT", () => {
  test("現場DX: 新規工事登録 → 工事一覧に追加される", async ({ page }) => {
    await page.goto("/#/field/projects");
    await page.waitForTimeout(3500);
    await expect(page.getByText("品川タワー新築工事").first()).toBeVisible();
    await page.getByRole("button", { name: "新規工事登録" }).click();
    await fillModal(page, "工事名", "現場DXテスト工事");
    await page.getByRole("button", { name: "保存" }).click();
    await page.waitForTimeout(800);
    await expect(page.getByText("現場DXテスト工事").first()).toBeVisible();
  });

  test("文書: アップロード → 一覧に追加される", async ({ page }) => {
    await page.goto("/#/documents/pdf");
    await page.waitForTimeout(3500);
    await page.getByRole("button", { name: "アップロード" }).click();
    await fillModal(page, "ファイル名", "E2E試験成績書.pdf");
    await page.getByRole("button", { name: "保存" }).click();
    await page.waitForTimeout(800);
    // モバイルでは一覧が横スクロール領域になるため、DOM への追加を確認
    await expect(page.getByText("E2E試験成績書.pdf").first()).toBeAttached();
  });

  test("IoT: センサー登録 → 一覧に追加される", async ({ page }) => {
    await page.goto("/#/iot/sensors");
    await page.waitForTimeout(3500);
    await page.getByRole("button", { name: "センサー登録" }).click();
    await fillModal(page, "センサー名", "E2Eテストセンサー");
    await page.getByRole("button", { name: "保存" }).click();
    await page.waitForTimeout(800);
    await expect(page.getByText("E2Eテストセンサー").first()).toBeVisible();
  });

  test("CAD図面: 図面登録 → 一覧に追加される(DOC_FIELDS_CAD 未定義エラーの再発防止)", async ({
    page,
  }) => {
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto("/#/documents/cad");
    await page.waitForTimeout(3500);
    await expect(
      page.getByText("構造図_7F_鉄骨配置図.dwg").first(),
    ).toBeVisible();
    await page.getByRole("button", { name: "図面登録" }).click();
    await fillModal(page, "ファイル名", "E2Eテスト図面.dwg");
    await page.getByRole("button", { name: "保存" }).click();
    await page.waitForTimeout(800);
    await expect(page.getByText("E2Eテスト図面.dwg").first()).toBeVisible();
    expect(errors, `pageerror(s) detected: ${errors.join("; ")}`).toHaveLength(
      0,
    );
  });
});
