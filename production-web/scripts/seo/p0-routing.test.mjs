import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const root = new URL("../../", import.meta.url);
const readJson = async (path) => JSON.parse(await readFile(new URL(path, root), "utf8"));
const slugify = (value) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

const p0 = await readJson("src/data/p0-redirects.json");
const p1 = await readJson("src/data/p1-redirects.json");
const p2 = await readJson("src/data/p2-redirects.json");
const inventory = await readJson("src/data/imported-inventory.json");
const configSource = await readFile(new URL("next.config.ts", root), "utf8");
const middlewareSource = await readFile(new URL("src/middleware.ts", root), "utf8");
const sitemapSource = await readFile(new URL("src/lib/sitemaps.ts", root), "utf8");
const rentingPageSource = await readFile(new URL("src/app/renting/[[...segments]]/page.tsx", root), "utf8");
const vehiclePageSource = await readFile(new URL("src/app/coches/[slug]/page.tsx", root), "utf8");
const layoutSource = await readFile(new URL("src/app/layout.tsx", root), "utf8");
const notFoundSource = await readFile(new URL("src/app/not-found.tsx", root), "utf8");
const priorityArticleSource = await readFile(new URL("src/components/editorial/PriorityArticleContent.tsx", root), "utf8");
const blogPageSource = await readFile(new URL("src/app/blog/[slug]/page.tsx", root), "utf8");
const homeSource = await readFile(new URL("src/app/page.tsx", root), "utf8");
const listingSource = await readFile(new URL("src/components/seo/SeoListingPage.tsx", root), "utf8");
const cardSource = await readFile(new URL("src/components/vehicles/VehicleCard.tsx", root), "utf8");
const detailSource = await readFile(new URL("src/components/vehicles/VehicleDetail.tsx", root), "utf8");
const comparisonSource = await readFile(new URL("src/components/comparison/ComparisonTable.tsx", root), "utf8");
const pricingSource = await readFile(new URL("src/lib/offer-pricing.ts", root), "utf8");
const csvSource = await readFile(new URL("src/app/informes/renting-espana-2026/datos.csv/route.ts", root), "utf8");
const landingEngineSource = await readFile(new URL("src/lib/seo-landing-engine.ts", root), "utf8");
const reportSource = await readFile(new URL("src/app/informes/renting-espana-2026/page.tsx", root), "utf8");
const snapshotSource = await readFile(new URL("scripts/seo/snapshot-market.mjs", root), "utf8");

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

test("los lotes de auditoría no contienen fuentes duplicadas ni cadenas", () => {
  const redirects = [...p0, ...p1, ...p2];
  const sources = redirects.map(({ source }) => source);
  assert.equal(new Set(sources).size, sources.length);
  const sourceSet = new Set(sources);
  for (const { source, destination } of redirects) {
    assert.notEqual(source, destination);
    assert.ok(!sourceSet.has(destination), `${source} apunta a otra fuente: ${destination}`);
    assert.ok(!destination.includes("?"), `${source} conserva parámetros innecesarios`);
  }
});

test("cada destino de auditoría existe en las rutas o el inventario actuales", () => {
  for (const { source, destination } of [...p0, ...p1, ...p2]) assert.ok(canonicalRoutes.has(destination), `${source} -> ${destination} no existe`);
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
  assert.match(sitemapSource, /consolidatedArticleSlugs/);
});

test("las guías editoriales duplicadas se consolidan", () => {
  assert.match(middlewareSource, /renting-autonomos-guia\.html[^\n]+renting-autonomos-deduccion-2026\.html/);
  assert.match(middlewareSource, /renting-vs-leasing\.html[^\n]+renting-vs-leasing-diferencias-2026\.html/);
});

test("las URLs P2 inestables se resuelven directamente a una categoría vigente", () => {
  assert.match(middlewareSource, /"\/renting-gasolina\.html": "\/renting\/gasolina"/);
  assert.match(middlewareSource, /"\/renting\/furgonetas\/menos-de-500-euros": "\/renting\/furgonetas"/);
});

test("las URLs P2 duplicadas redirigen sin parámetros a destinos canónicos vigentes", () => {
  assert.equal(p2.length, 91);
  assert.ok(p2.some(({ source, destination }) => source === "/marcas/seat" && destination === "/renting/seat"));
  assert.ok(p2.some(({ source, destination }) => source === "/modelos/peugeot/208" && destination === "/renting/peugeot/208"));
  assert.ok(p2.some(({ source, destination }) => source === "/renting/kia/niro/entrega-inmediata" && destination === "/renting/kia/niro"));
  for (const { destination } of p2) assert.ok(!destination.includes("?"));
});

