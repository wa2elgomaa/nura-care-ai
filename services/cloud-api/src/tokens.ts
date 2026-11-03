import { createHmac, timingSafeEqual } from "node:crypto";

export interface TokenPayload { sub: string; site: string; exp: number }

/** Minimal HMAC-signed bearer token (dev). Swap for a standard JWT library when needed. */
export class TokenService {
  constructor(private readonly secret: Buffer, readonly ttlSeconds: number) {}

  private mac(body: string): string {
    return createHmac("sha256", this.secret).update(body).digest("base64url");
  }

  issue(deviceId: string, siteId: string): { token: string; expires_in: number } {
    const payload: TokenPayload = {
      sub: deviceId, site: siteId, exp: Math.floor(Date.now() / 1000) + this.ttlSeconds,
    };
    const body = Buffer.from(JSON.stringify(payload)).toString("base64url");
    return { token: `${body}.${this.mac(body)}`, expires_in: this.ttlSeconds };
  }

  verify(token: string): TokenPayload | null {
    const [body, sig] = token.split(".");
    if (!body || !sig) return null;
    const expected = Buffer.from(this.mac(body));
    const given = Buffer.from(sig);
    if (expected.length !== given.length || !timingSafeEqual(expected, given)) return null;
    try {
      const p = JSON.parse(Buffer.from(body, "base64url").toString("utf8")) as TokenPayload;
      return p.exp > Math.floor(Date.now() / 1000) ? p : null;
    } catch {
      return null;
    }
  }
}
