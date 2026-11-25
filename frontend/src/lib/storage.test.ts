import { afterEach, describe, expect, it, vi } from "vitest";

import { readStorage, writeStorage } from "./storage";

afterEach(() => {
  vi.restoreAllMocks();
  localStorage.clear();
});

describe("storage", () => {
  it("round-trips a value", () => {
    expect(writeStorage("k", "v")).toBe(true);
    expect(readStorage("k")).toBe("v");
  });

  it("returns null for a missing key", () => {
    expect(readStorage("missing")).toBeNull();
  });

  it("does not throw when storage is blocked", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new DOMException("blocked", "SecurityError");
    });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new DOMException("full", "QuotaExceededError");
    });

    expect(readStorage("k")).toBeNull();
    expect(writeStorage("k", "v")).toBe(false);
  });
});
