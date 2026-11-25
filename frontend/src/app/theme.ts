import { readStorage, writeStorage } from "@/lib/storage";

export type ThemePreference = "light" | "dark" | "system";
export type ResolvedTheme = "light" | "dark";

export const THEME_KEY = "galeway.theme";
const DARK_QUERY = "(prefers-color-scheme: dark)";

/** Anything that is not an explicit choice means "follow the system" (same rule as index.html). */
export function parsePreference(raw: string | null): ThemePreference {
  return raw === "light" || raw === "dark" ? raw : "system";
}

export function resolveTheme(preference: ThemePreference, systemDark: boolean): ResolvedTheme {
  if (preference === "system") return systemDark ? "dark" : "light";
  return preference;
}

export function systemPrefersDark(): boolean {
  return window.matchMedia(DARK_QUERY).matches;
}

/** Calls `onChange` when the OS theme flips. Returns the unsubscribe function. */
export function subscribeToSystemTheme(onChange: () => void): () => void {
  const query = window.matchMedia(DARK_QUERY);
  query.addEventListener("change", onChange);
  return () => {
    query.removeEventListener("change", onChange);
  };
}

export function readPreference(): ThemePreference {
  return parsePreference(readStorage(THEME_KEY));
}

/**
 * Sets `data-theme` and keeps `<meta name="theme-color">` in step. The static metas use
 * media queries; an explicit choice turns the matching one on and the other off.
 */
export function applyTheme(preference: ThemePreference): ResolvedTheme {
  const resolved = resolveTheme(preference, systemPrefersDark());
  document.documentElement.setAttribute("data-theme", resolved);

  for (const meta of document.querySelectorAll<HTMLMetaElement>('meta[name="theme-color"]')) {
    // getAttribute/setAttribute, not `meta.media`: that IDL property is not available everywhere.
    const original = (meta.dataset.media ??= meta.getAttribute("media") ?? "all");
    const media =
      preference === "system" ? original : original.includes(resolved) ? "all" : "not all";
    meta.setAttribute("media", media);
  }
  return resolved;
}

export function savePreference(preference: ThemePreference): void {
  writeStorage(THEME_KEY, preference);
}

export const NEXT_PREFERENCE: Record<ThemePreference, ThemePreference> = {
  system: "light",
  light: "dark",
  dark: "system",
};
