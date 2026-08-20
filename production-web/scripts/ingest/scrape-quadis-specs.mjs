import fs from "node:fs/promises";
import path from "node:path";
import * as cheerio from "cheerio";

const urls = [
  "https://www.quadis.es/coches-nuevos/mercedes-benz/clase-gle-coupe/clase-gle-coupe-gle-300-d-4matic/515094",
  "https://www.quadis.es/coches-nuevos/mercedes-benz/clase-gle-coupe/clase-gle-coupe-gle-350-de-4matic/499221",
  "https://www.quadis.es/coches-nuevos/nissan/qashqai/qashqai-dig-t-103kw-140cv-mhev-4x2-acenta/522510",
  "https://www.quadis.es/coches-km0/opel/corsa/corsa-12t-xhl-74kw-100cv-gs/510607",
  "https://www.quadis.es/coches-ocasion/peugeot/208/208-puretech-100-allure-75-kw-100-cv/514309",
  "https://www.quadis.es/coches-nuevos/nissan/juke/juke-16-hybrid-105kw-145cv-n-connecta/522514",
  "https://www.quadis.es/coches-nuevos/maserati/grecale/grecale-l4-mhev-300cv-awd/512138",
  "https://www.quadis.es/coches-nuevos/mercedes-benz/glc/glc-glc-300-de-4matic/497801",
  "https://www.quadis.es/coches-nuevos/mercedes-benz/glc-coupe/glc-coupe-glc-300-de-4matic/497652",
  "https://www.quadis.es/coches-nuevos/skoda/fabia/fabia-15-tsi-110kw-150cv-dsg-plus/523019",
  "https://www.quadis.es/furgonetas-nuevas/mercedes-benz-industriales/citan/citan-110-cdi-70kw-furgon-base/502928",
  "https://www.quadis.es/coches-nuevos/audi/a1/a1-sportback-adrenalin-30-tfsi-85kw-116cv/520582",
  "https://www.quadis.es/coches-renting/mg/zs/zs-hybrid-business/522422",
  "https://www.quadis.es/coches-km0/ebro/s800/s800-15-tgdi-phev-luxury-e-cvt/523173",
  "https://www.quadis.es/coches-nuevos/honda/cr-v/cr-v-20-i-mmd-phev-4x2-elegance-tech/523116",
];
const ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36";
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function extract(url) {
  const response = await fetch(url, { headers:{ "user-agent":ua, "accept-language":"es-ES,es;q=0.9" }, signal:AbortSignal.timeout(30000) });
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  const $ = cheerio.load(await response.text());
  const candidates = $("script[type='application/ld+json']").map((_, script) => $(script).html()).get();
  let vehicle;
  for (const candidate of candidates) {
    try {
      const parsed = JSON.parse(candidate);
      const items = Array.isArray(parsed) ? parsed : [parsed];
      vehicle = items.find((item) => item?.["@type"] === "Vehicle");
      if (vehicle) break;
    } catch {}
  }
  if (!vehicle && url.includes("/coches-renting/")) {
    const text=$("body").text().replace(/\s+/g," ").trim();
    const name=$("h1").first().text().replace(/\s+/g," ").trim() || $("title").text().split(" desde ")[0];
    return {
      provider:"Quadis", source_url:url, name, brand:name.split(" ")[0] || null,
      model:name.match(/^\S+\s+(\S+)/)?.[1] ?? null,
      version:name.replace(/^\S+\s+\S+\s*/,"") || null,
      model_year:null, body_type:null,
      fuel:text.match(/Combustible\s+(.+?)\s+Distintivo/i)?.[1] ?? null,
      transmission:text.match(/Cambio\s+(.+?)\s+Tracción/i)?.[1] ?? null,
      drive:text.match(/Tracción\s+(.+?)\s+Potencia/i)?.[1] ?? null,
      doors:null, seats:null, fuel_consumption_l_100km:null, condition:null,
      verified_at:new Date().toISOString(),
    };
  }
  if (!vehicle) throw new Error(`Sin Vehicle JSON-LD: ${url}`);
  return {
    provider:"Quadis",
    source_url:url,
    name:vehicle.name ?? null,
    brand:vehicle.brand?.name ?? null,
    model:vehicle.model ?? null,
    version:vehicle.vehicleConfiguration ?? null,
    model_year:vehicle.vehicleModelDate ?? null,
    body_type:vehicle.bodyType ?? null,
    fuel:vehicle.vehicleEngine?.fuelType ?? vehicle.vehicleEngine?.name ?? null,
    transmission:vehicle.vehicleTransmission ?? null,
    drive:vehicle.driveWheelConfiguration ?? null,
    doors:vehicle.numberOfDoors ?? null,
    seats:vehicle.vehicleSeatingCapacity ?? null,
    fuel_consumption_l_100km:vehicle.fuelConsumption ?? null,
    condition:vehicle.itemCondition ?? null,
    verified_at:new Date().toISOString(),
  };
}

const specs=[];
for (const url of urls) {
  try { specs.push(await extract(url)); }
  catch (error) { console.error(error.message); }
  await sleep(400);
}
const output=path.resolve("outputs/quadis-scraped-specs.json");
await fs.mkdir(path.dirname(output),{recursive:true});
await fs.writeFile(output,`${JSON.stringify({generated_at:new Date().toISOString(),image_policy:"No contiene imágenes ni URLs de imágenes",count:specs.length,specs},null,2)}\n`);
console.log(`Guardadas ${specs.length}/${urls.length} fichas en ${output}`);
