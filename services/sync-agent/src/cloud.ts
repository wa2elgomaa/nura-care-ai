import { DeviceIdentity } from "./identity.js";
import { log } from "./log.js";

export interface HttpResult<T = any> { status: number; data: T }

export class CloudClient {
  private token: { value: string; expiresAt: number } | undefined;

  constructor(
    private readonly baseUrl: string,
    private readonly identity: DeviceIdentity,
    private readonly claimCode: string,
    private readonly timeoutMs: number,
  ) {}

  private async rawFetch(path: string, init: RequestInit = {}): Promise<Response> {
    return fetch(`${this.baseUrl}${path}`, { ...init, signal: AbortSignal.timeout(this.timeoutMs) });
  }

  private async post(path: string, body: unknown, token?: string): Promise<HttpResult> {
    const res = await this.rawFetch(path, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        ...(token ? { authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(body),
    });
    const text = await res.text();
    let data: unknown = text;
    try { data = JSON.parse(text); } catch { /* keep text */ }
    return { status: res.status, data };
  }

  /** One-time enrollment with the claim code. Idempotent for the same key. */
  async enroll(): Promise<void> {
    const r = await this.post("/v1/enroll", {
      claim_code: this.claimCode,
      public_key_pem: this.identity.publicKeyPem,
    });
    if (r.status !== 200) throw new Error(`enroll failed: HTTP ${r.status} ${JSON.stringify(r.data)}`);
    this.identity.setDeviceId((r.data as { device_id: string }).device_id);
    log("info", "enrolled", { device_id: this.identity.deviceId });
  }

  /** Challenge-response: sign a server nonce with the device key, receive a short-lived token. */
  private async authenticate(allowReenroll = true): Promise<string> {
    if (!this.identity.deviceId) await this.enroll();
    const deviceId = this.identity.deviceId as string;

    const ch = await this.post("/v1/auth/challenge", { device_id: deviceId });
    if (ch.status === 404 && allowReenroll) {
      log("warn", "cloud does not know this device, re-enrolling");
      await this.enroll();
      return this.authenticate(false);
    }
    if (ch.status !== 200) throw new Error(`challenge failed: HTTP ${ch.status}`);

    const { nonce } = ch.data as { nonce: string };
    const signature = this.identity.signMessage(`nura-auth-v1:${deviceId}:${nonce}`);
    const tk = await this.post("/v1/auth/token", { device_id: deviceId, nonce, signature });
    if (tk.status !== 200) throw new Error(`token request failed: HTTP ${tk.status}`);

    const { access_token, expires_in } = tk.data as { access_token: string; expires_in: number };
    this.token = { value: access_token, expiresAt: Date.now() + (expires_in - 30) * 1000 };
    return access_token;
  }

  private async bearer(): Promise<string> {
    if (this.token && Date.now() < this.token.expiresAt) return this.token.value;
    return this.authenticate();
  }

  /** Authenticated JSON POST; refreshes the token once on 401. */
  async authedPost(path: string, body: unknown): Promise<HttpResult> {
    let r = await this.post(path, body, await this.bearer());
    if (r.status === 401) {
      this.token = undefined;
      r = await this.post(path, body, await this.bearer());
    }
    return r;
  }

  async authedGet(path: string): Promise<{ status: number; body: Buffer }> {
    const doGet = async () =>
      this.rawFetch(path, { headers: { authorization: `Bearer ${await this.bearer()}` } });
    let res = await doGet();
    if (res.status === 401) {
      this.token = undefined;
      res = await doGet();
    }
    return { status: res.status, body: Buffer.from(await res.arrayBuffer()) };
  }
}
