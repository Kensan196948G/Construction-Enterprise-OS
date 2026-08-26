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
