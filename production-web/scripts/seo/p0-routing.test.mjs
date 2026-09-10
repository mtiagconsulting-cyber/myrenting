import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const root = new URL("../../", import.meta.url);
const readJson = async (path) => JSON.parse(await readFile(new URL(path, root), "utf8"));
const slugify = (value) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

const p0 = await readJson("src/data/p0-redirects.json");
const p1 = await readJson("src/data/p1-redirects.json");
const inventory = await readJson("src/data/imported-inventory.json");
const configSource = await readFile(new URL("next.config.ts", root), "utf8");
const middlewareSource = await readFile(new URL("src/middleware.ts", root), "utf8");
const sitemapSource = await readFile(new URL("src/lib/sitemaps.ts", root), "utf8");
const rentingPageSource = await readFile(new URL("src/app/renting/[[...segments]]/page.tsx", root), "utf8");
const vehiclePageSource = await readFile(new URL("src/app/coches/[slug]/page.tsx", root), "utf8");
const layoutSource = await readFile(new URL("src/app/layout.tsx", root), "utf8");
const notFoundSource = await readFile(new URL("src/app/not-found.tsx", root), "utf8");
const priorityArticleSource = await readFile(new URL("src/components/editorial/PriorityArticleContent.tsx", root), "utf8");

const canonicalRoutes = new Set([
  "/renting", "/coches",
  "/renting/baratos", "/renting/suv", "/renting/familiares", "/renting/furgonetas", "/renting/coches-pequenos", "/renting/gasolina", "/renting/diesel", "/renting/hibridos", "/renting/electricos", "/renting/hibridos-enchufables",
  "/renting/menos-de-300-euros", "/renting/menos-de-350-euros", "/renting/menos-de-400-euros", "/renting/menos-de-500-euros",
  "/renting/autonomos", "/renting/empresas", "/renting/particulares",
  ...["madrid", "barcelona", "valencia", "sevilla", "malaga", "zaragoza", "bilbao", "alicante"].map((city) => `/renting/${city}`),
  ...["electricos", "hibridos", "suv"].flatMap((taxonomy) => [300, 350, 400, 500].map((price) => `/renting/${taxonomy}/menos-de-${price}-euros`)),
]);
const representativeByModel = new Map();
const identity = (value) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
const modelKey = (vehicle) => {
  const brand = identity(vehicle.brand);
  const rawModel = identity(vehicle.model);
  return `${brand}|${rawModel.startsWith(`${brand} `) ? rawModel.slice(brand.length + 1) : rawModel}`;
};
const rank = (vehicle) => vehicle.slug.includes("particular") ? 0 : vehicle.slug.includes("autonomo") ? 1 : 2;
for (const vehicle of inventory.vehicles) {
  const brand = slugify(vehicle.brand);
  let model = slugify(vehicle.model);
  if (model.startsWith(`${brand}-`)) model = model.slice(brand.length + 1);
  canonicalRoutes.add(`/renting/${brand}`);
  canonicalRoutes.add(`/renting/${brand}/${model}`);
  const current = representativeByModel.get(modelKey(vehicle));
  if (!current || rank(vehicle) < rank(current) || (rank(vehicle) === rank(current) && vehicle.slug.localeCompare(current.slug, "es") < 0)) representativeByModel.set(modelKey(vehicle), vehicle);
}
for (const vehicle of representativeByModel.values()) canonicalRoutes.add(`/coches/${slugify(`${vehicle.brand}-${vehicle.model}-${vehicle.version}-${vehicle.power}-cv-${vehicle.fuel}`)}`);

test("el lote P0 no contiene fuentes duplicadas ni cadenas", () => {
  const redirects = [...p0, ...p1];
  const sources = redirects.map(({ source }) => source);
  assert.equal(new Set(sources).size, sources.length);
  const sourceSet = new Set(sources);
  for (const { source, destination } of redirects) {
    assert.notEqual(source, destination);
    assert.ok(!sourceSet.has(destination), `${source} apunta a otra fuente: ${destination}`);
    assert.ok(!destination.includes("?"), `${source} conserva parámetros innecesarios`);
  }
});

test("cada destino del lote P0 existe en las rutas o el inventario actuales", () => {
  for (const { source, destination } of [...p0, ...p1]) assert.ok(canonicalRoutes.has(destination), `${source} -> ${destination} no existe`);
});

test("las redirecciones permanentes configuradas responden 301", () => {
  assert.match(configSource, /statusCode: 301 as const/);
  assert.match(middlewareSource, /NextResponse\.redirect\([^;]+, 301\)/);
});

test("canonicals y sitemap se construyen desde las URLs definitivas", () => {
  assert.match(rentingPageSource, /alternates: \{ canonical: landing\.canonical \}/);
  assert.match(vehiclePageSource, /alternates: \{ canonical \}/);
  assert.match(sitemapSource, /indexableSeoLandings/);
  assert.match(sitemapSource, /canonicalVehicles\(vehicles\)\.map\(vehiclePublicPath\)/);
  assert.doesNotMatch(sitemapSource, /legacy-redirects|p0-redirects|p1-redirects/);
});

test("la respuesta 404 no hereda la canonical de la home y declara noindex", () => {
  assert.doesNotMatch(layoutSource, /alternates:\s*\{\s*canonical:\s*["']\/["']/);
  assert.match(notFoundSource, /robots:\s*\{\s*index:\s*false,\s*follow:\s*false\s*\}/);
});

test("el artículo duplicado de renting barato se consolida y sale del sitemap", () => {
  assert.match(middlewareSource, /mejores-coches-renting-baratos\.html[^\n]+renting-barato-2026\.html/);
  assert.match(sitemapSource, /slug !== "mejores-coches-renting-baratos\.html"/);
});

test("las páginas editoriales prioritarias muestran inventario vivo y CTA", () => {
  for (const slug of ["renting-electrico-2026.html", "renting-barato-2026.html", "mejores-coches-renting-2026.html", "que-incluye-renting-coche.html"]) assert.match(priorityArticleSource, new RegExp(slug.replaceAll(".", "\\.")));
  assert.match(priorityArticleSource, /inventoryUpdatedAt/);
  assert.match(priorityArticleSource, /VehicleGrid/);
});
