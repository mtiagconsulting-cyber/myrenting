import fs from "node:fs/promises";

const inventory=JSON.parse(await fs.readFile("src/data/imported-inventory.json","utf8"));
const quadis=JSON.parse(await fs.readFile("outputs/quadis-catalog.json","utf8"));
const paper=JSON.parse(await fs.readFile("outputs/quadis-kia-offers.json","utf8"));
const vehicles=new Map(inventory.vehicles.map(vehicle=>[vehicle.id,vehicle]));
const placements=new Set();

for(const offer of inventory.offers){
  const source=offer.provider.startsWith("M-")?"m_renting":offer.vehicleId.startsWith("veh-quadis-paper-")?"quadis_paper":"quadis";
  placements.add(`${source}|${offer.audience}|${offer.vehicleId}`);
}

const imported=(source,audience)=>[...placements].filter(key=>key.startsWith(`${source}|${audience}|`)).length;
const replacedQuadisIds=new Set(paper.replaced_catalog_external_ids??[]);
const activeQuadisProducts=quadis.products.filter(product=>!replacedQuadisIds.has(String(product.external_id)));
const activeQuadisCount=(audience)=>audience==="particular"?activeQuadisProducts.length:activeQuadisProducts.filter(product=>product.audiences.includes(`${audience}s`)).length;
const rows=[
  {source:"M-Automoción / M-Renting",audience:"particular",reference_count:47,live_source_count:47,imported_count:imported("m_renting","particular"),status:"exact"},
  {source:"M-Automoción / M-Renting",audience:"autonomo",reference_count:61,live_source_count:61,imported_count:imported("m_renting","autonomo"),status:"exact"},
  {source:"M-Automoción / M-Renting",audience:"empresa",reference_count:61,live_source_count:60,listed_source_count:61,imported_count:imported("m_renting","empresa"),status:"one_listed_product_unavailable"},
  {source:"Quadis web (sin campañas reemplazadas)",audience:"particular",reference_count:36,live_source_count:activeQuadisCount("particular"),imported_count:imported("quadis","particular"),status:"current_web_catalog"},
  {source:"Quadis web (sin campañas reemplazadas)",audience:"autonomo",reference_count:31,live_source_count:activeQuadisCount("autonomo"),imported_count:imported("quadis","autonomo"),status:"current_web_catalog"},
  {source:"Quadis web (sin campañas reemplazadas)",audience:"empresa",reference_count:32,live_source_count:activeQuadisCount("empresa"),imported_count:imported("quadis","empresa"),status:"current_web_catalog"},
  ...["particular","autonomo","empresa"].map(audience=>({source:"Campañas Quadis aportadas",audience,reference_count:paper.offers.filter(offer=>(offer.audiences??["empresa"]).includes(audience)).length,live_source_count:null,imported_count:imported("quadis_paper",audience),status:"paper_source"})),
];
const failures=rows.filter(row=>row.imported_count!==(row.live_source_count??row.reference_count));
const report={
  generated_at:new Date().toISOString(),
  methodology:"Se cuentan fichas de producto únicas por proveedor y perfil; las múltiples cuotas por plazo/kilometraje no incrementan el recuento.",
  image_policy:"No se han importado imágenes ni URLs de imágenes.",
  totals:{unique_product_records:inventory.vehicles.length,profile_placements:placements.size,price_combinations:inventory.offers.length},
  rows,
  m_renting_discrepancy_note:"El catálogo de empresas anuncia 61 productos, pero la ficha 448 (Mazda CX-30) responde que el producto ya no está disponible. Se publican 60 fichas activas y se excluye la ficha inactiva.",
  quadis_discrepancy_note:"La fuente estructurada pública de Quadis consultada muestra 32 productos para autónomos y 31 para empresas. La referencia facilitada (31/32) está invertida; el inventario conserva los datos de la fuente.",
  quadis_source_snapshot:{base_products:quadis.base_product_count,audience_counts:{particular:quadis.base_product_count,autonomo:quadis.products.filter(product=>product.audiences.includes("autonomos")).length,empresa:quadis.products.filter(product=>product.audiences.includes("empresas")).length}},
  validation:failures.length===0?"passed":"failed",
  images_or_image_urls:inventory.vehicles.filter(vehicle=>vehicle.images?.length).length,
  unresolved_vehicle_ids:inventory.offers.filter(offer=>!vehicles.has(offer.vehicleId)).length,
};
await fs.writeFile("outputs/inventory-reconciliation.json",`${JSON.stringify(report,null,2)}\n`);
const columns=["source","audience","reference_count","live_source_count","imported_count","status"];
const csv=[columns.join(","),...rows.map(row=>columns.map(column=>row[column]??"").join(","))].join("\n");
await fs.writeFile("outputs/inventory-reconciliation.csv",`${csv}\n`);
console.log(JSON.stringify(report,null,2));
if(failures.length||report.images_or_image_urls||report.unresolved_vehicle_ids)process.exitCode=2;
