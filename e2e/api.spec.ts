/**
 * API E2E — 本番 HTTPS 経由の API・認証・DB(Neon)検証
 *
 * 対象: https://construction-os.mirai-dx-platform.com/api/v1/*
 * (Pages Function プロキシ → Cloudflare Tunnel → auth サービス → Neon)
 *
 * 正常系(ログイン→JWT→認証付きAPI)・エラー系(401/422)・DB 接続を検証する。
 */

import { test, expect, type APIRequestContext } from "@playwright/test";

const BASE = process.env.E2E_API_BASE_URL || "https://construction-os.mirai-dx-platform.com";
const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || "admin@mirai-dx-platform.com";
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || "AdminPass123!";

async function login(request: APIRequestContext, email: string, password: string) {
  return request.post(`${BASE}/api/v1/auth/login`, {
    data: { email, password },
    headers: { "Content-Type": "application/json" },
  });
}

test.describe("Construction Enterprise OS API (HTTPS)", () => {
  test("ヘルスチェック: 全サービス healthy が返る", async ({ request }) => {
    const res = await request.get(`${BASE}/api/v1/health/services`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    const services = body.services as Array<{ name: string; status: string }>;
    expect(services.length).toBeGreaterThanOrEqual(5);
    for (const s of services) {
      expect(s.status).toBe("healthy");
    }
  });

  test("認証: 正しい資格情報で JWT が発行される", async ({ request }) => {
    const res = await login(request, ADMIN_EMAIL, ADMIN_PASSWORD);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.success).toBe(true);
    expect(body.data.access_token).toBeTruthy();
    expect(body.data.refresh_token).toBeTruthy();
  });

  test("認証エラー: 誤パスワードで 401 が返る", async ({ request }) => {
    const res = await login(request, ADMIN_EMAIL, "WrongPassword123!");
    expect(res.status()).toBe(401);
  });

  test("認証エラー: 存在しないメールで 401 が返る", async ({ request }) => {
    const res = await login(request, "nobody@mirai-dx-platform.com", "AdminPass123!");
    expect(res.status()).toBe(401);
  });

  test("認可: トークンなしで 401 が返る", async ({ request }) => {
    const res = await request.get(`${BASE}/api/v1/users`);
    expect(res.status()).toBe(401);
  });

  test("認可: JWT で users が取得できる(Neon DB 接続)", async ({ request }) => {
    const loginRes = await login(request, ADMIN_EMAIL, ADMIN_PASSWORD);
    const { access_token } = (await loginRes.json()).data;
    const res = await request.get(`${BASE}/api/v1/users`, {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    expect(res.status()).toBe(200);
    const body = await res.json();
    const users = body.data.users as Array<{ email: string; status: string }>;
    expect(users.length).toBeGreaterThanOrEqual(1);
    expect(users.some((u) => u.email === ADMIN_EMAIL)).toBe(true);
    expect(users[0].status).toBe("active");
  });

  test("認可: JWT で roles が取得できる(7ロール・Neon DB 接続)", async ({ request }) => {
    const loginRes = await login(request, ADMIN_EMAIL, ADMIN_PASSWORD);
    const { access_token } = (await loginRes.json()).data;
    const res = await request.get(
      `${BASE}/api/v1/roles?organization_id=00000000-0000-0000-0000-000000000001`,
      { headers: { Authorization: `Bearer ${access_token}` } },
    );
    expect(res.status()).toBe(200);
    const body = await res.json();
    const names = (body.data as Array<{ name: string }>).map((r) => r.name);
    expect(names).toContain("admin");
    expect(names).toContain("site_manager");
    expect(names).toContain("readonly");
  });

  test("入力検証: 不正メール形式は 422 が返る", async ({ request }) => {
    const res = await login(request, "not-an-email", ADMIN_PASSWORD);
    expect(res.status()).toBe(422);
  });
});
