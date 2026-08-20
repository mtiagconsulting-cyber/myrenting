import { rentingFaqs } from "@/data/renting-faqs";
import legacyArticles from "@/data/legacy-articles.json";
import { inventoryUpdatedAt } from "@/data/offers";
import { vehicles } from "@/data/vehicles";
import { contentSlug } from "@/lib/content-slug";
import { absoluteUrl } from "@/lib/seo";
import { indexableSeoLandings, type SeoLandingFamily } from "@/lib/seo-landing-engine";
import { canonicalVehicles, vehiclePublicPath } from "@/lib/vehicle-groups";

export const sitemapNames = ["sitemap-renting.xml", "sitemap-marcas.xml", "sitemap-modelos.xml", "sitemap-categorias.xml", "sitemap-precios.xml", "sitemap-ciudades.xml", "sitemap-guias.xml"] as const;

const familyMap: Record<string, SeoLandingFamily> = {
  "sitemap-renting.xml": "renting",
  "sitemap-marcas.xml": "brands",
  "sitemap-modelos.xml": "models",
  "sitemap-categorias.xml": "categories",
  "sitemap-precios.xml": "prices",
  "sitemap-ciudades.xml": "cities",
};

const guidePaths = ["/", "/metodologia", "/blog", "/preguntas-frecuentes", "/respuestas", "/opiniones", "/quienes-somos", "/politica-editorial", "/prensa", "/informes/renting-espana-2026", "/legal/aviso-legal", "/legal/privacidad", "/legal/cookies", ...legacyArticles.articles.map(({ slug }) => `/blog/${slug}`), ...rentingFaqs.map(({ question }) => `/respuestas/${contentSlug(question)}`)];

function escapeXml(value: string) { return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&apos;"); }

export function sitemapIndexXml() {
  return `<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${sitemapNames.map((name) => `<sitemap><loc>${escapeXml(absoluteUrl(`/${name}`))}</loc><lastmod>${inventoryUpdatedAt}</lastmod></sitemap>`).join("")}</sitemapindex>`;
}

export function sitemapUrls(name: string) {
  if (name === "sitemap-guias.xml") return guidePaths;
  const family = familyMap[name];
  const landingPaths = family ? indexableSeoLandings.filter((landing) => landing.family === family).map((landing) => landing.canonical) : [];
  if (name === "sitemap-renting.xml") landingPaths.push(...canonicalVehicles(vehicles).map(vehiclePublicPath));
  return [...new Set(landingPaths)];
}

export function urlsetXml(paths: string[]) {
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${paths.map((path) => `<url><loc>${escapeXml(absoluteUrl(path))}</loc><lastmod>${inventoryUpdatedAt}</lastmod><changefreq>weekly</changefreq></url>`).join("")}</urlset>`;
}

export const xmlHeaders = { "Content-Type": "application/xml; charset=utf-8", "Cache-Control": "public, max-age=3600" };
