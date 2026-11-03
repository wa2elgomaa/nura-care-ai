import { createPublicKey, randomBytes } from "node:crypto";
import { readFileSync } from "node:fs";
import { createApp } from "./server.js";

function parseClaimCodes(raw: string): Map<string, string> {
  const m = new Map<string, string>();
  for (const part of raw.split(",")) {
    const [code, site] = part.split(":").map((s) => s.trim());
    if (code && site) m.set(code, site);
  }
  return m;
}

const claimCodes = parseClaimCodes(process.env.CLAIM_CODES ?? "");
if (claimCodes.size === 0) throw new Error("CLAIM_CODES is required, e.g. dev-claim-code:dev-site-001");

const adminToken = process.env.ADMIN_TOKEN ?? "";
if (adminToken.length < 8) throw new Error("ADMIN_TOKEN is required (8+ characters)");

let updatePublicKey = null;
const keyFile = process.env.UPDATE_PUBLIC_KEY_FILE;
if (keyFile) {
  try {
    updatePublicKey = createPublicKey(readFileSync(keyFile));
  } catch (e) {
    console.warn(JSON.stringify({ level: "warn", msg: "update public key not loaded; uploads will not be verified", error: String(e) }));
  }
}

const port = Number(process.env.PORT ?? 8080);
const { server } = createApp({
  port,
  dataDir: process.env.DATA_DIR ?? "/data",
  claimCodes,
  adminToken,
  // Random per start if unset: issued tokens become invalid on restart and agents simply re-authenticate.
  tokenSecret: process.env.TOKEN_SECRET ? Buffer.from(process.env.TOKEN_SECRET) : randomBytes(32),
  tokenTtlSeconds: Number(process.env.DEVICE_TOKEN_TTL_SECONDS ?? 900),
  updatePublicKey,
});

server.listen(port, "0.0.0.0", () =>
  console.log(JSON.stringify({ level: "info", msg: "cloud-api started", port, update_key_loaded: updatePublicKey !== null })),
);

for (const sig of ["SIGINT", "SIGTERM"] as const) process.on(sig, () => server.close(() => process.exit(0)));
