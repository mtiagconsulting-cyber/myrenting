import type { NextConfig } from "next";
import legacyRedirects from "./src/data/legacy-redirects.json";
import p0Redirects from "./src/data/p0-redirects.json";
import p1Redirects from "./src/data/p1-redirects.json";
import inventory from "./src/data/imported-inventory.json";

function publicVehicleSlug(vehicle: { brand: string; model: string; version: string; power: number; fuel: string }) {
  return `${vehicle.brand}-${vehicle.model}-${vehicle.version}-${vehicle.power}-cv-${vehicle.fuel}`.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

const slugify = (value: string) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const identity = (value: string) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();

function modelKey(vehicle: { brand: string; model: string }) {
  const brand = identity(vehicle.brand);
  const rawModel = identity(vehicle.model);
  return `${brand}|${rawModel.startsWith(`${brand} `) ? rawModel.slice(brand.length + 1) : rawModel}`;
}

function canonicalInventoryVehicle(vehicle: (typeof inventory.vehicles)[number]) {
  return inventory.vehicles.filter((candidate) => modelKey(candidate) === modelKey(vehicle)).sort((first, second) => {
    const rank = (slug: string) => slug.includes("particular") ? 0 : slug.includes("autonomo") ? 1 : 2;
    return rank(first.slug) - rank(second.slug) || first.slug.localeCompare(second.slug, "es");
  })[0];
}

const legacyDestinationAliases: Record<string, string> = {
  "/marcas/byd": "/renting/byd", "/marcas/citroen": "/renting/citroen", "/marcas/ebro": "/renting/ebro",
  "/marcas/jaecoo": "/renting/jaecoo", "/marcas/kia": "/renting/kia", "/marcas/mazda": "/renting/mazda",
  "/marcas/mercedes-benz": "/renting/mercedes-benz", "/marcas/mg": "/renting/mg", "/marcas/nissan": "/renting/nissan",
  "/marcas/omoda": "/renting/omoda", "/marcas/opel": "/renting/opel", "/marcas/peugeot": "/renting/peugeot",
  "/marcas/renault": "/renting/renault", "/marcas/seat": "/renting/seat", "/marcas/skoda": "/renting/skoda",
  "/marcas/toyota": "/renting/toyota", "/marcas/volkswagen": "/renting/volkswagen",
  "/categorias/suv": "/renting/suv", "/categorias/furgonetas": "/renting/furgonetas", "/categorias/urbanos": "/renting/coches-pequenos",
  "/renting-electricos": "/renting/electricos", "/renting-hibridos": "/renting/hibridos", "/renting-suv": "/renting/suv",
};

function directLegacyDestination(destination: string) {
  const [pathname, query] = destination.split("?");
  const vehicle = pathname.startsWith("/coches/") ? inventory.vehicles.find((item) => item.slug === pathname.slice(8)) : undefined;
  if (vehicle) {
    const brand = slugify(vehicle.brand);
    const rawModel = slugify(vehicle.model);
    const model = rawModel.startsWith(`${brand}-`) ? rawModel.slice(brand.length + 1) : rawModel;
    return `/renting/${brand}/${model}`;
  }
  if (pathname === "/coches" || pathname.startsWith("/coches/")) return null;
  return legacyDestinationAliases[pathname] ?? `${pathname}${query ? `?${query}` : ""}`;
}

const moved = (source: string, destination: string) => ({ source, destination, statusCode: 301 as const });

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    // Images are already stored as compressed WebP assets. Serving them
    // directly keeps catalogue requests out of the 10 ms Free Worker budget.
    unoptimized: true,
  },
  async redirects() {
    const vehicleRedirects = inventory.vehicles.map((vehicle) => moved(`/coches/${vehicle.slug}`, `/coches/${publicVehicleSlug(canonicalInventoryVehicle(vehicle))}`));
    const brandRedirects = [...new Set(inventory.vehicles.map((vehicle) => vehicle.brand))].map((brand) => moved(`/marcas/${slugify(brand)}`, `/renting/${slugify(brand)}`));
    const modelRedirects = [...new Map(inventory.vehicles.map((vehicle) => [`${slugify(vehicle.brand)}/${slugify(vehicle.model)}`, vehicle])).entries()].map(([path]) => moved(`/modelos/${path}`, `/renting/${path}`));
    const legacyProfileRedirects = [
      moved("/marcas/:slug/:publico(particular|autonomo|empresa)", "/renting/:slug"),
      moved("/modelos/:marca/:modelo/:publico(particular|autonomo|empresa)", "/renting/:marca/:modelo"),
      moved("/categorias/:slug/particular", "/renting/particulares"),
      moved("/categorias/:slug/autonomo", "/renting/autonomos"),
      moved("/categorias/:slug/empresa", "/renting/empresas"),
    ];
    const oldLandingRedirects = [
      ["renting-suv", "suv"], ["renting-hibridos", "hibridos"], ["renting-electricos", "electricos"], ["renting-barato", "baratos"],
      ["renting-sin-entrada", "sin-entrada"], ["renting-menos-300-euros", "menos-de-300-euros"], ["renting-menos-350-euros", "menos-de-350-euros"],
      ["renting-menos-450-euros", "menos-de-450-euros"], ["renting-menos-500-euros", "menos-de-500-euros"], ["renting-autonomos", "autonomos"],
      ["renting-menos-600-euros", "menos-de-500-euros"], ["renting-menos-700-euros", "menos-de-500-euros"],
      ["renting-entrega-inmediata", "entrega-inmediata"], ["renting-automaticos", "automaticos"], ["renting-etiqueta-eco", "etiqueta-eco"],
      ["renting-etiqueta-cero", "etiqueta-cero"], ["renting-furgonetas", "furgonetas"],
    ].map(([source, destination]) => moved(`/${source}`, `/renting/${destination}`));
    const taxonomyRedirects = [
      ["/categorias/suv", "/renting/suv"], ["/categorias/familiares", "/renting/familiares"], ["/categorias/urbanos", "/renting/coches-pequenos"], ["/categorias/berlinas", "/renting"], ["/categorias/empresas", "/renting/empresas"],
      ["/combustibles/gasolina", "/renting/gasolina"], ["/combustibles/diesel", "/renting/diesel"], ["/combustibles/hibridos", "/renting/hibridos"], ["/combustibles/hibridos-enchufables", "/renting/hibridos-enchufables"], ["/combustibles/electricos", "/renting/electricos"],
    ].map(([source, destination]) => moved(source, destination));
    const p0Sources = new Set(p0Redirects.map(({ source }) => source));
    const auditSources = new Set([...p0Sources, ...p1Redirects.map(({ source }) => source)]);
    const directLegacyRedirects = legacyRedirects.flatMap(({ source, destination }) => {
      const direct = directLegacyDestination(destination);
      return direct && !auditSources.has(source) ? [moved(source, direct)] : [];
    });
    return [...directLegacyRedirects, ...vehicleRedirects, ...legacyProfileRedirects, ...brandRedirects, ...modelRedirects, ...oldLandingRedirects, ...taxonomyRedirects];
  },
};

export default nextConfig;
