import fs from "node:fs/promises";
import path from "node:path";
import * as cheerio from "cheerio";

const BASE = "https://m-renting.com";
const CATALOGS = [
  { audience: "particular", url: `${BASE}/renting-particulares`, expected: 47 },
  { audience: "autonomo", url: `${BASE}/renting-autonomos`, expected: 61 },
  { audience: "empresa", url: `${BASE}/renting-empresas`, expected: 61 },
];
const OUTPUT_DIR = path.resolve("outputs");
const USER_AGENT =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " +
  "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36";
const delayMs = Number(process.env.SCRAPE_DELAY_MS ?? 900);
const limitArg = process.argv.find((arg) => arg.startsWith("--limit="));
const limit = limitArg ? Number(limitArg.split("=")[1]) : Infinity;
const audienceArg = process.argv.find((arg) => arg.startsWith("--audience="))?.split("=")[1];

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const clean = (value = "") => value.replace(/\s+/g, " ").trim();
const number = (value = "") => {
  let normalized = value.replace(/[^\d,.-]/g, "");
  if (normalized.includes(",")) normalized = normalized.replaceAll(".", "").replace(",", ".");
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : null;
};

async function fetchHtml(url, referer = BASE) {
  let lastError;
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    try {
      const response = await fetch(url, { headers: { "user-agent": USER_AGENT, accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "accept-language": "es-ES,es;q=0.9", referer }, redirect: "follow", signal: AbortSignal.timeout(30_000) });
      if (!response.ok) throw new Error(`${response.status} ${response.statusText}: ${url}`);
      return response.text();
    } catch (error) { lastError = error; await sleep(500 * attempt); }
  }
  throw lastError;
}

function selectedOption($, attributeId) {
  const select = $(`select[data-product-attribute="${attributeId}"]`);
  return clean(select.find("option[selected]").attr("title") || select.find("option:selected").text());
}

function variantQueries(html) {
  const $ = cheerio.load(html);
  const groups = ["5", "6"].map((attributeId) => ({
    attributeId,
    values: $(`select[data-product-attribute="${attributeId}"] option`).map((_, option) => $(option).attr("value")).get().filter(Boolean),
  }));
  if (groups.some((group) => group.values.length === 0)) return [];
  return groups[0].values.flatMap((km) => groups[1].values.map((duration) => {
    const params = new URLSearchParams();
    params.set("group[5]", km);
    params.set("group[6]", duration);
    return params;
  }));
}

function featureMap($) {
  const features = {};
  $(".especi div").each((_, element) => {
    const label = clean($(element).children("dd.value").first().text()).toLowerCase();
    const value = clean($(element).children("dt.name").first().text());
    if (label && value && !features[label]) features[label] = value;
  });
  $(".product-features2 > div").each((_, element) => {
    const label = clean($(element).find("dd.value").first().text()).toLowerCase();
    const value = clean($(element).find("dt.name").first().text());
    if (label && value) features[label] = value;
  });
  return features;
}

