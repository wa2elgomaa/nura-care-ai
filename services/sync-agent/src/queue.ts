import {
  closeSync, fsyncSync, mkdirSync, openSync, readdirSync, readFileSync,
  renameSync, unlinkSync, writeFileSync,
} from "node:fs";
import { join } from "node:path";
import { randomUUID } from "node:crypto";

export interface QueuedEvent {
  id: string;            // idempotency key, stays the same across retries
  type: string;
  occurred_at: string;   // original time, preserved across outages
  enqueued_at: string;
  payload: unknown;
}

export interface QueueItem { file: string; event: QueuedEvent }

/**
 * Crash-safe, dependency-free queue: one JSON file per event.
 * enqueue = write temp file + fsync + atomic rename. Ordering = file name.
 * An event is deleted only after the cloud acknowledged it.
 */
export class DiskQueue {
  private counter = 0;
  private readonly deadDir: string;

  constructor(private readonly dir: string) {
    mkdirSync(dir, { recursive: true });
    this.deadDir = join(dir, "dead");
    mkdirSync(this.deadDir, { recursive: true });
    for (const f of readdirSync(dir)) if (f.endsWith(".tmp")) unlinkSync(join(dir, f));
  }

  enqueue(type: string, payload: unknown, occurredAt?: string): QueuedEvent {
    const now = new Date().toISOString();
    const event: QueuedEvent = {
      id: randomUUID(),
      type,
      occurred_at: occurredAt ?? now,
      enqueued_at: now,
      payload,
    };
    const seq = `${Date.now().toString().padStart(15, "0")}-${String(this.counter++ % 100000).padStart(5, "0")}`;
    const name = `${seq}-${event.id}.json`;
    const tmp = join(this.dir, `${name}.tmp`);
    const fd = openSync(tmp, "w");
    try {
      writeFileSync(fd, JSON.stringify(event));
      fsyncSync(fd);
    } finally {
      closeSync(fd);
    }
    renameSync(tmp, join(this.dir, name));
    return event;
  }

  private files(): string[] {
    return readdirSync(this.dir).filter((f) => f.endsWith(".json")).sort();
  }

  peek(limit: number): QueueItem[] {
    const items: QueueItem[] = [];
    for (const file of this.files().slice(0, limit)) {
      try {
        items.push({ file, event: JSON.parse(readFileSync(join(this.dir, file), "utf8")) as QueuedEvent });
      } catch {
        renameSync(join(this.dir, file), join(this.deadDir, `${file}.corrupt`));
      }
    }
    return items;
  }

  ack(file: string): void {
    unlinkSync(join(this.dir, file));
  }

  /** Permanently rejected by the cloud (4xx): keep for inspection, stop retrying. */
  deadLetter(file: string): void {
    renameSync(join(this.dir, file), join(this.deadDir, file));
  }

  size(): number {
    return this.files().length;
  }

  deadSize(): number {
    return readdirSync(this.deadDir).length;
  }
}
