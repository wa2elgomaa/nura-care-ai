function env(key: string, fallback?: string): string {
  const v = process.env[key] ?? fallback;
  if (v === undefined || v === "") throw new Error(`Missing required env var ${key}`);
  return v;
}

export const config = {
  cloudUrl: env("CLOUD_URL").replace(/\/$/, ""),
  claimCode: env("SITE_CLAIM_CODE"),
  stateDir: env("STATE_DIR", "/var/lib/nura"),
  listenPort: Number(env("LISTEN_PORT", "7070")),
  updatePublicKeyFile: env("UPDATE_PUBLIC_KEY_FILE", "/keys/update_signing_key.pub"),
  updateNames: env("UPDATE_NAMES", "rule-pack").split(",").map((s) => s.trim()).filter(Boolean),
  flushIntervalMs: Number(env("FLUSH_INTERVAL_MS", "5000")),
  maxBackoffMs: Number(env("MAX_BACKOFF_MS", "30000")),
  heartbeatIntervalMs: Number(env("HEARTBEAT_INTERVAL_MS", "30000")),
  updateCheckIntervalMs: Number(env("UPDATE_CHECK_INTERVAL_MS", "60000")),
  requestTimeoutMs: Number(env("REQUEST_TIMEOUT_MS", "10000")),
  agentVersion: "0.1.0",
};
