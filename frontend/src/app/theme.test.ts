import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  applyTheme,
  NEXT_PREFERENCE,
  parsePreference,
  readPreference,
  resolveTheme,
  savePreference,
  THEME_KEY,
} from "./theme";

function mockSystemDark(dark: boolean): void {
  vi.stubGlobal("matchMedia", (query: string) => ({ matches: dark, media: query }));
}

beforeEach(() => {
  document.head.innerHTML = `
    <meta name="theme-color" content="#F6F7F9" media="(prefers-color-scheme: light)">
    <meta name="theme-color" content="#0B0F17" media="(prefers-color-scheme: dark)">`;
  mockSystemDark(false);
});

afterEach(() => {
  vi.unstubAllGlobals();
  localStorage.clear();
});

describe("preference parsing", () => {
  it.each([
    ["light", "light"],
    ["dark", "dark"],
    ["system", "system"],
    [null, "system"],
    ["purple", "system"],
    ["", "system"],
  ] as const)("%s -> %s", (raw, expected) => {
    expect(parsePreference(raw)).toBe(expected);
  });

  it("is read from and saved to storage", () => {
    expect(readPreference()).toBe("system");
    savePreference("dark");
    expect(localStorage.getItem(THEME_KEY)).toBe("dark");
    expect(readPreference()).toBe("dark");
  });
});

describe("resolveTheme", () => {
  it("follows the system only for 'system'", () => {
    expect(resolveTheme("system", true)).toBe("dark");
    expect(resolveTheme("system", false)).toBe("light");
    expect(resolveTheme("light", true)).toBe("light");
    expect(resolveTheme("dark", false)).toBe("dark");
  });
});

describe("applyTheme", () => {
  it("sets data-theme from the system when no choice was made", () => {
    mockSystemDark(true);

    expect(applyTheme("system")).toBe("dark");
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });

  it("lets an explicit choice win over the system", () => {
    mockSystemDark(true);

    expect(applyTheme("light")).toBe("light");
    expect(document.documentElement.getAttribute("data-theme")).toBe("light");
  });

  it("switches theme-color metas on explicit choice and restores them for 'system'", () => {
    const [light, dark] = document.querySelectorAll<HTMLMetaElement>('meta[name="theme-color"]');

    applyTheme("dark");
    expect([light?.getAttribute("media"), dark?.getAttribute("media")]).toEqual(["not all", "all"]);

    applyTheme("system");
    expect([light?.getAttribute("media"), dark?.getAttribute("media")]).toEqual([
      "(prefers-color-scheme: light)",
      "(prefers-color-scheme: dark)",
    ]);
  });
});

describe("NEXT_PREFERENCE", () => {
  it("cycles through every preference", () => {
    expect(NEXT_PREFERENCE.system).toBe("light");
    expect(NEXT_PREFERENCE.light).toBe("dark");
    expect(NEXT_PREFERENCE.dark).toBe("system");
  });
});
