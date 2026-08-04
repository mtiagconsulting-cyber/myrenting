import type { MetadataRoute } from "next";
import { vehicles } from "@/data/vehicles";
import { brands } from "@/data/brands";
import { guias } from "@/data/guias";
import { pairs, pairSlug } from "@/lib/pairs";
import { byCarroceria } from "@/data/vehicles";

const SITE = "https://myrenting.es";

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();
  const url = (path: string, priority: number, changeFrequency: MetadataRoute.Sitemap[number]["changeFrequency"] = "weekly") => ({
    url: `${SITE}${path}`,
    lastModified: now,
    changeFrequency,
    priority,
  });

  const staticPages = [
    url("/", 1),
    url("/coches", 0.9),
    url("/comparar", 0.8),
    url("/marcas", 0.7),
    url("/guias", 0.6, "monthly"),
    url("/renting-suv", 0.8),
    url("/renting-hibridos", 0.8),
    url("/renting-electricos", 0.8),
  ];

  const fichas = vehicles.map((v) => url(`/coches/${v.slug}`, 0.8));
  const comparativas = pairs.map(([a, b]) => url(`/comparar/${pairSlug(a, b)}`, 0.6));
  const marcasPages = brands.filter((b) => b.count >= 3).map((b) => url(`/marcas/${b.slug}`, 0.7));
  const categoriaPages = ["urbano", "familiar", "furgoneta"]
    .filter((s) => byCarroceria(s).length >= 3)
    .map((s) => url(`/categorias/${s}`, 0.7));
  const guiaPages = guias.map((g) => url(`/guias/${g.slug}`, 0.5, "monthly"));

  return [...staticPages, ...fichas, ...comparativas, ...marcasPages, ...categoriaPages, ...guiaPages];
}
