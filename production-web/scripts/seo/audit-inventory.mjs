import fs from "node:fs";

const inventory = JSON.parse(fs.readFileSync("src/data/imported-inventory.json", "utf8"));
const officialEvidence = JSON.parse(fs.readFileSync("src/data/vehicle-spec-evidence.json", "utf8"));
const vehicleAliases = JSON.parse(fs.readFileSync("src/data/vehicle-aliases.json", "utf8"));
const vehicleIds = new Set(inventory.vehicles.map((vehicle) => vehicle.id));
const offerIds = new Set();
const combinations = new Set();
const failures = [];
const missingTechnical = [];
const duplicateGroups = new Map();

for (const vehicle of inventory.vehicles) {
  const effectiveVehicle = { ...vehicle, ...(officialEvidence.specs[vehicle.id] ?? {}) };
  if (!vehicle.id || !vehicle.slug || !vehicle.brand || !vehicle.model) failures.push(`Vehículo incompleto: ${vehicle.id ?? "sin id"}`);
  if (effectiveVehicle.power <= 0 || effectiveVehicle.trunk == null || effectiveVehicle.consumption == null) missingTechnical.push(vehicle.id);
  const vehicleOffers = inventory.offers.filter((offer) => offer.vehicleId === vehicle.id);
  const matrix = vehicleOffers.map((offer) => [offer.audience, offer.duration, offer.kilometers, offer.monthlyPrice, offer.initialPayment, offer.priceIncludesVat, offer.provider].join("|")).sort().join(";");
  const duplicateKey = [vehicle.brand.toLowerCase(), vehicle.model.toLowerCase(), vehicle.version.toLowerCase(), vehicle.sourceUrl, matrix].join("||");
  duplicateGroups.set(duplicateKey, [...(duplicateGroups.get(duplicateKey) ?? []), vehicle.slug]);
}
for (const offer of inventory.offers) {
  if (!vehicleIds.has(offer.vehicleId)) failures.push(`Oferta huérfana ${offer.id}: ${offer.vehicleId}`);
  if (offerIds.has(offer.id)) failures.push(`ID de oferta duplicado: ${offer.id}`);
  offerIds.add(offer.id);
  if (!(offer.monthlyPrice > 0) || !(offer.duration > 0) || !(offer.kilometers > 0)) failures.push(`Condiciones inválidas: ${offer.id}`);
  const key = [offer.vehicleId, offer.audience, offer.duration, offer.kilometers].join("|");
  if (combinations.has(key)) failures.push(`Combinación duplicada: ${key}`);
  combinations.add(key);
}

const withoutOffers = inventory.vehicles.filter((vehicle) => !inventory.offers.some((offer) => offer.vehicleId === vehicle.id));
for (const vehicle of withoutOffers) failures.push(`Vehículo sin ofertas: ${vehicle.id}`);

const duplicateSlugs = [...duplicateGroups.values()].filter((group) => group.length > 1).flatMap((group) => group.slice(1));
for (const slug of duplicateSlugs) {
  if (!vehicleAliases[slug]) failures.push(`Duplicado sin canonicalización: ${slug}`);
}
for (const [source, destination] of Object.entries(vehicleAliases)) {
  if (!duplicateSlugs.includes(source)) failures.push(`Alias sin duplicado demostrado: ${source}`);
  if (!inventory.vehicles.some((vehicle) => vehicle.slug === destination)) failures.push(`Destino de alias inexistente: ${source} -> ${destination}`);
}

console.log(`Vehículos: ${inventory.vehicles.length}`);
console.log(`Ofertas: ${inventory.offers.length}`);
console.log(`Vehículos con datos técnicos pendientes: ${missingTechnical.length}`);
console.log(`Duplicados canonicalizados: ${duplicateSlugs.length}`);
for (const failure of failures) console.error(`ERROR: ${failure}`);
if (failures.length) process.exit(1);
console.log("Auditoría de inventario superada.");
