import {
  ROLE_POLICIES,
  applyTransaction,
  approveDrawing,
  buildAiProposal,
  createNewVersion,
  proposalToTransaction,
  seedDrawing,
  submitForReview,
  validateDrawing
} from "./cad-core.js";

const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
  "referrer-policy": "no-referrer"
};

const memory = {
  drawings: new Map(),
  agentRuns: new Map(),
  auditLogs: []
};

export async function handleApiRequest(request, env = {}) {
  ensureSeed(memory);
  const url = new URL(request.url);
  const startedAt = Date.now();
  const route = normalizeRoute(url.pathname);
  const requestId = request.headers.get("x-request-id") ?? `req_${Date.now().toString(36)}`;

  if (request.method === "OPTIONS") {
    return json({ ok: true }, 204, corsHeaders(env, requestId));
  }

  try {
    const actor = resolveActor(request, env);
    if (!actor.ok) return json({ ok: false, error: actor.error }, 401, corsHeaders(env, requestId));

    if (request.method === "GET" && route === "/health") {
      return json(
        {
          ok: true,
          service: "mirai-web-cad-api",
          auth: { mode: authMode(env), actor: actor.actor.id, role: actor.actor.role },
          db: databaseStatus(env),
          durationMs: Date.now() - startedAt
        },
        200,
        corsHeaders(env, requestId)
      );
    }

    if (request.method === "GET" && route === "/drawings/demo") {
      return json({ ok: true, drawing: getDrawing("dwg_demo_001") }, 200, corsHeaders(env, requestId));
    }

    if (request.method === "POST" && route === "/drawings") {
      authorize(actor.actor, "canEdit");
      const body = await readJson(request);
      const drawing = seedDrawing();
      drawing.id = body.id ?? `dwg_${cryptoSafeId()}`;
      drawing.name = body.name ?? "新規図面";
      drawing.currentRole = actor.actor.role;
      memory.drawings.set(drawing.id, drawing);
      audit(actor.actor, "drawing.created", "drawing", drawing.id, { name: drawing.name });
      return json({ ok: true, drawing }, 201, corsHeaders(env, requestId));
    }

    const drawingMatch = route.match(/^\/drawings\/([^/]+)$/);
    if (request.method === "GET" && drawingMatch) {
      return json({ ok: true, drawing: getDrawing(drawingMatch[1]) }, 200, corsHeaders(env, requestId));
    }

    const transactionMatch = route.match(/^\/drawings\/([^/]+)\/transactions$/);
    if (request.method === "POST" && transactionMatch) {
      authorize(actor.actor, "canEdit");
      const drawing = withActor(getDrawing(transactionMatch[1]), actor.actor);
      const body = await readJson(request);
      requireIdempotency(request);
      requireExpectedVersion(request, drawing);
      const result = applyTransaction(drawing, {
        source: "user",
        actor: actor.actor.id,
        label: body.label ?? "API transaction",
        commands: body.commands ?? []
      });
      if (!result.ok) return json({ ok: false, error: result.error }, 409, corsHeaders(env, requestId));
      memory.drawings.set(drawing.id, result.drawing);
      audit(actor.actor, "drawing.transaction", "drawing", drawing.id, { label: body.label });
      return json({ ok: true, drawing: result.drawing, warnings: result.warnings }, 200, corsHeaders(env, requestId));
    }

    const agentMatch = route.match(/^\/drawings\/([^/]+)\/agent-runs$/);
    if (request.method === "POST" && agentMatch) {
      authorize(actor.actor, "canRunAi");
      const drawing = withActor(getDrawing(agentMatch[1]), actor.actor);
      const body = await readJson(request);
      const proposal = buildAiProposal(drawing, body.prompt ?? "");
      const run = {
        id: `run_${cryptoSafeId()}`,
        drawingId: drawing.id,
        status: proposal.status,
        prompt: body.prompt ?? "",
        proposal,
        createdBy: actor.actor.id,
        createdAt: new Date().toISOString()
      };
      memory.agentRuns.set(run.id, run);
      audit(actor.actor, "agent.planned", "agent_run", run.id, { status: run.status });
      return json({ ok: true, run }, proposal.status === "planned" ? 201 : 202, corsHeaders(env, requestId));
    }

    const approveAgentMatch = route.match(/^\/agent-runs\/([^/]+)\/approve$/);
    if (request.method === "POST" && approveAgentMatch) {
      authorize(actor.actor, "canEdit");
      requireIdempotency(request);
      const body = await readJson(request);
      const run = resolveAgentRunForApproval(approveAgentMatch[1], body);
      if (run.proposal.status !== "planned") {
        return json({ ok: false, error: "適用可能なAI提案ではありません。" }, 409, corsHeaders(env, requestId));
      }
      const drawing = withActor(getDrawing(run.drawingId), actor.actor);
      requireExpectedVersion(request, drawing);
      const result = applyTransaction(drawing, proposalToTransaction(run.proposal, actor.actor.id));
      if (!result.ok) return json({ ok: false, error: result.error }, 409, corsHeaders(env, requestId));
      run.status = "completed";
      memory.drawings.set(drawing.id, result.drawing);
      audit(actor.actor, "agent.approved", "drawing", drawing.id, { runId: run.id });
      return json({ ok: true, drawing: result.drawing, run }, 200, corsHeaders(env, requestId));
    }

    const reviewMatch = route.match(/^\/drawings\/([^/]+)\/review$/);
    if (request.method === "POST" && reviewMatch) {
      const drawing = withActor(getDrawing(reviewMatch[1]), actor.actor);
      const body = await readJson(request);
      if (body.action === "submit") {
        authorize(actor.actor, "canEdit");
        const next = submitForReview(drawing, actor.actor.id);
        memory.drawings.set(drawing.id, next);
        audit(actor.actor, "review.submitted", "drawing", drawing.id, {});
        return json({ ok: true, drawing: next }, 200, corsHeaders(env, requestId));
      }
      if (body.action === "approve") {
        authorize(actor.actor, "canApprove");
        const result = approveDrawing(drawing, actor.actor.id);
        if (!result.ok) return json({ ok: false, error: result.error, issues: validateDrawing(drawing) }, 409, corsHeaders(env, requestId));
        memory.drawings.set(drawing.id, result.drawing);
        audit(actor.actor, "review.approved", "drawing", drawing.id, {});
        return json({ ok: true, drawing: result.drawing }, 200, corsHeaders(env, requestId));
      }
      if (body.action === "new_version") {
        authorize(actor.actor, "canApprove");
        const next = createNewVersion(drawing, actor.actor.id);
        memory.drawings.set(drawing.id, next);
        audit(actor.actor, "drawing.version.created", "drawing", drawing.id, {});
        return json({ ok: true, drawing: next }, 200, corsHeaders(env, requestId));
      }
      return json({ ok: false, error: "review actionが不正です。" }, 400, corsHeaders(env, requestId));
    }

    if (request.method === "GET" && route === "/audit-logs") {
      authorize(actor.actor, "canApprove");
      return json({ ok: true, auditLogs: memory.auditLogs.slice(-100).reverse() }, 200, corsHeaders(env, requestId));
    }

    return json({ ok: false, error: "not found" }, 404, corsHeaders(env, requestId));
  } catch (error) {
    const status = error.status ?? 500;
    return json({ ok: false, error: error.message ?? "internal error" }, status, corsHeaders(env, requestId));
  }
}

