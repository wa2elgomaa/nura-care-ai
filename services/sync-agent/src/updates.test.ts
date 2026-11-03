import { test } from "node:test";
import assert from "node:assert/strict";
import { createHash, generateKeyPairSync, sign } from "node:crypto";
import { verifyManifest } from "./updates.js";

const { publicKey, privateKey } = generateKeyPairSync("ed25519");
const other = generateKeyPairSync("ed25519");

function make(overrides: Record<string, unknown> = {}, key = privateKey) {
  const manifest = JSON.stringify({
    name: "rule-pack",
    version: 2,
    issued_at: new Date().toISOString(),
    expires_at: new Date(Date.now() + 86_400_000).toISOString(),
    bundle_sha256: createHash("sha256").update("x").digest("hex"),
    bundle_size: 1,
    ...overrides,
  });
  return { manifest, sig: sign(null, Buffer.from(manifest), key).toString("base64") };
}

test("accepts a valid, newer manifest", () => {
  const { manifest, sig } = make();
  assert.equal(verifyManifest(manifest, sig, publicKey, 1).ok, true);
});

test("rejects a manifest signed by a different key", () => {
  const { manifest, sig } = make({}, other.privateKey);
  const r = verifyManifest(manifest, sig, publicKey, 1);
  assert.equal(r.ok, false);
  if (!r.ok) assert.equal(r.reason, "bad_signature");
});

test("rejects a tampered manifest", () => {
  const { manifest, sig } = make();
  const r = verifyManifest(manifest.replace('"version":2', '"version":9'), sig, publicKey, 1);
  assert.equal(r.ok, false);
  if (!r.ok) assert.equal(r.reason, "bad_signature");
});

test("rejects an expired manifest", () => {
  const { manifest, sig } = make({ expires_at: new Date(Date.now() - 3_600_000).toISOString() });
  const r = verifyManifest(manifest, sig, publicKey, 1);
  assert.equal(r.ok, false);
  if (!r.ok) assert.equal(r.reason, "expired");
});

test("rejects a replay of the installed or an older version", () => {
  const { manifest, sig } = make({ version: 2 });
  for (const installed of [2, 5]) {
    const r = verifyManifest(manifest, sig, publicKey, installed);
    assert.equal(r.ok, false);
    if (!r.ok) assert.equal(r.reason, "not_newer");
  }
});

test("rejects a malformed manifest even when correctly signed", () => {
  const { manifest, sig } = make({ bundle_sha256: "nope" });
  const r = verifyManifest(manifest, sig, publicKey, 1);
  assert.equal(r.ok, false);
  if (!r.ok) assert.equal(r.reason, "invalid_manifest");
});
