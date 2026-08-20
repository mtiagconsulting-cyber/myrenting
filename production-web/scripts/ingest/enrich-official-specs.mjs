import fs from "node:fs/promises";
import { execFileSync } from "node:child_process";
import * as cheerio from "cheerio";

const inventoryPath = "src/data/imported-inventory.json";
const registryPath = "src/data/official-spec-sources.json";
const outputPath = "src/data/vehicle-spec-evidence.json";
const cachePath = "src/data/official-spec-cache.json";
const inventory = JSON.parse(await fs.readFile(inventoryPath, "utf8"));
const registry = JSON.parse(await fs.readFile(registryPath, "utf8"));
const cache = JSON.parse(await fs.readFile(cachePath, "utf8"));
const dryRun = process.argv.includes("--dry-run");
const normalize = (value = "") => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, " ").trim().toLowerCase();
const same = (first, second) => normalize(first) === normalize(second);
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function officialUrl(source) {
  const hostname = new URL(source.url).hostname.toLowerCase();
  return source.officialDomains.some((domain) => hostname === domain || hostname.endsWith(`.${domain}`));
}

function matches(vehicle, rule) {
  if (!same(vehicle.brand, rule.brand) || !same(vehicle.model, rule.model)) return false;
  if (rule.fuel && !same(vehicle.fuel, rule.fuel)) return false;
  if (rule.powerCv && vehicle.power !== rule.powerCv) return false;
  if (rule.versionRegex && !new RegExp(rule.versionRegex, "i").test(vehicle.version)) return false;
  return true;
}

async function fetchOfficialText(source) {
  if (!officialUrl(source)) throw new Error("dominio no autorizado como oficial");
  const response = await fetch(source.url, {
    headers: { "user-agent": "MyRentingBot/1.0 (+https://myrenting.es/metodologia)", "accept-language": "es-ES,es;q=0.9" },
    redirect: "follow",
    signal: AbortSignal.timeout(30_000),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const finalHostname = new URL(response.url).hostname.toLowerCase();
  if (!source.officialDomains.some((domain) => finalHostname === domain || finalHostname.endsWith(`.${domain}`))) throw new Error("redirección fuera del dominio oficial");
  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/pdf") || response.url.toLowerCase().endsWith(".pdf")) {
    const pdf = Buffer.from(await response.arrayBuffer());
    return normalize(execFileSync("pdftotext", ["-", "-"], { input: pdf, encoding: "utf8", maxBuffer: 20_000_000 }));
  }
  if (!contentType.includes("text/html")) throw new Error(`formato no soportado: ${contentType}`);
  const $ = cheerio.load(await response.text());
  $("script,style,noscript").remove();
  return normalize($("body").text());
}

const specs = {};
const rejectedSources = [];
for (const source of registry.sources) {
  const candidates = inventory.vehicles.filter((vehicle) => matches(vehicle, source.match));
  if (!candidates.length) { rejectedSources.push({ id: source.id, reason: "ninguna versión coincide exactamente" }); continue; }
  let usedLiveRetrieval = false;
  try {
    let text;
    let retrieval = "live";
    let retrievedAt = new Date().toISOString();
    try {
      text = await fetchOfficialText(source);
      usedLiveRetrieval = true;
    } catch (liveError) {
      const snapshot = cache.snapshots[source.id];
      if (!snapshot || snapshot.url !== source.url) throw liveError;
      text = normalize(snapshot.text);
      retrieval = "verified-cache";
      retrievedAt = snapshot.retrievedAt;
    }
    const missingEvidence = source.requiredEvidence.filter((evidence) => !text.includes(normalize(evidence)));
    if (missingEvidence.length) throw new Error(`evidencia ausente: ${missingEvidence.join(", ")}`);
    for (const vehicle of candidates) {
      const previous = specs[vehicle.id] ?? {};
      const sourceEvidence = { id: source.id, url: source.url, publisher: source.publisher, retrievedAt, retrieval, confidence: "high", matchedVersion: vehicle.version };
      specs[vehicle.id] = {
        ...previous,
        ...source.facts,
        ...((previous.dimensions || source.facts.dimensions) ? { dimensions: { ...(previous.dimensions ?? {}), ...(source.facts.dimensions ?? {}) } } : {}),
        source: sourceEvidence,
        sources: [...(previous.sources ?? (previous.source ? [previous.source] : [])), sourceEvidence],
      };
    }
    console.log(`${source.id}: ${candidates.length} ficha(s) enriquecida(s)`);
  } catch (error) {
    rejectedSources.push({ id: source.id, reason: error.message });
    console.error(`${source.id}: rechazada (${error.message})`);
  }
  if (usedLiveRetrieval) await sleep(250);
}

const output = { generatedAt: new Date().toISOString(), matchedVehicles: Object.keys(specs).length, rejectedSources, specs };
if (!dryRun) await fs.writeFile(outputPath, `${JSON.stringify(output, null, 2)}\n`);
console.log(`Coincidencias de confianza alta: ${output.matchedVehicles}. Fuentes rechazadas: ${rejectedSources.length}.`);
if (dryRun) console.log("Modo dry-run: no se ha modificado el archivo de evidencias.");
