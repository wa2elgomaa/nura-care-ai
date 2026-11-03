import { createHash, createPublicKey, verify, type KeyObject } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import type { CloudClient } from "./cloud.js";
import type { DiskQueue } from "./queue.js";
import { log } from "./log.js";

export interface Manifest {
  name: string;
  version: number;       // monotonically increasing integer
  issued_at: string;
  expires_at: string;
  bundle_sha256: string;
  bundle_size: number;
}

export type VerifyResult =
  | { ok: true; manifest: Manifest }
  | { ok: false; reason: "bad_signature" | "invalid_manifest" | "expired" | "not_yet_valid" | "not_newer"; detail?: string };

export function loadPublicKey(file: string): KeyObject | null {
  try {
    return createPublicKey(readFileSync(file));
  } catch (e) {
    log("error", "update public key unavailable; updates disabled, alerting continues", {
      file, error: String(e),
    });
    return null;
  }
}

/**
 * Pure verification of a signed manifest.
 * The signature covers the exact manifest bytes; the manifest pins the bundle hash,
 * version and expiry, so a validly signed but old or expired bundle is rejected.
 */
export function verifyManifest(
  manifestJson: string,
  signatureB64: string,
  publicKey: KeyObject,
  installedVersion: number,
  now: Date = new Date(),
  skewMs = 5 * 60 * 1000,
): VerifyResult {
  let signatureOk = false;
  try {
    signatureOk = verify(null, Buffer.from(manifestJson, "utf8"), publicKey, Buffer.from(signatureB64, "base64"));
  } catch { /* treated as bad signature */ }
  if (!signatureOk) return { ok: false, reason: "bad_signature" };

  let m: Manifest;
  try {
    m = JSON.parse(manifestJson) as Manifest;
  } catch {
    return { ok: false, reason: "invalid_manifest", detail: "not JSON" };
  }
  const valid =
    typeof m.name === "string" && /^[a-z0-9-]{1,40}$/.test(m.name) &&
    Number.isInteger(m.version) && m.version > 0 &&
    typeof m.bundle_sha256 === "string" && /^[0-9a-f]{64}$/.test(m.bundle_sha256) &&
    Number.isInteger(m.bundle_size) && m.bundle_size >= 0 &&
    !Number.isNaN(Date.parse(m.issued_at)) && !Number.isNaN(Date.parse(m.expires_at));
  if (!valid) return { ok: false, reason: "invalid_manifest" };

  if (now.getTime() > Date.parse(m.expires_at) + skewMs) return { ok: false, reason: "expired" };
  if (Date.parse(m.issued_at) > now.getTime() + skewMs) return { ok: false, reason: "not_yet_valid" };
  if (m.version <= installedVersion) {
    return { ok: false, reason: "not_newer", detail: `offered ${m.version}, installed ${installedVersion}` };
  }
  return { ok: true, manifest: m };
}

interface AgentStateData { installed: Record<string, number>; rejected: string[] }

export class AgentState {
  data: AgentStateData = { installed: {}, rejected: [] };
  constructor(private readonly file: string) {
    if (existsSync(file)) this.data = JSON.parse(readFileSync(file, "utf8")) as AgentStateData;
  }
  save(): void {
    writeFileSync(this.file, JSON.stringify(this.data));
  }
}

const sha256 = (b: Buffer) => createHash("sha256").update(b).digest("hex");

export async function checkForUpdates(opts: {
  client: CloudClient;
  state: AgentState;
  publicKey: KeyObject | null;
  names: string[];
  queue: DiskQueue;
  stateDir: string;
}): Promise<void> {
  const { client, state, publicKey, names, queue, stateDir } = opts;
  if (!publicKey) return;

  for (const name of names) {
    const r = await client.authedGet(`/v1/updates/latest?name=${encodeURIComponent(name)}`);
    if (r.status === 404) continue;
    if (r.status !== 200) throw new Error(`update check failed: HTTP ${r.status}`);

    const { manifest, signature } = JSON.parse(r.body.toString("utf8")) as { manifest: string; signature: string };
    const manifestDigest = sha256(Buffer.from(manifest));
    if (state.data.rejected.includes(manifestDigest)) continue;

    const installed = state.data.installed[name] ?? 0;
    const v = verifyManifest(manifest, signature, publicKey, installed);
    if (!v.ok) {
      if (v.reason !== "not_newer") {
        log("error", "update rejected", { name, reason: v.reason, detail: v.detail });
        queue.enqueue("update.rejected", { name, reason: v.reason, manifest_sha256: manifestDigest });
        state.data.rejected.push(manifestDigest);
        state.save();
      }
      continue;
    }

    const m = v.manifest;
    const bundle = await client.authedGet(`/v1/updates/${encodeURIComponent(name)}/${m.version}/bundle`);
    if (bundle.status !== 200) throw new Error(`bundle download failed: HTTP ${bundle.status}`);
    if (bundle.body.length !== m.bundle_size || sha256(bundle.body) !== m.bundle_sha256) {
      log("error", "bundle does not match signed manifest", { name, version: m.version });
      queue.enqueue("update.rejected", { name, version: m.version, reason: "bundle_hash_mismatch" });
      state.data.rejected.push(manifestDigest);
      state.save();
      continue;
    }

    // Stage only. Applying the bundle (rules, models) is the next step; keep it separate.
    const dir = join(stateDir, "updates", name, String(m.version));
    mkdirSync(dir, { recursive: true });
    writeFileSync(join(dir, "bundle.tar"), bundle.body);
    writeFileSync(join(dir, "manifest.json"), manifest);
    state.data.installed[name] = m.version;
    state.save();
    queue.enqueue("update.staged", { name, version: m.version, bundle_sha256: m.bundle_sha256 });
    log("info", "update staged", { name, version: m.version });
  }
}
