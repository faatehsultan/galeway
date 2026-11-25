import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { getHealth, HttpError } from "./client";
import { shouldRetry } from "./queryClient";

import { API, server } from "@/test/server";

describe("getHealth", () => {
  it("returns the parsed health payload", async () => {
    await expect(getHealth()).resolves.toEqual({ status: "ok", version: "abcdef1234567" });
  });

  it("throws an HttpError carrying the status on a non-2xx response", async () => {
    server.use(http.get(`${API}/api/v1/health`, () => new HttpResponse(null, { status: 503 })));

    const error = await getHealth().catch((e: unknown) => e);

    expect(error).toBeInstanceOf(HttpError);
    expect((error as HttpError).status).toBe(503);
  });

  it("honours a caller's abort signal", async () => {
    const controller = new AbortController();
    controller.abort();

    await expect(getHealth(controller.signal)).rejects.toThrow();
  });
});

describe("shouldRetry (CACHING §1)", () => {
  it("never retries a 4xx", () => {
    expect(shouldRetry(0, new HttpError(404, "nope"))).toBe(false);
    expect(shouldRetry(0, new HttpError(429, "slow down"))).toBe(false);
  });

  it("retries 5xx and network errors twice", () => {
    expect(shouldRetry(0, new HttpError(502, "bad gateway"))).toBe(true);
    expect(shouldRetry(1, new TypeError("network"))).toBe(true);
    expect(shouldRetry(2, new HttpError(502, "bad gateway"))).toBe(false);
  });
});
