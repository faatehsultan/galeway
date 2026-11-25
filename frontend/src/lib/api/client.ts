import type { components } from "./schema";

export type Health = components["schemas"]["HealthOut"];

/** A non-2xx response. `status` drives retry decisions (no retry on 4xx). */
export class HttpError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "HttpError";
    this.status = status;
  }
}

const API_BASE = import.meta.env.VITE_API_BASE_URL.replace(/\/+$/, "");
// A free-tier instance can take about a minute to wake up (FRONTEND §6).
const COLD_START_TIMEOUT_MS = 90_000;

export async function getHealth(signal?: AbortSignal): Promise<Health> {
  const timeout = AbortSignal.timeout(COLD_START_TIMEOUT_MS);
  const response = await fetch(`${API_BASE}/api/v1/health`, {
    signal: signal ? AbortSignal.any([signal, timeout]) : timeout,
  });
  if (!response.ok) {
    throw new HttpError(
      response.status,
      `Health check failed with status ${String(response.status)}`,
    );
  }
  return (await response.json()) as Health;
}
