const STORAGE_KEY = "myrenting:favorites";
const EVENT_NAME = "myrenting:favorites-change";
let cachedRaw: string | null = null;
let cachedFavorites: string[] = [];

export function getFavorites(): string[] {
  if (typeof window === "undefined") return [];
  const raw = window.localStorage.getItem(STORAGE_KEY) ?? "[]";
  if (raw === cachedRaw) return cachedFavorites;
  try {
    const value = JSON.parse(raw);
    cachedRaw = raw;
    cachedFavorites = Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
    return cachedFavorites;
  } catch {
    cachedRaw = raw;
    cachedFavorites = [];
    return cachedFavorites;
  }
}

export function toggleFavorite(id: string) {
  const favorites = getFavorites();
  const next = favorites.includes(id) ? favorites.filter((item) => item !== id) : [...favorites, id];
  const raw = JSON.stringify(next);
  window.localStorage.setItem(STORAGE_KEY, raw);
  cachedRaw = raw;
  cachedFavorites = next;
  window.dispatchEvent(new Event(EVENT_NAME));
}

export function subscribeFavorites(callback: () => void) {
  window.addEventListener(EVENT_NAME, callback);
  window.addEventListener("storage", callback);
  return () => { window.removeEventListener(EVENT_NAME, callback); window.removeEventListener("storage", callback); };
}

export const emptyFavorites: string[] = [];
