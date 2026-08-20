import fs from "node:fs";
import path from "node:path";
import { load } from "cheerio";

const root = process.cwd();
const assets = path.join(root, ".open-next", "assets");
const failures = [];
const warnings = [];

function fail(message) { failures.push(message); }
function warn(message) { warnings.push(message); }
function read(relativePath) {
  const target = path.join(assets, relativePath);
  if (!fs.existsSync(target)) { fail(`Falta el asset ${relativePath}`); return ""; }
  return fs.readFileSync(target, "utf8");
}
function hasNull(value) {
  if (value === null) return true;
  if (Array.isArray(value)) return value.some(hasNull);
  if (typeof value === "object" && value) return Object.values(value).some(hasNull);
  return false;
}
function graphNodes(value) {
  if (Array.isArray(value)) return value.flatMap(graphNodes);
  if (typeof value !== "object" || !value) return [];
  return value["@graph"] ? graphNodes(value["@graph"]) : [value];
}

const sitemap = read("sitemap.xml");
if (!sitemap.startsWith("<?xml")) fail("sitemap.xml no comienza como XML");
const childSitemaps = [...sitemap.matchAll(/<loc>(https:\/\/myrenting\.es\/(sitemap-[^<]+\.xml))<\/loc>/g)].map((match) => ({ url: match[1], asset: match[2] }));
if (!childSitemaps.length) fail("sitemap.xml no es un índice de sitemaps válido");
const urls = childSitemaps.flatMap(({ asset }) => [...read(asset).matchAll(/<loc>([^<]+)<\/loc>/g)].map((match) => match[1].replaceAll("&amp;", "&")));
if (!urls.length) fail("Los sitemaps no contienen URLs");
if (new Set(urls).size !== urls.length) fail("sitemap.xml contiene URLs duplicadas");

for (const url of urls) {
  const parsed = new URL(url);
  if (parsed.origin !== "https://myrenting.es") fail(`Origen incorrecto en sitemap: ${url}`);
  if (parsed.search || parsed.hash) fail(`URL no canónica en sitemap: ${url}`);
  const relative = parsed.pathname === "/" ? "index.html" : `${decodeURIComponent(parsed.pathname.slice(1))}.html`;
  const html = read(relative);
  if (!html) continue;
  const $ = load(html);
  const title = $("title").text().trim();
  const canonical = $('link[rel="canonical"]').attr("href");
  const robots = $('meta[name="robots"]').attr("content") ?? "";
  const h1 = $("h1").first().text().trim();
  const expectedCanonical = parsed.pathname === "/" ? parsed.origin : `${parsed.origin}${parsed.pathname}`;
  if (!title) fail(`${parsed.pathname}: falta title`);
  if (!h1) fail(`${parsed.pathname}: falta H1`);
  if (canonical?.replace(/\/$/, "") !== expectedCanonical.replace(/\/$/, "")) fail(`${parsed.pathname}: canonical ${canonical ?? "ausente"}`);
  if (/noindex/i.test(robots)) fail(`${parsed.pathname}: URL del sitemap marcada noindex`);
  if ((parsed.pathname.startsWith("/coches/") || parsed.pathname.startsWith("/renting") || parsed.pathname.startsWith("/blog/") || parsed.pathname.startsWith("/respuestas/") || parsed.pathname.startsWith("/informes/")) && !$('meta[property="og:title"]').attr("content")) fail(`${parsed.pathname}: falta Open Graph específico`);
  if (parsed.pathname.startsWith("/comparar/") && !$("main").text().includes("Comparación homogénea:") && !$("main").text().includes("No existe una configuración idéntica")) fail(`${parsed.pathname}: no declara si la configuración es comparable`);
  if (parsed.pathname.startsWith("/coches/") && !$("main").text().includes("Fuente:")) fail(`${parsed.pathname}: no muestra la procedencia de la oferta`);
  const pageSchemaNodes = [];
  $('script[type="application/ld+json"]').each((_, element) => {
    try {
      const data = JSON.parse($(element).text());
      pageSchemaNodes.push(...graphNodes(data));
      if (hasNull(data)) fail(`${parsed.pathname}: JSON-LD contiene null`);
      if (parsed.pathname.startsWith("/coches/")) {
        const product = graphNodes(data).find((node) => node["@type"] === "Product");
        if (product) {
          const offer = product.offers;
          if (offer?.["@type"] !== "AggregateOffer" || !offer.offerCount || !Array.isArray(offer.offers)) fail(`${parsed.pathname}: falta AggregateOffer con todas las cuotas`);
          if (offer?.offers?.some((item) => !item.priceSpecification || item.priceSpecification.unitText !== "mes")) fail(`${parsed.pathname}: alguna oferta estructurada no identifica la cuota mensual`);
          const properties = new Set((product.additionalProperty ?? []).map((item) => item.name));
          for (const required of ["Tipo de cliente", "Duración del contrato", "Kilómetros anuales", "Entrada", "Tratamiento del IVA"]) if (!properties.has(required)) fail(`${parsed.pathname}: falta ${required} en Product`);
        }
      }
    } catch {
      fail(`${parsed.pathname}: JSON-LD inválido`);
    }
  });
  const editorialType = parsed.pathname.startsWith("/informes/") ? "Report" : parsed.pathname.startsWith("/blog/") || parsed.pathname.startsWith("/respuestas/") ? "Article" : null;
  if (editorialType) {
    const editorial = pageSchemaNodes.find((node) => node["@type"] === editorialType);
    const webpage = pageSchemaNodes.find((node) => node["@type"] === "WebPage");
    if (!editorial || !webpage) fail(`${parsed.pathname}: falta grafo WebPage + ${editorialType}`);
    if (!editorial?.dateModified) fail(`${parsed.pathname}: falta dateModified editorial`);
    if (editorial?.author?.["@id"] !== "https://myrenting.es/#organization" || editorial?.publisher?.["@id"] !== "https://myrenting.es/#organization") fail(`${parsed.pathname}: autor o publisher editorial no enlazado a Organization`);
    if (editorial?.mainEntityOfPage?.["@id"] !== webpage?.["@id"]) fail(`${parsed.pathname}: mainEntityOfPage editorial incoherente`);
  }
}

const robots = read("robots.txt");
if (!robots.includes("Sitemap: https://myrenting.es/sitemap.xml")) fail("robots.txt no declara el sitemap canónico");
const llms = read("llms.txt");
for (const required of ["## Modelos agrupados", "## Combustibles", "Informe del mercado 2026", "Sala de prensa y datos", "Metodología"]) if (!llms.includes(required)) fail(`llms.txt no incluye ${required}`);
const homepage = read("index.html");
if (!homepage.includes("traffic_attribution") || !homepage.includes("AI Assistants") || !homepage.includes("myrenting_attribution")) fail("La atribución de asistentes IA no está presente en el HTML");
for (const link of [...llms.matchAll(/\]\((https:\/\/myrenting\.es\/[^)]+)\)/g)].map((match) => match[1])) {
  if (link.includes("&")) warn(`Revisar enlace especial en llms.txt: ${link}`);
}

console.log(`URLs auditadas: ${urls.length}`);
for (const message of warnings) console.warn(`AVISO: ${message}`);
for (const message of failures) console.error(`ERROR: ${message}`);
if (failures.length) process.exit(1);
console.log("Auditoría SEO del build superada.");
