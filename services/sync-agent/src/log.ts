export type Level = "debug" | "info" | "warn" | "error";
const order: Record<Level, number> = { debug: 10, info: 20, warn: 30, error: 40 };
const min = order[(process.env.LOG_LEVEL as Level) ?? "info"] ?? 20;

export function log(level: Level, msg: string, fields: Record<string, unknown> = {}): void {
  if (order[level] < min) return;
  console.log(JSON.stringify({ t: new Date().toISOString(), level, msg, ...fields }));
}
