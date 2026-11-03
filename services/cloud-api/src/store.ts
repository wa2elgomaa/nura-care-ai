import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import { join } from "node:path";

export interface Device {
  device_id: string;
  site_id: string;
  public_key_pem: string;
  enrolled_at: string;
  last_seen_at?: string;
  last_queue_depth?: number;
  agent_version?: string;
  installed?: Record<string, number>;
}

export interface StoredEvent {
  id: string;
  type: string;
  occurred_at: string;
  payload: unknown;
  device_id: string;
  site_id: string;
  received_at: string;
}

interface State {
  devices: Record<string, Device>;
  events: StoredEvent[];
  seen: Record<string, string>;
}

const MAX_EVENTS = 2000;
const MAX_SEEN = 20000;

/** File-backed state for local development. Replace with Postgres (cloud-db) next. */
export class Store {
  private state: State;
  private readonly file: string;

  constructor(readonly dataDir: string) {
    mkdirSync(dataDir, { recursive: true });
    this.file = join(dataDir, "state.json");
    this.state = existsSync(this.file)
      ? (JSON.parse(readFileSync(this.file, "utf8")) as State)
      : { devices: {}, events: [], seen: {} };
  }

  private save(): void {
    const tmp = `${this.file}.tmp`;
    writeFileSync(tmp, JSON.stringify(this.state));
    renameSync(tmp, this.file);
  }

  getDevice(id: string): Device | undefined {
    return this.state.devices[id];
  }

  upsertDevice(d: Device): void {
    this.state.devices[d.device_id] = d;
    this.save();
  }

  touchDevice(id: string, patch: Partial<Device>): void {
    const d = this.state.devices[id];
    if (!d) return;
    Object.assign(d, patch, { last_seen_at: new Date().toISOString() });
    this.save();
  }

  /** Returns false if the idempotency key was already seen. */
  addEvent(ev: StoredEvent): boolean {
    if (this.state.seen[ev.id]) return false;
    this.state.seen[ev.id] = ev.received_at;
    const keys = Object.keys(this.state.seen);
    if (keys.length > MAX_SEEN) for (const k of keys.slice(0, keys.length - MAX_SEEN)) delete this.state.seen[k];
    this.state.events.push(ev);
    if (this.state.events.length > MAX_EVENTS) this.state.events.splice(0, this.state.events.length - MAX_EVENTS);
    this.save();
    return true;
  }

  listEvents(limit: number): StoredEvent[] {
    return this.state.events.slice(-limit);
  }

  listDevices(): Array<Device & { seconds_since_seen: number | null }> {
    return Object.values(this.state.devices).map((d) => ({
      ...d,
      seconds_since_seen: d.last_seen_at ? Math.round((Date.now() - Date.parse(d.last_seen_at)) / 1000) : null,
    }));
  }
}
