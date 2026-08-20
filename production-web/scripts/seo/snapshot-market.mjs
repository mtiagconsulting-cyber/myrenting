import fs from "node:fs";

const inventory = JSON.parse(fs.readFileSync("src/data/imported-inventory.json", "utf8"));
const aliases = JSON.parse(fs.readFileSync("src/data/vehicle-aliases.json", "utf8"));
const target = "src/data/market-snapshots.json";
const stored = JSON.parse(fs.readFileSync(target, "utf8"));
const duplicateIds = new Set(Object.keys(aliases).map((slug) => `veh-${slug}`));
const vehicles = inventory.vehicles.filter((vehicle) => !aliases[vehicle.slug]);
const offers = inventory.offers.filter((offer) => !duplicateIds.has(offer.vehicleId));
const periodArgument = process.argv.find((value) => value.startsWith("--period="));
const period = periodArgument?.split("=")[1] ?? inventory.generatedAt.slice(0, 7);
if (!/^\d{4}-\d{2}$/.test(period)) throw new Error("Usa --period=AAAA-MM");

function median(values) { const sorted = [...values].sort((a, b) => a - b); return sorted.length ? sorted[Math.floor(sorted.length / 2)] : 0; }
function stats(list) { const values = list.map((offer) => offer.monthlyPrice); return { offers: list.length, minimum: values.length ? Math.min(...values) : 0, median: median(values), maximum: values.length ? Math.max(...values) : 0 }; }

const brandGroups = new Map();
for (const vehicle of vehicles) {
  const key = vehicle.brand.toLocaleLowerCase("es");
  if (!brandGroups.has(key)) brandGroups.set(key, { brand: vehicle.brand, ids: new Set() });
  brandGroups.get(key).ids.add(vehicle.id);
}
const brands = [...brandGroups.values()].map((group) => {
  const list = offers.filter((offer) => group.ids.has(offer.vehicleId));
  const summary = stats(list);
  return { brand: group.brand, offers: summary.offers, minimum: summary.minimum, median: summary.median };
}).sort((a, b) => b.offers - a.offers);
const withEntry = offers.filter((offer) => offer.initialPayment > 0);
const withoutEntry = offers.filter((offer) => offer.initialPayment === 0);
const snapshot = {
  period,
  reviewedAt: new Date().toISOString().slice(0, 10),
  inventoryGeneratedAt: inventory.generatedAt,
  vehicles: vehicles.length,
  offers: offers.length,
  audiences: Object.fromEntries(["particular", "autonomo", "empresa"].map((audience) => [audience, stats(offers.filter((offer) => offer.audience === audience))])),
  entry: { withEntry: withEntry.length, withoutEntry: withoutEntry.length, medianTotalWithoutEntry: median(withoutEntry.map((offer) => offer.monthlyPrice * offer.duration + offer.initialPayment)) },
  brands,
};
const snapshots = [...stored.snapshots.filter((item) => item.period !== period), snapshot].sort((a, b) => a.period.localeCompare(b.period));
fs.writeFileSync(target, `${JSON.stringify({ snapshots }, null, 2)}\n`);
console.log(`Snapshot ${period}: ${vehicles.length} vehículos y ${offers.length} combinaciones.`);
