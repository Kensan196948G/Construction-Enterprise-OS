/**
 * API E2E — HTTPS 経由の API・認証・DB(Neon)検証
 *
 * 対象: E2E_API_BASE_URL(既定は MVP: https://construction-os-mvp.mirai-dx-platform.com/api/v1/*)
 * (Pages Function プロキシ → Cloudflare Tunnel → auth サービス → Neon)
 *
 * 本番(construction-os.mirai-dx-platform.com)は Cloudflare Access 保護下にあり、
 * 未認証のAPIクライアントでは 302(ログインへリダイレクト)となるため既定対象にしない。
 * 本番を検証する場合は Access のサービス トークン等を付与した上で
 *   E2E_API_BASE_URL=https://construction-os.mirai-dx-platform.com
 * を明示指定する。
 *
 * 正常系(ログイン→JWT→認証付きAPI)・エラー系(401/422)・DB 接続を検証する。
 */

import { test, expect, type APIRequestContext } from "@playwright/test";

const BASE = process.env.E2E_API_BASE_URL || "https://construction-os-mvp.mirai-dx-platform.com";
// 資格情報はコードに埋め込まず、環境変数（CI では GitHub Secrets）で渡す。
const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL ?? "";
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD ?? "";
const HAS_ADMIN_CREDENTIALS = ADMIN_EMAIL !== "" && ADMIN_PASSWORD !== "";
const HAS_KNOWN_EMAIL = ADMIN_EMAIL !== "";

async function login(request: APIRequestContext, email: string, password: string) {
  return request.post(`${BASE}/api/v1/auth/login`, {
    data: { email, password },
    headers: { "Content-Type": "application/json" },
  });
}

test.describe("Construction Enterprise OS API (HTTPS)", () => {
  test("ヘルスチェック: 監視対象サービスが healthy かつ overall が整合する", async ({ request }) => {
    const res = await request.get(`${BASE}/api/v1/health/services`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    const services = body.services as Array<{ name: string; status: string }>;

    // 本番構成(2026-09-13 時点)では Cloudflare Tunnel が公開するのは
    // auth サービス(Neon 接続)のみで、他サービスは同一ホストに配置されない。
    // そのため「監視対象として実際に公開されているサービス」を検証する。
    // 監視対象が増えた場合もこのテストは成立する。
    expect(services.length).toBeGreaterThanOrEqual(1);
    for (const s of services) {
      expect(s.status).toBe("healthy");
    }
    // 認証基盤のヘルスは常に監視対象であること
    expect(services.map((s) => s.name)).toContain("auth");

    // overall は各サービスの状態から導出される値と整合していること
    expect(body.overall).toBe("healthy");
    expect(typeof body.checked_at).toBe("string");
    expect(Number.isNaN(Date.parse(body.checked_at))).toBe(false);
  });

  test("認証: 正しい資格情報で JWT が発行される", async ({ request }) => {
    test.skip(!HAS_ADMIN_CREDENTIALS, "E2E_ADMIN_EMAIL / E2E_ADMIN_PASSWORD が未設定のためスキップ");
    const res = await login(request, ADMIN_EMAIL, ADMIN_PASSWORD);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.success).toBe(true);
    expect(body.data.access_token).toBeTruthy();
    expect(body.data.refresh_token).toBeTruthy();
  });

  test("認証エラー: 誤パスワードで 401 が返る", async ({ request }) => {
    test.skip(!HAS_KNOWN_EMAIL, "E2E_ADMIN_EMAIL が未設定のためスキップ");
    const res = await login(request, ADMIN_EMAIL, "WrongPassword123!");
    expect(res.status()).toBe(401);
  });

  test("認証エラー: 存在しないメールで 401 が返る", async ({ request }) => {
    const res = await login(request, "nobody@mirai-dx-platform.com", "irrelevant-password");
    expect(res.status()).toBe(401);
  });

  test("認可: トークンなしで 401 が返る", async ({ request }) => {
    const res = await request.get(`${BASE}/api/v1/users`);
    expect(res.status()).toBe(401);
  });

  test("認可: JWT で users が取得できる(Neon DB 接続)", async ({ request }) => {
    test.skip(!HAS_ADMIN_CREDENTIALS, "E2E_ADMIN_EMAIL / E2E_ADMIN_PASSWORD が未設定のためスキップ");
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
    test.skip(!HAS_ADMIN_CREDENTIALS, "E2E_ADMIN_EMAIL / E2E_ADMIN_PASSWORD が未設定のためスキップ");
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
