import {
  createHash, createPublicKey, randomBytes, timingSafeEqual, verify, type KeyObject,
} from "node:crypto";
import {
  createServer, type IncomingMessage, type Server, type ServerResponse,
} from "node:http";
import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { Store } from "./store.js";
import { TokenService } from "./tokens.js";

export interface ServerConfig {
  port: number;
  dataDir: string;
  claimCodes: Map<string, string>;        // claim code -> site id
  adminToken: string;
  tokenSecret: Buffer;
  tokenTtlSeconds: number;
  updatePublicKey: KeyObject | null;      // public key only: the cloud never holds the signing key
}

const NAME_RE = /^[a-z0-9-]{1,40}$/;
const TYPE_RE = /^[a-z0-9_.-]{1,64}$/;

class HttpError extends Error {
  constructor(readonly status: number, message: string) { super(message); }
}

function readBody(req: IncomingMessage, limit: number): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    let size = 0;
    req.on("data", (c: Buffer) => {
      size += c.length;
      if (size > limit) { reject(new HttpError(413, "body too large")); req.destroy(); return; }
      chunks.push(c);
    });
    req.on("end", () => resolve(Buffer.concat(chunks)));
    req.on("error", reject);
  });
}

async function readJson<T>(req: IncomingMessage, limit = 64 * 1024): Promise<T> {
  try {
    return JSON.parse((await readBody(req, limit)).toString("utf8")) as T;
  } catch (e) {
    if (e instanceof HttpError) throw e;
    throw new HttpError(400, "invalid JSON");
  }
}

function send(res: ServerResponse, status: number, body: unknown, type = "application/json"): void {
  const data = Buffer.isBuffer(body) ? body : Buffer.from(typeof body === "string" ? body : JSON.stringify(body));
  res.writeHead(status, { "content-type": type, "content-length": data.length });
  res.end(data);
}

const safeEqual = (a: string, b: string) => {
  const x = Buffer.from(a), y = Buffer.from(b);
  return x.length === y.length && timingSafeEqual(x, y);
};

const sha256 = (b: Buffer) => createHash("sha256").update(b).digest("hex");

function latestVersion(dir: string): number | null {
  if (!existsSync(dir)) return null;
  const vs = readdirSync(dir).filter((d) => /^\d+$/.test(d)).map(Number);
  return vs.length ? Math.max(...vs) : null;
}

