import fs from "node:fs";

const inventory = JSON.parse(fs.readFileSync("src/data/imported-inventory.json", "utf8"));
const evidence = JSON.parse(fs.readFileSync("src/data/vehicle-spec-evidence.json", "utf8"));
const registry = JSON.parse(fs.readFileSync("src/data/official-spec-sources.json", "utf8"));
const facts = ["trunk", "consumption", "doors", "seats", "dimensions", "electricRangeKm", "emissionsCo2GKm", "batteryCapacityKWh"];
const merged = inventory.vehicles.map((vehicle) => ({ ...vehicle, ...(evidence.specs[vehicle.id] ?? {}) }));
const normalizedFuel = (vehicle) => String(vehicle.fuel ?? "").normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase();
const isApplicable = (vehicle, field) => {
  const fuel = normalizedFuel(vehicle);
  if (field === "electricRangeKm") return fuel.includes("electrico") || fuel.includes("enchufable");
  if (field === "batteryCapacityKWh") return fuel.includes("electrico") || fuel.includes("hibrido");
  return true;
};
const isMissing = (vehicle, field) => field === "consumption" ? vehicle.consumption == null && vehicle.consumptionRange == null : field === "emissionsCo2GKm" ? vehicle.emissionsCo2GKm == null && vehicle.emissionsCo2Range == null : vehicle[field] == null;
const missingByField = Object.fromEntries(facts.map((field) => [field, merged.filter((vehicle) => isApplicable(vehicle, field) && isMissing(vehicle, field)).length]));
const pendingModels = new Map();
const researchQueue = new Map();
for (const vehicle of merged) {
  const missing = facts.filter((field) => isApplicable(vehicle, field) && isMissing(vehicle, field));
  if (!missing.length) continue;
  const key = `${vehicle.brand.toUpperCase()}|${vehicle.model.toUpperCase()}`;
  if (!pendingModels.has(key)) pendingModels.set(key, { brand: vehicle.brand, model: vehicle.model, vehicles: 0, missing: new Set() });
  const item = pendingModels.get(key); item.vehicles += 1; missing.forEach((field) => item.missing.add(field));
  const versionKey = [vehicle.brand, vehicle.model, vehicle.version, vehicle.power, vehicle.fuel].join("|").toUpperCase();
  if (!researchQueue.has(versionKey)) {
    const terms = [vehicle.brand, vehicle.model, vehicle.version, vehicle.power ? `${vehicle.power} CV` : "", "especificaciones ficha técnica consumo emisiones dimensiones maletero batería autonomía"].filter(Boolean).join(" ");
    researchQueue.set(versionKey, {
      brand: vehicle.brand,
      model: vehicle.model,
      version: vehicle.version,
      powerCv: vehicle.power ?? null,
      fuel: vehicle.fuel,
      vehicleIds: [],
      missing: new Set(),
      officialSearchQuery: `${terms} ${vehicle.brand} España oficial`,
    });
  }
  const queueItem = researchQueue.get(versionKey);
  queueItem.vehicleIds.push(vehicle.id);
  missing.forEach((field) => queueItem.missing.add(field));
}
const report = {
  generatedAt: new Date().toISOString(),
  vehicles: merged.length,
  matchedWithOfficialEvidence: Object.keys(evidence.specs).length,
  registeredOfficialSources: registry.sources.length,
  rejectedSources: evidence.rejectedSources,
  missingByField,
  pendingModels: [...pendingModels.values()].map((item) => ({ ...item, missing: [...item.missing] })).sort((a, b) => b.vehicles - a.vehicles || `${a.brand} ${a.model}`.localeCompare(`${b.brand} ${b.model}`, "es")),
  researchQueue: [...researchQueue.values()].map((item) => ({ ...item, missing: [...item.missing] })).sort((a, b) => `${a.brand} ${a.model} ${a.version}`.localeCompare(`${b.brand} ${b.model} ${b.version}`, "es")),
};
fs.mkdirSync("outputs", { recursive: true });
fs.writeFileSync("outputs/official-spec-coverage.json", `${JSON.stringify(report, null, 2)}\n`);
console.log(`Evidencia oficial: ${report.matchedWithOfficialEvidence}/${report.vehicles} vehículos.`);
console.log(`Fuentes oficiales registradas: ${report.registeredOfficialSources}. Rechazadas: ${report.rejectedSources.length}.`);
for (const [field, count] of Object.entries(missingByField)) console.log(`${field}: ${count} pendientes`);
console.log(`Informe: outputs/official-spec-coverage.json (${report.pendingModels.length} modelos pendientes).`);
console.log(`Cola de investigación oficial: ${report.researchQueue.length} versiones exactas.`);
if (report.rejectedSources.length) process.exitCode = 1;
