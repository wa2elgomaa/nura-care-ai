import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { DiskQueue } from "./queue.js";

function withQueue(fn: (q: DiskQueue, dir: string) => void) {
  const dir = mkdtempSync(join(tmpdir(), "nura-q-"));
  try { fn(new DiskQueue(dir), dir); } finally { rmSync(dir, { recursive: true, force: true }); }
}

test("keeps order and original timestamps", () => {
  withQueue((q) => {
    q.enqueue("a", { n: 1 }, "2026-01-01T00:00:00.000Z");
    q.enqueue("a", { n: 2 }, "2026-01-01T00:00:01.000Z");
    q.enqueue("a", { n: 3 });
    const items = q.peek(10);
    assert.deepEqual(items.map((i) => (i.event.payload as { n: number }).n), [1, 2, 3]);
    assert.equal(items[0]?.event.occurred_at, "2026-01-01T00:00:00.000Z");
  });
});

test("survives restart: a new instance sees the same events", () => {
  withQueue((q, dir) => {
    q.enqueue("a", { n: 1 });
    assert.equal(new DiskQueue(dir).size(), 1);
  });
});

test("ack removes, deadLetter stops retrying", () => {
  withQueue((q) => {
    q.enqueue("a", 1);
    q.enqueue("a", 2);
    const [first, second] = q.peek(2);
    q.ack(first!.file);
    q.deadLetter(second!.file);
    assert.equal(q.size(), 0);
    assert.equal(q.deadSize(), 1);
  });
});
