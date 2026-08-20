import type { NextConfig } from "next";
import legacyRedirects from "./src/data/legacy-redirects.json";
import inventory from "./src/data/imported-inventory.json";

function publicVehicleSlug(vehicle: { brand: string; model: string; version: string; power: number; fuel: string }) {
  return `${vehicle.brand}-${vehicle.model}-${vehicle.version}-${vehicle.power}-cv-${vehicle.fuel}`.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

const slugify = (value: string) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    // Images are already stored as compressed WebP assets. Serving them
    // directly keeps catalogue requests out of the 10 ms Free Worker budget.
    unoptimized: true,
  },
  async redirects() {
    const vehicleRedirects = inventory.vehicles.map((vehicle) => ({ source: `/coches/${vehicle.slug}`, destination: `/coches/${publicVehicleSlug(vehicle)}`, permanent: true }));
    const brandRedirects = [...new Set(inventory.vehicles.map((vehicle) => vehicle.brand))].map((brand) => ({ source: `/marcas/${slugify(brand)}`, destination: `/renting/${slugify(brand)}`, permanent: true }));
    const modelRedirects = [...new Map(inventory.vehicles.map((vehicle) => [`${slugify(vehicle.brand)}/${slugify(vehicle.model)}`, vehicle])).entries()].map(([path]) => ({ source: `/modelos/${path}`, destination: `/renting/${path}`, permanent: true }));
    const legacyProfileRedirects = [
      { source: "/marcas/:slug/:publico(particular|autonomo|empresa)", destination: "/renting/:slug", permanent: true },
      { source: "/modelos/:marca/:modelo/:publico(particular|autonomo|empresa)", destination: "/renting/:marca/:modelo", permanent: true },
      { source: "/categorias/:slug/particular", destination: "/renting/particulares", permanent: true },
      { source: "/categorias/:slug/autonomo", destination: "/renting/autonomos", permanent: true },
      { source: "/categorias/:slug/empresa", destination: "/renting/empresas", permanent: true },
    ];
    const oldLandingRedirects = [
      ["renting-suv", "suv"], ["renting-hibridos", "hibridos"], ["renting-electricos", "electricos"], ["renting-barato", "baratos"],
      ["renting-sin-entrada", "sin-entrada"], ["renting-menos-300-euros", "menos-de-300-euros"], ["renting-menos-350-euros", "menos-de-350-euros"],
      ["renting-menos-450-euros", "menos-de-450-euros"], ["renting-menos-500-euros", "menos-de-500-euros"], ["renting-autonomos", "autonomos"],
      ["renting-menos-600-euros", "menos-de-500-euros"], ["renting-menos-700-euros", "menos-de-500-euros"],
      ["renting-entrega-inmediata", "entrega-inmediata"], ["renting-automaticos", "automaticos"], ["renting-etiqueta-eco", "etiqueta-eco"],
      ["renting-etiqueta-cero", "etiqueta-cero"], ["renting-furgonetas", "furgonetas"],
    ].map(([source, destination]) => ({ source: `/${source}`, destination: `/renting/${destination}`, permanent: true }));
    const taxonomyRedirects = [
      ["/categorias/suv", "/renting/suv"], ["/categorias/familiares", "/renting/familiares"], ["/categorias/urbanos", "/renting/coches-pequenos"], ["/categorias/berlinas", "/renting"], ["/categorias/empresas", "/renting/empresas"],
      ["/combustibles/gasolina", "/renting/gasolina"], ["/combustibles/diesel", "/renting/diesel"], ["/combustibles/hibridos", "/renting/hibridos"], ["/combustibles/hibridos-enchufables", "/renting/hibridos-enchufables"], ["/combustibles/electricos", "/renting/electricos"],
    ].map(([source, destination]) => ({ source, destination, permanent: true }));
    return [...legacyRedirects, ...vehicleRedirects, ...legacyProfileRedirects, ...brandRedirects, ...modelRedirects, ...oldLandingRedirects, ...taxonomyRedirects];
  },
};

export default nextConfig;
