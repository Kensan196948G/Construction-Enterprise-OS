import { neon } from "@neondatabase/serverless";
import { seedDrawing } from "./cad-core.js";

const memory = {
  drawings: new Map(),
  agentRuns: new Map(),
  auditLogs: [],
  idempotencyKeys: new Set()
};

export function createDataStore(env = {}) {
  if (env.DATA_STORE) return env.DATA_STORE;
  const connectionString = env.DATABASE_URL ?? env.HYPERDRIVE?.connectionString;
  if (connectionString) return new NeonDataStore(connectionString);
  return new MemoryDataStore();
}

export function resetMemoryStoreData() {
  memory.drawings.clear();
  memory.agentRuns.clear();
  memory.auditLogs.splice(0, memory.auditLogs.length);
  memory.idempotencyKeys.clear();
  ensureMemorySeed();
}

class MemoryDataStore {
  constructor() {
    ensureMemorySeed();
  }

  async probe() {
    return { provider: "memory", mode: "memory-preview", migration: "0002_idempotency.sql" };
  }

  async getDrawing(id) {
    return clone(memory.drawings.get(id));
  }

  async saveDrawing(drawing) {
    memory.drawings.set(drawing.id, clone(drawing));
    return drawing;
  }

  async saveAgentRun(run) {
    memory.agentRuns.set(run.id, clone(run));
    return run;
  }

  async getAgentRun(id) {
    return clone(memory.agentRuns.get(id));
  }

  async appendAudit(entry) {
    memory.auditLogs.push(clone(entry));
  }

  async listAuditLogs(limit = 100) {
    return memory.auditLogs.slice(-limit).reverse().map(clone);
  }

  async claimIdempotency(key) {
    if (memory.idempotencyKeys.has(key)) return false;
    memory.idempotencyKeys.add(key);
    return true;
  }
}

class NeonDataStore {
  constructor(connectionString) {
    this.sql = neon(connectionString);
  }

  async probe() {
    const rows = await this.sql`
      select current_database() as database,
             exists (
               select 1 from information_schema.tables
               where table_schema = 'public' and table_name = 'drawing_versions'
             ) and exists (
               select 1 from information_schema.tables
               where table_schema = 'public' and table_name = 'idempotency_keys'
             ) as migrated
    `;
    return {
      provider: "neon-postgres",
      mode: "connected",
      database: rows[0].database,
      migrated: rows[0].migrated,
      migration: "0002_idempotency.sql"
    };
  }

  async getDrawing(id) {
    const rows = await this.sql`
      select d.id, d.name, d.unit, d.current_version, d.state, v.content
      from drawings d
      join drawing_versions v
        on v.drawing_id = d.id and v.version_no = d.current_version
      where d.id = ${id}
      limit 1
    `;
    if (rows.length === 0) return null;

    const row = rows[0];
    let drawing = row.content;
    if (!isCadDrawing(drawing)) {
      drawing = seedDrawing();
    }
    drawing = {
      ...drawing,
      id: row.id,
      name: row.name,
      unit: row.unit,
      version: row.current_version,
      state: row.state
    };
    if (!isCadDrawing(row.content)) await this.saveDrawing(drawing);
    return drawing;
  }

  async saveDrawing(drawing) {
    const content = JSON.stringify(drawing);
    const contentHash = drawing.commandEvents?.at(-1)?.afterHash ?? `version-${drawing.version}`;
    const versionId = `ver_${drawing.id}_${String(drawing.version).padStart(3, "0")}`;
    const actor = drawing.auditLog?.at(-1)?.actor ?? drawing.currentRole ?? "system";
    await this.sql.transaction([
      this.sql`
        insert into drawings (id, project_id, name, unit, current_version, state)
        values (${drawing.id}, 'prj_demo_road_001', ${drawing.name}, ${drawing.unit}, ${drawing.version}, ${drawing.state})
        on conflict (id) do update set
          name = excluded.name,
          unit = excluded.unit,
          current_version = excluded.current_version,
          state = excluded.state,
          updated_at = now()
      `,
      this.sql`
        insert into drawing_versions (id, drawing_id, version_no, state, content, content_hash, created_by)
        values (${versionId}, ${drawing.id}, ${drawing.version}, ${drawing.state}, ${content}::jsonb, ${contentHash}, ${actor})
        on conflict (drawing_id, version_no) do update set
          state = excluded.state,
          content = excluded.content,
          content_hash = excluded.content_hash
      `
    ]);
    return drawing;
  }

