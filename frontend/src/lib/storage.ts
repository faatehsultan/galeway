/**
 * Safe `localStorage` access. Storage can be missing or throw (private mode, blocked site data,
 * quota), so every call is guarded and the app keeps working without it (FRONTEND §7).
 */
export function readStorage(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

/** Returns false when the value could not be saved. */
export function writeStorage(key: string, value: string): boolean {
  try {
    localStorage.setItem(key, value);
    return true;
  } catch {
    return false;
  }
}