export function createApp(cfg: ServerConfig): { server: Server; store: Store } {
  const store = new Store(cfg.dataDir);
  const tokens = new TokenService(cfg.tokenSecret, cfg.tokenTtlSeconds);
  const challenges = new Map<string, { device_id: string; exp: number }>();
  const updatesDir = join(cfg.dataDir, "updates");
  mkdirSync(updatesDir, { recursive: true });

  const deviceAuth = (req: IncomingMessage) => {
    const h = req.headers.authorization ?? "";
    const p = h.startsWith("Bearer ") ? tokens.verify(h.slice(7)) : null;
    if (!p) throw new HttpError(401, "invalid or expired token");
    return p;
  };
  const adminAuth = (req: IncomingMessage) => {
    const t = req.headers["x-admin-token"];
    if (typeof t !== "string" || !safeEqual(t, cfg.adminToken)) throw new HttpError(401, "admin token required");
  };

  async function route(req: IncomingMessage, res: ServerResponse): Promise<void> {
    const url = new URL(req.url ?? "/", "http://x");
    const m = req.method ?? "GET";
    const p = url.pathname;

    if (m === "GET" && p === "/healthz") return send(res, 200, { ok: true });

    // ---- device enrollment and authentication ------------------------------
    if (m === "POST" && p === "/v1/enroll") {
      const b = await readJson<{ claim_code?: string; public_key_pem?: string }>(req);
      const site = typeof b.claim_code === "string" ? cfg.claimCodes.get(b.claim_code) : undefined;
      if (!site) throw new HttpError(401, "unknown claim code");
      let pem: string;
      try {
        const key = createPublicKey(String(b.public_key_pem));
        if (key.asymmetricKeyType !== "ed25519") throw new Error("not ed25519");
        pem = key.export({ type: "spki", format: "pem" }).toString();
      } catch {
        throw new HttpError(400, "public_key_pem must be an Ed25519 public key");
      }
      const device_id = `dev_${createHash("sha256").update(pem).digest("hex").slice(0, 16)}`;
      const existing = store.getDevice(device_id);
      store.upsertDevice({
        device_id, site_id: site, public_key_pem: pem,
        enrolled_at: existing?.enrolled_at ?? new Date().toISOString(),
        ...(existing ?? {}),
      });
      return send(res, 200, { device_id, site_id: site });
    }

    if (m === "POST" && p === "/v1/auth/challenge") {
      const b = await readJson<{ device_id?: string }>(req);
      if (!b.device_id || !store.getDevice(b.device_id)) throw new HttpError(404, "unknown device");
      const nonce = randomBytes(32).toString("hex");
      challenges.set(nonce, { device_id: b.device_id, exp: Date.now() + 60_000 });
      for (const [k, v] of challenges) if (v.exp < Date.now()) challenges.delete(k);
      return send(res, 200, { nonce, expires_in: 60 });
    }

    if (m === "POST" && p === "/v1/auth/token") {
      const b = await readJson<{ device_id?: string; nonce?: string; signature?: string }>(req);
      const ch = b.nonce ? challenges.get(b.nonce) : undefined;
      const dev = b.device_id ? store.getDevice(b.device_id) : undefined;
      if (!ch || !dev || ch.device_id !== dev.device_id || ch.exp < Date.now()) {
        throw new HttpError(401, "invalid challenge");
      }
      challenges.delete(b.nonce as string);            // one-time use
      let ok = false;
      try {
        ok = verify(
          null,
          Buffer.from(`nura-auth-v1:${dev.device_id}:${b.nonce}`),
          createPublicKey(dev.public_key_pem),
          Buffer.from(String(b.signature), "base64"),
        );
      } catch { /* invalid */ }
      if (!ok) throw new HttpError(401, "bad signature");
      const t = tokens.issue(dev.device_id, dev.site_id);
      return send(res, 200, { access_token: t.token, expires_in: t.expires_in });
    }

    // ---- device-authenticated ingest ---------------------------------------
    if (m === "POST" && p === "/v1/events") {
      const who = deviceAuth(req);
      const b = await readJson<{ id?: string; type?: string; occurred_at?: string; payload?: unknown }>(req);
      if (typeof b.id !== "string" || !/^[A-Za-z0-9-]{8,64}$/.test(b.id)) throw new HttpError(400, "invalid id");
      if (typeof b.type !== "string" || !TYPE_RE.test(b.type)) throw new HttpError(400, "invalid type");
      if (typeof b.occurred_at !== "string" || Number.isNaN(Date.parse(b.occurred_at))) {
        throw new HttpError(400, "invalid occurred_at");
      }
      const fresh = store.addEvent({
        id: b.id, type: b.type, occurred_at: b.occurred_at, payload: b.payload ?? null,
        device_id: who.sub, site_id: who.site, received_at: new Date().toISOString(),
      });
      return send(res, 200, { ok: true, duplicate: !fresh });
    }

    if (m === "POST" && p === "/v1/heartbeat") {
      const who = deviceAuth(req);
      const b = await readJson<{ queue_depth?: number; installed?: Record<string, number>; agent_version?: string }>(req);
      store.touchDevice(who.sub, {
        ...(typeof b.queue_depth === "number" ? { last_queue_depth: b.queue_depth } : {}),
        ...(b.installed ? { installed: b.installed } : {}),
        ...(typeof b.agent_version === "string" ? { agent_version: b.agent_version } : {}),
      });
      return send(res, 200, { ok: true, server_time: new Date().toISOString() });
    }

    // ---- signed updates (device side) --------------------------------------
    if (m === "GET" && p === "/v1/updates/latest") {
      deviceAuth(req);
      const name = url.searchParams.get("name") ?? "";
      if (!NAME_RE.test(name)) throw new HttpError(400, "invalid name");
      const dir = join(updatesDir, name);
      const v = latestVersion(dir);
      if (v === null) throw new HttpError(404, "no update");
      return send(res, 200, {
        manifest: readFileSync(join(dir, String(v), "manifest.json"), "utf8"),
        signature: readFileSync(join(dir, String(v), "manifest.sig"), "utf8"),
      });
    }

    const bundleMatch = /^\/v1\/updates\/([a-z0-9-]{1,40})\/(\d+)\/bundle$/.exec(p);
    if (m === "GET" && bundleMatch) {
      deviceAuth(req);
      const file = join(updatesDir, bundleMatch[1] as string, bundleMatch[2] as string, "bundle.tar");
      if (!existsSync(file)) throw new HttpError(404, "no such bundle");
      return send(res, 200, readFileSync(file), "application/octet-stream");
    }

    // ---- admin (dev) -------------------------------------------------------
    if (m === "GET" && p === "/v1/admin/devices") {
      adminAuth(req);
      return send(res, 200, store.listDevices());
    }

    if (m === "GET" && p === "/v1/admin/events") {
      adminAuth(req);
      const limit = Math.min(Number(url.searchParams.get("limit") ?? 50) || 50, 500);
      return send(res, 200, store.listEvents(limit));
    }

    if (m === "POST" && p === "/v1/admin/updates") {
      adminAuth(req);
      const b = await readJson<{ manifest?: string; signature?: string; bundle_b64?: string }>(req, 60 * 1024 * 1024);
      if (typeof b.manifest !== "string" || typeof b.signature !== "string" || typeof b.bundle_b64 !== "string") {
        throw new HttpError(400, "manifest, signature and bundle_b64 are required");
      }
      if (cfg.updatePublicKey) {
        let ok = false;
        try {
          ok = verify(null, Buffer.from(b.manifest), cfg.updatePublicKey, Buffer.from(b.signature, "base64"));
        } catch { /* invalid */ }
        if (!ok) throw new HttpError(400, "signature does not verify against the update public key");
      }
      let man: { name: string; version: number; bundle_sha256: string; bundle_size: number };
      try { man = JSON.parse(b.manifest); } catch { throw new HttpError(400, "manifest is not JSON"); }
      if (!NAME_RE.test(man.name) || !Number.isInteger(man.version) || man.version < 1) {
        throw new HttpError(400, "invalid manifest name or version");
      }
      const bundle = Buffer.from(b.bundle_b64, "base64");
      if (sha256(bundle) !== man.bundle_sha256 || bundle.length !== man.bundle_size) {
        throw new HttpError(400, "bundle does not match manifest hash or size");
      }
      const nameDir = join(updatesDir, man.name);
      const current = latestVersion(nameDir);
      if (current !== null && man.version <= current) {
        throw new HttpError(409, `version must be greater than ${current}`);
      }
      const dir = join(nameDir, String(man.version));
      mkdirSync(dir, { recursive: true });
      writeFileSync(join(dir, "manifest.json"), b.manifest);
      writeFileSync(join(dir, "manifest.sig"), b.signature);
      writeFileSync(join(dir, "bundle.tar"), bundle);
      return send(res, 200, { ok: true, name: man.name, version: man.version, verified: cfg.updatePublicKey !== null });
    }

    throw new HttpError(404, "not found");
  }

  const server = createServer((req, res) => {
    route(req, res).catch((e: unknown) => {
      if (e instanceof HttpError) return send(res, e.status, { error: e.message });
      console.error(JSON.stringify({ level: "error", msg: "unhandled", error: String(e) }));
      send(res, 500, { error: "internal error" });
    });
  });
  return { server, store };
}