export function resetMemoryStore() {
  memory.drawings.clear();
  memory.agentRuns.clear();
  memory.auditLogs.splice(0, memory.auditLogs.length);
  ensureSeed(memory);
}

function resolveActor(request, env) {
  const mode = authMode(env);
  if (mode === "demo") {
    const role = request.headers.get("x-demo-role") ?? "drafter";
    if (!ROLE_POLICIES[role]) return { ok: false, error: "不正なデモ権限です。" };
    return { ok: true, actor: { id: request.headers.get("x-demo-actor") ?? "demo@example.com", role } };
  }

  const jwtEmail = request.headers.get("cf-access-authenticated-user-email");
  const role = request.headers.get("x-mirai-role");
  if (!jwtEmail || !role || !ROLE_POLICIES[role]) {
    return { ok: false, error: "Cloudflare Access認証情報を確認できません。" };
  }
  return { ok: true, actor: { id: jwtEmail, role } };
}

function authMode(env) {
  if (env.AUTH_MODE) return env.AUTH_MODE;
  return env.APP_ENV === "production" ? "access" : "demo";
}

function databaseStatus(env) {
  return {
    provider: "neon-postgres",
    configured: Boolean(env.DATABASE_URL || env.HYPERDRIVE),
    mode: env.DATABASE_URL || env.HYPERDRIVE ? "configured-not-probed" : "memory-preview",
    migration: "0001_initial.sql"
  };
}