function parseOffer(html, sourceUrl, audience, listingId) {
  const $ = cheerio.load(html);
  const features = featureMap($);
  const title = clean(
    $("h1.namne_details, h1").first().text() ||
      $("meta[property='og:title']").attr("content") ||
      $("title").text().split("|")[0],
  );
  const manufacturerMatch = html.match(/manufacturer_name(?:\\?&quot;|\\?")\s*:\s*(?:\\?&quot;|\\?")([^"&]+)/i);
  const brand = clean(manufacturerMatch?.[1] || title.split(" ")[0]);
  const model = clean(features.modelo || (brand && title.toUpperCase().startsWith(brand.toUpperCase()) ? title.slice(brand.length) : title));
  const exVat = number($("meta[property='product:pretax_price:amount']").attr("content"));
  const incVat = number($("meta[property='product:price:amount']").attr("content"));
  const advertisedPrice = number($(".current-price").first().text());
  const kmText = selectedOption($, "5");
  const durationText = selectedOption($, "6");
  const coverageHref = $("a[aria-controls]")
    .filter((_, link) => clean($(link).text()).toLowerCase() === "coberturas")
    .first()
    .attr("href");
  const coverage = $(`${coverageHref || "#extra-3"} tr`)
    .map((_, row) => {
      const cells = $(row).find("th, td").map((__, cell) => clean($(cell).text())).get();
      return cells.length >= 2 ? { item: cells[0], detail: cells.slice(1).join(" — ") } : null;
    })
    .get();
  const availability = html.match(/availability_message(?:\\?&quot;|\\?")\s*:\s*(?:\\?&quot;|\\?")([^"&]+)/i)?.[1];

  return {
    provider: "M-Automoción / M-Renting",
    audience,
    source_url: sourceUrl,
    external_id: listingId,
    brand,
    model,
    version: clean($(".product-description").first().text()),
    status: features.estado || null,
    body_type: features["carrocería"] || null,
    fuel: features.combustible || null,
    transmission: features["transmisión"] || null,
    power: features.motor || null,
    emissions_label: features.etiqueta || null,
    doors: number(features.puertas),
    seats: number(features.plazas),
    color: features.color || null,
    annual_km: Number(kmText.replace(/\D/g, "")) || null,
    duration_months: Number(durationText.replace(/\D/g, "")) || null,
    monthly_price_ex_vat: exVat,
    monthly_price_inc_vat: incVat,
    advertised_price: advertisedPrice,
    advertised_tax_label: clean($(".product-prices").first().text()).replace(/^[\d.,]+\s*€?\s*/, "") || null,
    vat_included_in_advertised_price:
      advertisedPrice !== null && incVat !== null && Math.abs(advertisedPrice - incVat) < 0.01,
    initial_payment_eur: 0,
    availability: clean(availability || $(".availability-message").first().text()) || null,
    coverage,
    verified_at: new Date().toISOString(),
  };
}

function csvEscape(value) {
  if (value === null || value === undefined) return "";
  const text = String(value);
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

async function main() {
  const candidates = [];
  for (const catalog of CATALOGS.filter((item) => !audienceArg || item.audience === audienceArg)) {
    const products = new Map();
    for (let page = 1; page <= 10; page += 1) {
      const url = page === 1 ? catalog.url : `${catalog.url}?page=${page}`;
      const $ = cheerio.load(await fetchHtml(url, catalog.url));
      const previousCount = products.size;
      $("article[data-id-product]").each((_, article) => {
        const listingId = $(article).attr("data-id-product");
        const href = $(article).find("a[href]").first().attr("href");
        if (listingId && href) products.set(listingId, new URL(href, BASE).href.split("#")[0]);
      });
      if (page > 1 && products.size === previousCount) break;
      await sleep(delayMs);
    }
    if (products.size !== catalog.expected) console.error(`Esperados ${catalog.expected} productos ${catalog.audience}; encontrados ${products.size}`);
    candidates.push(...[...products].map(([listingId, offerUrl]) => ({ ...catalog, listingId, offerUrl })));
  }

  const selectedUrls = candidates.slice(0, limit);
  const offers = [];
  for (const [index, item] of selectedUrls.entries()) {
    try {
      const baseHtml = await fetchHtml(item.offerUrl, item.url);
      const queries = variantQueries(baseHtml);
      const variants = new Map();
      const baseOffer = parseOffer(baseHtml, item.offerUrl, item.audience, item.listingId);
      variants.set(`${baseOffer.duration_months}:${baseOffer.annual_km}`, baseOffer);
      for (const params of queries) {
        const variantUrl = `${item.offerUrl}?${params}`;
        const variant = parseOffer(await fetchHtml(variantUrl, item.url), item.offerUrl, item.audience, item.listingId);
        if (variant.duration_months && variant.annual_km && variant.advertised_price !== null) {
          variants.set(`${variant.duration_months}:${variant.annual_km}`, variant);
        }
        await sleep(delayMs);
      }
      offers.push(...variants.values());
      process.stdout.write(`\r${index + 1}/${selectedUrls.length} productos · ${offers.length} combinaciones`);
    } catch (error) {
      console.error(`\nNo se pudo extraer ${item.offerUrl}: ${error.message}`);
    }
    await sleep(delayMs);
  }
  process.stdout.write("\n");

  await fs.mkdir(OUTPUT_DIR, { recursive: true });
  const payload = {
    sources: CATALOGS,
    scope: "Particulares, autónomos y empresas; todas las combinaciones publicadas de plazo y kilometraje",
    image_policy: "No se descargan ni se almacenan imágenes o URLs de imágenes",
    generated_at: new Date().toISOString(),
    count: offers.length,
    offers,
  };
  await fs.writeFile(path.join(OUTPUT_DIR, "m-renting-offers.json"), `${JSON.stringify(payload, null, 2)}\n`);
  const headers = Object.keys(offers[0] ?? {});
  const csv = [headers.join(","), ...offers.map((offer) => headers.map((key) => csvEscape(offer[key])).join(","))].join("\n");
  await fs.writeFile(path.join(OUTPUT_DIR, "m-renting-offers.csv"), `${csv}\n`);
  console.log(`Guardadas ${offers.length} ofertas sin imágenes en ${OUTPUT_DIR}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
