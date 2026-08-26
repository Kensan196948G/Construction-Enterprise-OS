import test from "node:test";
import assert from "node:assert/strict";
import { applyTransaction, createDrawing, line, measurements } from "../src/cad-core.js";

test("10,000 entities remain processable by the deterministic CAD core", { timeout: 15_000 }, () => {
  const drawing = createDrawing({ id: "dwg_performance", currentRole: "drafter" });
  const commands = Array.from({ length: 10_000 }, (_, index) => ({
    op: "add",
    entity: line("layer-structure", [index, 0], [index, 100], { id: `perf_${index}` })
  }));

  const startedAt = performance.now();
  const result = applyTransaction(drawing, {
    source: "system",
    actor: "performance-test",
    label: "10k entity baseline",
    commands
  });
  assert.equal(result.ok, true);
  assert.equal(result.drawing.entities.length, 10_000);
  assert.equal(measurements(result.drawing).entityCount, 10_000);
  assert.ok(performance.now() - startedAt < 5_000, "10k CAD core processing exceeded 5 seconds");
});
