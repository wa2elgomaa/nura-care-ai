import { createServer } from "node:http";
import { join } from "node:path";
import { config } from "./config.js";
import { log } from "./log.js";
import { DiskQueue } from "./queue.js";
import { DeviceIdentity } from "./identity.js";
import { CloudClient } from "./cloud.js";
import { AgentState, checkForUpdates, loadPublicKey } from "./updates.js";

const queue = new DiskQueue(join(config.stateDir, "queue"));
const identity = DeviceIdentity.loadOrCreate(config.stateDir);
const state = new AgentState(join(config.stateDir, "state.json"));
const client = new CloudClient(config.cloudUrl, identity, config.claimCode, config.requestTimeoutMs);
const publicKey = loadPublicKey(config.updatePublicKeyFile);

const status = {
  online: false,
  last_success_at: null as string | null,
  last_error: null as string | null,
  started_at: new Date().toISOString(),
};

function markOnline(): void {
  status.online = true;
  status.last_success_at = new Date().toISOString();
  status.last_error = null;
}
function markOffline(e: unknown): void {
  status.online = false;
  status.last_error = String(e);
}

// ---- flush: oldest first, delete only after the cloud acknowledged ----------
async function flush(): Promise<void> {
  for (const { file, event } of queue.peek(50)) {
    const r = await client.authedPost("/v1/events", event);
    if (r.status === 200) {
      queue.ack(file);                       // accepted, or already seen (idempotent)
    } else if (r.status >= 400 && r.status < 500 && r.status !== 401 && r.status !== 429) {
      log("error", "event permanently rejected", { id: event.id, status: r.status });
      queue.deadLetter(file);                // never block the queue on a bad event
    } else {
      throw new Error(`cloud returned HTTP ${r.status}`);
    }
  }
}

let backoff = config.flushIntervalMs;
async function flushLoop(): Promise<void> {
  try {
    await flush();
    markOnline();
    backoff = config.flushIntervalMs;
  } catch (e) {
    markOffline(e);
    backoff = Math.min(backoff * 2, config.maxBackoffMs);
    log("warn", "cloud unreachable, will retry", { queued: queue.size(), retry_in_ms: backoff });
  }
  setTimeout(flushLoop, status.online ? config.flushIntervalMs : backoff);
}

async function heartbeatLoop(): Promise<void> {
  try {
    const r = await client.authedPost("/v1/heartbeat", {
      queue_depth: queue.size(),
      installed: state.data.installed,
      agent_version: config.agentVersion,
    });
    if (r.status === 200) markOnline();
  } catch (e) {
    markOffline(e);
  }
  setTimeout(heartbeatLoop, config.heartbeatIntervalMs);
}

async function updateLoop(): Promise<void> {
  try {
    await checkForUpdates({ client, state, publicKey, names: config.updateNames, queue, stateDir: config.stateDir });
  } catch (e) {
    log("warn", "update check failed", { error: String(e) });
  }
  setTimeout(updateLoop, config.updateCheckIntervalMs);
}

// ---- local ingest API for other services on the box (core_net only) ---------
const server = createServer((req, res) => {
  const send = (code: number, body: unknown) => {
    res.writeHead(code, { "content-type": "application/json" });
    res.end(JSON.stringify(body));
  };

  if (req.method === "GET" && req.url === "/healthz") return send(200, { ok: true });
  if (req.method === "GET" && req.url === "/status") {
    return send(200, {
      ...status,
      device_id: identity.deviceId ?? null,
      queued: queue.size(),
      dead_lettered: queue.deadSize(),
      installed_updates: state.data.installed,
      updates_enabled: publicKey !== null,
    });
  }
  if (req.method === "POST" && req.url === "/enqueue") {
    const chunks: Buffer[] = [];
    let size = 0;
    req.on("data", (c: Buffer) => {
      size += c.length;
      if (size > 64 * 1024) { send(413, { error: "too large" }); req.destroy(); return; }
      chunks.push(c);
    });
    req.on("end", () => {
      if (res.writableEnded) return;
      try {
        const body = JSON.parse(Buffer.concat(chunks).toString("utf8")) as {
          type?: unknown; payload?: unknown; occurred_at?: unknown;
        };
        if (typeof body.type !== "string" || !/^[a-z0-9_.-]{1,64}$/.test(body.type)) {
          return send(400, { error: "type must match ^[a-z0-9_.-]{1,64}$" });
        }
        if (body.occurred_at !== undefined &&
            (typeof body.occurred_at !== "string" || Number.isNaN(Date.parse(body.occurred_at)))) {
          return send(400, { error: "occurred_at must be an ISO timestamp" });
        }
        const ev = queue.enqueue(body.type, body.payload ?? null, body.occurred_at as string | undefined);
        send(202, { id: ev.id, queued: queue.size() });
      } catch {
        send(400, { error: "invalid JSON" });
      }
    });
    return;
  }
  send(404, { error: "not found" });
});

server.listen(config.listenPort, "0.0.0.0", () => {
  log("info", "sync-agent started", {
    port: config.listenPort, cloud: config.cloudUrl,
    queued: queue.size(), updates_enabled: publicKey !== null,
  });
});

void flushLoop();
void heartbeatLoop();
void updateLoop();

for (const sig of ["SIGINT", "SIGTERM"] as const) {
  process.on(sig, () => { log("info", "shutting down", { signal: sig }); server.close(() => process.exit(0)); });
}