function authorize(actor, capability) {
  const policy = ROLE_POLICIES[actor.role] ?? ROLE_POLICIES.viewer;
  if (!policy[capability]) {
    const error = new Error(`${policy.label}には${capability}権限がありません。`);
    error.status = 403;
    throw error;
  }
}

function getDrawing(id) {
  const drawing = memory.drawings.get(id);
  if (!drawing) {
    const error = new Error(`図面が見つかりません: ${id}`);
    error.status = 404;
    throw error;
  }
  return drawing;
}

function getAgentRun(id) {
  const run = memory.agentRuns.get(id);
  if (!run) {
    const error = new Error(`Agent Runが見つかりません: ${id}`);
    error.status = 404;
    throw error;
  }
  return run;
}

function resolveAgentRunForApproval(id, body) {
  const run = memory.agentRuns.get(id);
  if (run) return run;
  if (body?.drawingId && body?.proposal?.status === "planned" && Array.isArray(body.proposal.commands)) {
    return {
      id,
      drawingId: body.drawingId,
      status: "planned",
      prompt: body.prompt ?? "",
      proposal: body.proposal,
      createdBy: "stateless-preview",
      createdAt: new Date().toISOString()
    };
  }
  return getAgentRun(id);
}

function withActor(drawing, actor) {
  return { ...drawing, currentRole: actor.role };
}

function requireIdempotency(request) {
  if (!request.headers.get("idempotency-key")) {
    const error = new Error("Idempotency-Keyが必要です。");
    error.status = 428;
    throw error;
  }
}

function requireExpectedVersion(request, drawing) {
  const expected = Number(request.headers.get("expected-version"));
  if (!Number.isFinite(expected)) {
    const error = new Error("expected-versionが必要です。");
    error.status = 428;
    throw error;
  }
  if (expected !== drawing.version) {
    const error = new Error(`版が競合しています。expected=${expected}, actual=${drawing.version}`);
    error.status = 409;
    throw error;
  }
}

async function readJson(request) {
  if (!request.body) return {};
  const text = await request.text();
  if (!text.trim()) return {};
  try {
    return JSON.parse(text);
  } catch {
    const error = new Error("JSON本文が不正です。");
    error.status = 400;
    throw error;
  }
}

function normalizeRoute(pathname) {
  return pathname.replace(/^\/api\/v1/, "").replace(/^\/api/, "") || "/";
}

function json(body, status = 200, headers = {}) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: { ...JSON_HEADERS, ...headers }
  });
}

function corsHeaders(env, requestId) {
  return {
    "access-control-allow-origin": env.CORS_ORIGIN ?? "*",
    "access-control-allow-methods": "GET,POST,OPTIONS",
    "access-control-allow-headers": "content-type,idempotency-key,expected-version,x-demo-role,x-demo-actor,x-request-id",
    "x-request-id": requestId
  };
}

function ensureSeed(store) {
  if (!store.drawings.has("dwg_demo_001")) {
    store.drawings.set("dwg_demo_001", seedDrawing());
  }
}

function audit(actor, action, targetType, targetId, detail) {
  memory.auditLogs.push({
    id: `audit_${cryptoSafeId()}`,
    actorId: actor.id,
    role: actor.role,
    action,
    targetType,
    targetId,
    detail,
    createdAt: new Date().toISOString()
  });
}

function cryptoSafeId() {
  if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID().slice(0, 12);
  return `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
}