  async saveAgentRun(run) {
    await this.sql`
      insert into agent_runs (
        id, drawing_version_id, status, prompt, skill_id, skill_version,
        proposal, risk, created_by, created_at
      )
      select ${run.id}, v.id, ${run.status}, ${run.prompt},
             ${run.proposal.skill?.id ?? null}, ${run.proposal.skill?.version ?? null},
             ${JSON.stringify(run.proposal)}::jsonb, ${run.proposal.risk ?? "preview"},
             ${run.createdBy}, ${run.createdAt}
      from drawing_versions v
      where v.drawing_id = ${run.drawingId}
      order by v.version_no desc
      limit 1
      on conflict (id) do update set
        status = excluded.status,
        proposal = excluded.proposal
    `;
    return run;
  }

  async getAgentRun(id) {
    const rows = await this.sql`
      select a.id, v.drawing_id, a.status, a.prompt, a.proposal,
             a.created_by, a.created_at
      from agent_runs a
      join drawing_versions v on v.id = a.drawing_version_id
      where a.id = ${id}
      limit 1
    `;
    if (rows.length === 0) return null;
    const row = rows[0];
    return {
      id: row.id,
      drawingId: row.drawing_id,
      status: row.status,
      prompt: row.prompt,
      proposal: row.proposal,
      createdBy: row.created_by,
      createdAt: new Date(row.created_at).toISOString()
    };
  }

  async appendAudit(entry) {
    await this.sql`
      insert into audit_logs (id, actor_id, action, target_type, target_id, detail, created_at)
      values (${entry.id}, ${entry.actorId}, ${entry.action}, ${entry.targetType},
              ${entry.targetId}, ${JSON.stringify({ role: entry.role, ...entry.detail })}::jsonb,
              ${entry.createdAt})
      on conflict (id) do nothing
    `;
  }

  async listAuditLogs(limit = 100) {
    const safeLimit = Math.max(1, Math.min(100, Number(limit) || 100));
    const rows = await this.sql`
      select id, actor_id, action, target_type, target_id, detail, created_at
      from audit_logs
      order by created_at desc
      limit ${safeLimit}
    `;
    return rows.map((row) => ({
      id: row.id,
      actorId: row.actor_id,
      role: row.detail?.role,
      action: row.action,
      targetType: row.target_type,
      targetId: row.target_id,
      detail: row.detail,
      createdAt: new Date(row.created_at).toISOString()
    }));
  }

  async claimIdempotency(key, actorId, route) {
    const rows = await this.sql`
      insert into idempotency_keys (key, actor_id, route)
      values (${key}, ${actorId}, ${route})
      on conflict (key) do nothing
      returning key
    `;
    return rows.length === 1;
  }
}

function ensureMemorySeed() {
  if (!memory.drawings.has("dwg_demo_001")) memory.drawings.set("dwg_demo_001", seedDrawing());
}

function isCadDrawing(value) {
  return Boolean(
    value &&
      Array.isArray(value.layers) &&
      value.layers.every((layer) => typeof layer === "object" && typeof layer.id === "string") &&
      Array.isArray(value.entities) &&
      Array.isArray(value.commandEvents) &&
      Array.isArray(value.auditLog)
  );
}

function clone(value) {
  return value == null ? value : structuredClone(value);
}
