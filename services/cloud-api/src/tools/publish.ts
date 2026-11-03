// Offline signing tool. Run it where the PRIVATE key lives (your laptop or CI),
// never inside the running cloud service.
//
//   SIGNING_KEY_FILE=secrets/update_signing_key.pem ADMIN_TOKEN=... CLOUD_URL=http://localhost:8082 \
//   node dist/tools/publish.js --name rule-pack --version 1 --dir ./bundles/demo [--ttl-days 30]
import { createHash, createPrivateKey, sign } from "node:crypto";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

function arg(name: string, fallback?: string): string {
  const i = process.argv.indexOf(`--${name}`);
  const v = i >= 0 ? process.argv[i + 1] : fallback;
  if (!v) throw new Error(`missing --${name}`);
  return v;
}
const need = (k: string) => {
  const v = process.env[k];
  if (!v) throw new Error(`missing env ${k}`);
  return v;
};

const name = arg("name");
const version = Number(arg("version"));
const dir = arg("dir");
const ttlDays = Number(arg("ttl-days", "30"));
if (!Number.isInteger(version) || version < 1) throw new Error("--version must be a positive integer");

const tmp = mkdtempSync(join(tmpdir(), "nura-publish-"));
try {
  const tarFile = join(tmp, "bundle.tar");
  execFileSync("tar", ["-cf", tarFile, "-C", dir, "."]);
  const bundle = readFileSync(tarFile);

  const now = Date.now();
  const manifest = JSON.stringify({
    name,
    version,
    issued_at: new Date(now).toISOString(),
    expires_at: new Date(now + ttlDays * 86_400_000).toISOString(),
    bundle_sha256: createHash("sha256").update(bundle).digest("hex"),
    bundle_size: bundle.length,
  });
  const signature = sign(null, Buffer.from(manifest), createPrivateKey(readFileSync(need("SIGNING_KEY_FILE"))))
    .toString("base64");

  const res = await fetch(`${process.env.CLOUD_URL ?? "http://localhost:8080"}/v1/admin/updates`, {
    method: "POST",
    headers: { "content-type": "application/json", "x-admin-token": need("ADMIN_TOKEN") },
    body: JSON.stringify({ manifest, signature, bundle_b64: bundle.toString("base64") }),
  });
  console.log(res.status, await res.text());
  if (!res.ok) process.exitCode = 1;
} finally {
  rmSync(tmp, { recursive: true, force: true });
}
