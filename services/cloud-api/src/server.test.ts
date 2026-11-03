import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { generateKeyPairSync, randomBytes, sign } from "node:crypto";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import type { AddressInfo } from "node:net";
import { createApp } from "./server.js";

let base = "";
let dir = "";
let close: () => void = () => {};
const dev = generateKeyPairSync("ed25519");
const devPem = dev.publicKey.export({ type: "spki", format: "pem" }).toString();

before(async () => {
  dir = mkdtempSync(join(tmpdir(), "nura-cloud-"));
  const { server } = createApp({
    port: 0, dataDir: dir, claimCodes: new Map([["c1", "site-1"]]), adminToken: "admin-token",
    tokenSecret: randomBytes(32), tokenTtlSeconds: 60, updatePublicKey: null,
  });
  await new Promise<void>((r) => server.listen(0, "127.0.0.1", r));
  base = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
  close = () => server.close();
});
after(() => { close(); rmSync(dir, { recursive: true, force: true }); });

const post = (path: string, body: unknown, token?: string) =>
  fetch(base + path, {
    method: "POST",
    headers: { "content-type": "application/json", ...(token ? { authorization: `Bearer ${token}` } : {}) },
    body: JSON.stringify(body),
  });

async function login(): Promise<string> {
  const e = await (await post("/v1/enroll", { claim_code: "c1", public_key_pem: devPem })).json() as { device_id: string };
  const ch = await (await post("/v1/auth/challenge", { device_id: e.device_id })).json() as { nonce: string };
  const signature = sign(null, Buffer.from(`nura-auth-v1:${e.device_id}:${ch.nonce}`), dev.privateKey).toString("base64");
  const t = await (await post("/v1/auth/token", { device_id: e.device_id, nonce: ch.nonce, signature })).json() as { access_token: string };
  return t.access_token;
}

test("rejects enrollment with an unknown claim code", async () => {
  assert.equal((await post("/v1/enroll", { claim_code: "nope", public_key_pem: devPem })).status, 401);
});

test("rejects events without a token", async () => {
  assert.equal((await post("/v1/events", { id: "abcdefgh", type: "x", occurred_at: new Date().toISOString() })).status, 401);
});

test("rejects a token request signed by the wrong key", async () => {
  const e = await (await post("/v1/enroll", { claim_code: "c1", public_key_pem: devPem })).json() as { device_id: string };
  const ch = await (await post("/v1/auth/challenge", { device_id: e.device_id })).json() as { nonce: string };
  const wrong = generateKeyPairSync("ed25519").privateKey;
  const signature = sign(null, Buffer.from(`nura-auth-v1:${e.device_id}:${ch.nonce}`), wrong).toString("base64");
  assert.equal((await post("/v1/auth/token", { device_id: e.device_id, nonce: ch.nonce, signature })).status, 401);
});

test("a challenge cannot be reused", async () => {
  const e = await (await post("/v1/enroll", { claim_code: "c1", public_key_pem: devPem })).json() as { device_id: string };
  const ch = await (await post("/v1/auth/challenge", { device_id: e.device_id })).json() as { nonce: string };
  const signature = sign(null, Buffer.from(`nura-auth-v1:${e.device_id}:${ch.nonce}`), dev.privateKey).toString("base64");
  const body = { device_id: e.device_id, nonce: ch.nonce, signature };
  assert.equal((await post("/v1/auth/token", body)).status, 200);
  assert.equal((await post("/v1/auth/token", body)).status, 401);
});

test("events are idempotent by id", async () => {
  const token = await login();
  const ev = { id: "11111111-aaaa-bbbb-cccc-222222222222", type: "alert.test", occurred_at: new Date().toISOString(), payload: { a: 1 } };
  const first = await (await post("/v1/events", ev, token)).json() as { duplicate: boolean };
  const second = await (await post("/v1/events", ev, token)).json() as { duplicate: boolean };
  assert.equal(first.duplicate, false);
  assert.equal(second.duplicate, true);
  const list = await (await fetch(`${base}/v1/admin/events?limit=100`, { headers: { "x-admin-token": "admin-token" } })).json() as unknown[];
  assert.equal(list.filter((x) => (x as { id: string }).id === ev.id).length, 1);
});
