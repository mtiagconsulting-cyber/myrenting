import fs from "node:fs/promises";

const inventoryPath = "outputs/m-renting-offers.json";
const refreshPath = process.argv[2] ?? "outputs/m-renting-refresh-2026-08-12.json";
const payload = JSON.parse(await fs.readFile(inventoryPath, "utf8"));
const refresh = JSON.parse(await fs.readFile(refreshPath, "utf8"));

const refreshedKeys = new Set(
  refresh.offers.map((offer) => `${offer.audience}:${offer.external_id}`),
);
const templates = new Map();
for (const offer of payload.offers) {
  const key = `${offer.audience}:${offer.external_id}`;
  if (!templates.has(key)) templates.set(key, offer);
}

const untouched = payload.offers.filter(
  (offer) => !refreshedKeys.has(`${offer.audience}:${offer.external_id}`),
);
const updated = refresh.offers.map((offer) => {
  const key = `${offer.audience}:${offer.external_id}`;
  const template = templates.get(key) ?? {};
  const { _title, _version, ...live } = offer;
  return {
    ...template,
    ...live,
    brand: template.brand ?? _title?.split(" ")[0] ?? "",
    model: template.model ?? _title ?? "",
    version: template.version || _version || "",
  };
});

payload.offers = [...untouched, ...updated].sort((a, b) =>
  `${a.audience}:${a.external_id}:${a.duration_months}:${a.annual_km}`.localeCompare(
    `${b.audience}:${b.external_id}:${b.duration_months}:${b.annual_km}`,
  ),
);
payload.count = payload.offers.length;
payload.generated_at = refresh.generated_at;
payload.refresh = {
  source: refreshPath,
  refreshed_product_records: refreshedKeys.size,
  refreshed_price_combinations: updated.length,
  catalog_counts: { particular: 47, autonomo: 61, empresa: 61 },
  active_detail_counts: { particular: 47, autonomo: 61, empresa: 60 },
  unavailable_catalog_records: [
    {
      audience: "empresa",
      external_id: "448",
      source_url: "https://m-renting.com/oferta-renting-empresa-mazda-cx-30-mt-blanco",
      reason: "La ficha responde: Este producto ya no está disponible",
    },
  ],
};

await fs.writeFile(inventoryPath, `${JSON.stringify(payload, null, 2)}\n`);

const headers = Object.keys(payload.offers[0] ?? {});
const csvCell = (value) => {
  if (value === null || value === undefined) return "";
  const text = typeof value === "object" ? JSON.stringify(value) : String(value);
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
};
const csv = [
  headers.join(","),
  ...payload.offers.map((offer) => headers.map((header) => csvCell(offer[header])).join(",")),
].join("\n");
await fs.writeFile("outputs/m-renting-offers.csv", `${csv}\n`);

console.log(
  `M-Renting actualizado: ${refreshedKeys.size} productos comprobados en detalle, ${updated.length} combinaciones y ${payload.count} combinaciones activas totales.`,
);
