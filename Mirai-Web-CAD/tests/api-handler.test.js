import test from "node:test";
import assert from "node:assert/strict";
import { handleApiRequest, resetMemoryStore } from "../src/api-handler.js";

const env = { AUTH_MODE: "demo", APP_ENV: "preview" };

test("health returns auth and database preview status", async () => {
  resetMemoryStore();
  const response = await handleApiRequest(new Request("https://example.test/api/health"), env);
  const body = await response.json();
  assert.equal(response.status, 200);
  assert.equal(body.ok, true);
  assert.equal(body.auth.mode, "demo");
  assert.equal(body.db.mode, "memory-preview");
});

test("production-like access mode fails closed without Cloudflare Access headers", async () => {
  resetMemoryStore();
  const response = await handleApiRequest(new Request("https://example.test/api/health"), {
    APP_ENV: "production",
    AUTH_MODE: "access"
  });
  const body = await response.json();
  assert.equal(response.status, 401);
  assert.equal(body.ok, false);
});

test("access mode ignores client role spoofing and uses server role mapping", async () => {
  resetMemoryStore();
  const response = await handleApiRequest(
    new Request("https://example.test/api/health", {
      headers: {
        "cf-access-jwt-assertion": "signed-test-token",
        "cf-access-authenticated-user-email": "attacker@example.com",
        "x-mirai-role": "cad_admin"
      }
    }),
    {
      APP_ENV: "production",
      AUTH_MODE: "access",
      ACCESS_ROLE_MAP: JSON.stringify({ "drafter@example.com": "drafter" }),
      ACCESS_JWT_VERIFIER: async (token) => {
        assert.equal(token, "signed-test-token");
        return { email: "drafter@example.com" };
      }
    }
  );
  const body = await response.json();
  assert.equal(response.status, 200);
  assert.equal(body.auth.role, "drafter");
});

test("access mode fails closed when JWT verifier configuration is absent", async () => {
  resetMemoryStore();
  const response = await handleApiRequest(
    new Request("https://example.test/api/health", {
      headers: { "cf-access-jwt-assertion": "unverified-token" }
    }),
    { APP_ENV: "production", AUTH_MODE: "access" }
  );
  const body = await response.json();
  assert.equal(response.status, 401);
  assert.match(body.error, /JWT/);
});

test("viewer cannot create transactions", async () => {
  resetMemoryStore();
  const response = await handleApiRequest(
    new Request("https://example.test/api/drawings/dwg_demo_001/transactions", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-demo-role": "viewer",
        "idempotency-key": "idem-viewer",
        "expected-version": "1"
      },
      body: JSON.stringify({ label: "viewer transaction", commands: [] })
    }),
    env
  );
  const body = await response.json();
  assert.equal(response.status, 403);
  assert.match(body.error, /権限/);
});

test("transaction requires idempotency and expected version gates", async () => {
  resetMemoryStore();
  const missingIdempotency = await handleApiRequest(
    new Request("https://example.test/api/drawings/dwg_demo_001/transactions", {
      method: "POST",
      headers: { "content-type": "application/json", "x-demo-role": "drafter", "expected-version": "1" },
      body: JSON.stringify({ commands: [] })
    }),
    env
  );
  assert.equal(missingIdempotency.status, 428);

  const wrongVersion = await handleApiRequest(
    new Request("https://example.test/api/drawings/dwg_demo_001/transactions", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-demo-role": "drafter",
        "idempotency-key": "idem-wrong",
        "expected-version": "99"
      },
      body: JSON.stringify({ commands: [] })
    }),
    env
  );
  assert.equal(wrongVersion.status, 409);
});

test("duplicate idempotency key cannot execute a transaction twice", async () => {
  resetMemoryStore();
  const request = () =>
    new Request("https://example.test/api/drawings/dwg_demo_001/transactions", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-demo-role": "drafter",
        "idempotency-key": "idem-duplicate",
        "expected-version": "1"
      },
      body: JSON.stringify({ label: "duplicate guard", commands: [] })
    });
  const first = await handleApiRequest(request(), env);
  const second = await handleApiRequest(request(), env);
  assert.equal(first.status, 200);
  assert.equal(second.status, 409);
  assert.match((await second.json()).error, /処理済み/);
});

test("review updates require concurrency and idempotency gates", async () => {
  resetMemoryStore();
  const missingGates = await handleApiRequest(
    new Request("https://example.test/api/drawings/dwg_demo_001/review", {
      method: "POST",
      headers: { "content-type": "application/json", "x-demo-role": "drafter" },
      body: JSON.stringify({ action: "submit" })
    }),
    env
  );
  assert.equal(missingGates.status, 428);

  const submitted = await handleApiRequest(
    new Request("https://example.test/api/drawings/dwg_demo_001/review", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-demo-role": "drafter",
        "idempotency-key": "idem-review-submit",
        "expected-version": "1"
      },
      body: JSON.stringify({ action: "submit" })
    }),
    env
  );
  assert.equal(submitted.status, 200);
  assert.equal((await submitted.json()).drawing.state, "in_review");
});

test("agent run preview then explicit approval mutates drawing", async () => {
  resetMemoryStore();
  const planResponse = await handleApiRequest(
    new Request("https://example.test/api/drawings/dwg_demo_001/agent-runs", {
      method: "POST",
      headers: { "content-type": "application/json", "x-demo-role": "drafter" },
      body: JSON.stringify({ prompt: "クレーンの重機範囲を追加" })
    }),
    env
  );
  const planBody = await planResponse.json();
  assert.equal(planResponse.status, 201);
  assert.equal(planBody.run.status, "planned");

  const before = await (await handleApiRequest(new Request("https://example.test/api/drawings/dwg_demo_001"), env)).json();
  const approveResponse = await handleApiRequest(
    new Request(`https://example.test/api/agent-runs/${planBody.run.id}/approve`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-demo-role": "drafter",
        "idempotency-key": "idem-agent",
        "expected-version": "1"
      },
      body: "{}"
    }),
    env
  );
  const approveBody = await approveResponse.json();
  assert.equal(approveResponse.status, 200);
  assert.equal(approveBody.drawing.entities.length, before.drawing.entities.length + 2);
});

test("stateless preview approval can apply proposal when run memory is not shared", async () => {
  resetMemoryStore();
  const planResponse = await handleApiRequest(
    new Request("https://example.test/api/drawings/dwg_demo_001/agent-runs", {
      method: "POST",
      headers: { "content-type": "application/json", "x-demo-role": "drafter" },
      body: JSON.stringify({ prompt: "注記追加" })
    }),
    env
  );
  const planBody = await planResponse.json();
  resetMemoryStore();

  const approveResponse = await handleApiRequest(
    new Request(`https://example.test/api/agent-runs/${planBody.run.id}/approve`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-demo-role": "drafter",
        "idempotency-key": "idem-stateless-agent",
        "expected-version": "1"
      },
      body: JSON.stringify({
        drawingId: planBody.run.drawingId,
        proposal: planBody.run.proposal
      })
    }),
    env
  );
  const approveBody = await approveResponse.json();
  assert.equal(approveResponse.status, 200);
  assert.equal(approveBody.run.createdBy, "stateless-preview");
  assert.equal(approveBody.drawing.entities.length, 11);
});
