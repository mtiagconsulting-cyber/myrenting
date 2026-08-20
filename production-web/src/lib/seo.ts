export const siteUrl = (process.env.NEXT_PUBLIC_SITE_URL ?? "https://myrenting.es").replace(/\/$/, "");

export function absoluteUrl(path: string) {
  return `${siteUrl}${path.startsWith("/") ? path : `/${path}`}`;
}
