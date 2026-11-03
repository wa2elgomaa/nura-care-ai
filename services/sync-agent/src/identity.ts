import {
  createPrivateKey, createPublicKey, generateKeyPairSync, sign, type KeyObject,
} from "node:crypto";
import { chmodSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

export class DeviceIdentity {
  deviceId: string | undefined;

  private constructor(
    private readonly privateKey: KeyObject,
    readonly publicKeyPem: string,
    private readonly metaFile: string,
  ) {
    if (existsSync(metaFile)) {
      this.deviceId = (JSON.parse(readFileSync(metaFile, "utf8")) as { device_id?: string }).device_id;
    }
  }

  /** Generates an Ed25519 keypair on first start. The private key never leaves the box. */
  static loadOrCreate(stateDir: string): DeviceIdentity {
    mkdirSync(stateDir, { recursive: true });
    const keyFile = join(stateDir, "device.key");
    if (!existsSync(keyFile)) {
      const { privateKey } = generateKeyPairSync("ed25519");
      writeFileSync(keyFile, privateKey.export({ type: "pkcs8", format: "pem" }), { mode: 0o600 });
      chmodSync(keyFile, 0o600);
    }
    const privateKey = createPrivateKey(readFileSync(keyFile));
    const publicKeyPem = createPublicKey(privateKey).export({ type: "spki", format: "pem" }).toString();
    return new DeviceIdentity(privateKey, publicKeyPem, join(stateDir, "device.json"));
  }

  setDeviceId(id: string): void {
    this.deviceId = id;
    writeFileSync(this.metaFile, JSON.stringify({ device_id: id }));
  }

  signMessage(message: string): string {
    return sign(null, Buffer.from(message, "utf8"), this.privateKey).toString("base64");
  }
}