test("las landings geográficas antiguas consolidan autoridad en el catálogo indexable", () => {
  const redirects = [...p0, ...p1];
  for (const city of ["madrid", "barcelona", "valencia", "malaga", "bilbao", "zaragoza", "alicante"]) {
    assert.ok(redirects.some(({ source, destination }) => source === `/renting-${city}.html` && destination === "/renting"));
  }
});

test("las landings históricas de marca, modelo y ciudad no terminan en 404", () => {
  assert.match(middlewareSource, /function legacyBrandDestination/);
  for (const brand of ["bmw", "seat", "nissan", "hyundai", "mercedes-benz", "volkswagen", "mazda"]) {
    assert.match(middlewareSource, new RegExp(`\\"${brand}\\"`));
  }
  for (const destination of ["mercedes-benz", "lynk-co", "electricos", "suv", "hibridos"]) assert.match(middlewareSource, new RegExp(`\\"${destination}\\"`));
});

test("las páginas editoriales prioritarias muestran inventario vivo y CTA", () => {
  for (const slug of ["renting-electrico-2026.html", "renting-barato-2026.html", "mejores-coches-renting-2026.html", "que-incluye-renting-coche.html", "renting-autonomos-deduccion-2026.html", "renting-vs-leasing-diferencias-2026.html"]) assert.match(priorityArticleSource, new RegExp(slug.replaceAll(".", "\\.")));
  assert.match(priorityArticleSource, /inventoryUpdatedAt/);
  assert.match(priorityArticleSource, /VehicleGrid/);
});

test("los precios SEO se comparan con y sin IVA mediante una única regla", () => {
  assert.match(pricingSource, /offerPriceExVat/);
  assert.match(pricingSource, /offerPriceIncVat/);
  assert.match(rentingPageSource, /sin IVA/);
  assert.match(rentingPageSource, /con IVA/);
  assert.match(listingSource, /minimumPriceExVat/);
  assert.match(listingSource, /minimumPriceIncVat/);
  assert.doesNotMatch(landingEngineSource, /\$\{title\}[^`]+\| MyRenting/);
  assert.doesNotMatch(vehiclePageSource, /const title = `[^`]+\| MyRenting/);
});

test("las tarjetas no publican cero caballos como dato real", () => {
  assert.match(cardSource, /vehicle\.power > 0/);
  assert.doesNotMatch(cardSource, />\{vehicle\.power\} CV</);
  assert.match(detailSource, /vehicle\.power > 0/);
  assert.match(comparisonSource, /vehicle\.power > 0/);
});

test("la home enlaza directamente las oportunidades detectadas en Search Console", () => {
  for (const path of ["/renting/kia/niro", "/renting/peugeot/208", "/renting/bmw/serie-1", "/renting/hyundai/tucson", "/renting/volkswagen/t-roc", "/renting/nissan/qashqai"]) assert.match(homeSource, new RegExp(path));
  assert.match(homeSource, /Marcos Automoción/);
});

test("las páginas con oportunidad en Search Console tienen snippets, FAQ y enlaces específicos", () => {
  for (const path of ["/renting", "/renting/kia/niro", "/renting/peugeot/208", "/renting/suv"]) assert.match(rentingPageSource, new RegExp(path.replaceAll("/", "\\/")));
  for (const phrase of ["Renting coches desde", "Renting Kia Niro desde", "Renting Peugeot 208 desde", "Renting SUV desde"]) assert.match(rentingPageSource, new RegExp(phrase));
  assert.match(rentingPageSource, /priorityFaqs/);
  assert.match(rentingPageSource, /priority\?\.links/);
  assert.match(priorityArticleSource, /¿Cuál es el coche de renting más barato\?/);
  assert.match(blogPageSource, /faqSchema\(priorityFaqs\)/);
});

test("el informe ofrece datos reutilizables y distingue ambos precios", () => {
  assert.match(csvSource, /precio_sin_iva/);
  assert.match(csvSource, /precio_con_iva/);
  assert.match(csvSource, /offer\.provider/);
  assert.match(reportSource, /datos\.csv/);
  assert.match(reportSource, /providerNames/);
  assert.doesNotMatch(reportSource, /Datos propios · Agosto de 2026/);
  assert.match(snapshotSource, /normalizeBrand/);
});
