import fs from "node:fs/promises";
import path from "node:path";

const m = JSON.parse(await fs.readFile("outputs/m-renting-offers.json", "utf8"));
const q = JSON.parse(await fs.readFile("outputs/quadis-kia-offers.json", "utf8"));
const qCatalog = JSON.parse(await fs.readFile("outputs/quadis-catalog.json", "utf8"));
const slugify = (value) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const fuel = (value="") => /enchuf/i.test(value) ? "Híbrido enchufable" : /híbr|mhev|hev/i.test(value) ? "Híbrido" : /diés|dies/i.test(value) ? "Diésel" : /eléct/i.test(value) ? "Eléctrico" : "Gasolina";
const label = (value="") => /cero|^0$/i.test(value) ? "0" : /eco/i.test(value) ? "ECO" : "C";
const body = (value="", model="") => /furg/i.test(value+model) ? "Furgoneta" : /suv|todoterreno/i.test(value) || /niro|qashqai|juke|mokka|grecale|gle|glc|zs|s800|cr-v/i.test(model) ? "SUV" : /berlina/i.test(value) ? "Berlina" : "Compacto";
const availability = (value="") => /stock|inmediata|últimas/i.test(value) ? "Disponible" : /agosto|septiembre|octubre|días/i.test(value) ? "Entrega próxima" : "Consultar";
const vehicleMap = new Map();
const offers=[];
const mRentingDefaultCoverage = [
  {item:"Seguro a todo riesgo",detail:"Incluido en la cuota; condiciones según contrato"},
  {item:"Mantenimiento preventivo y correctivo",detail:"Incluido en la cuota"},
  {item:"Neumáticos por desgaste",detail:"Incluidos según las condiciones del contrato"},
];

function vehicleId(brand,model,version){return `veh-${slugify(`${brand}-${model}-${version}`)}`;}
function addVehicle(data){
  const id=data.inventoryKey?`veh-${slugify(data.inventoryKey)}`:vehicleId(data.brand,data.model,data.version);
  if(!vehicleMap.has(id)) vehicleMap.set(id,{id,brand:data.brand,model:data.model,version:data.version,slug:id.slice(4),images:null,fuel:fuel(data.fuel),power:data.power??0,trunk:null,consumption:data.consumption??null,consumptionUnit:"l/100 km",label:label(data.emissions_label),bodyType:body(data.body_type,data.model),transmission:data.transmission??null,doors:data.doors??null,seats:data.seats??null,colors:data.colors??null,campaign:data.campaign??null,sourceUrl:data.source_url??null});
  return id;
}

for(const item of m.offers){
  const id=addVehicle({...item,inventoryKey:`m-${item.audience}-${item.external_id}`,power:Number(String(item.power??"").match(/\d+/)?.[0]??0)});
  const coverage=item.coverage.length?item.coverage:mRentingDefaultCoverage;
  offers.push({id:`off-${slugify(item.audience+'-'+item.external_id+'-'+item.duration_months+'-'+item.annual_km)}`,vehicleId:id,provider:item.provider,audience:item.audience,monthlyPrice:item.advertised_price??item.monthly_price_inc_vat??item.monthly_price_ex_vat,priceIncludesVat:item.vat_included_in_advertised_price,monthlyPriceExVat:item.monthly_price_ex_vat,monthlyPriceIncVat:item.monthly_price_inc_vat,initialPayment:item.initial_payment_eur??0,duration:item.duration_months,kilometers:item.annual_km,maintenance:coverage.some(x=>/mantenimiento|mecánica/i.test(x.item)),insurance:coverage.some(x=>/seguro/i.test(x.item)),tyres:coverage.some(x=>/neumático/i.test(x.item)),coverage,availability:availability(item.availability),sourceUrl:item.source_url,verifiedAt:item.verified_at});
}
const replacedQuadisIds=new Set(q.replaced_catalog_external_ids??[]);
for(const item of qCatalog.products.filter(product=>!replacedQuadisIds.has(String(product.external_id)))){
  const id=addVehicle({...item,inventoryKey:`quadis-${item.external_id}`,power:item.power_cv,source_url:item.source_url});
  const audiences=["particular",...(item.audiences.includes("autonomos")?["autonomo"]:[]),...(item.audiences.includes("empresas")?["empresa"]:[])];
  for(const audience of audiences)for(const price of item.prices){
    const isParticular=audience==="particular";
    const displayed=isParticular?price.monthly_price_inc_vat:price.monthly_price_ex_vat;
    offers.push({id:`off-${slugify(id+'-quadis-'+audience+'-'+price.duration_months+'-'+price.annual_km+'-'+displayed)}`,vehicleId:id,provider:item.provider,audience,monthlyPrice:displayed,priceIncludesVat:isParticular,monthlyPriceExVat:price.monthly_price_ex_vat,monthlyPriceIncVat:price.monthly_price_inc_vat,initialPayment:0,duration:price.duration_months,kilometers:price.annual_km,maintenance:true,insurance:true,tyres:true,coverage:item.coverage.map(detail=>({item:detail,detail:"Incluido"})),availability:availability(item.availability),sourceUrl:item.source_url,verifiedAt:item.verified_at});
  }
}
for(const [paperIndex,item] of q.offers.entries()){
  const campaignKey=item.campaign??`${paperIndex+1}`;
  const id=addVehicle({...item,inventoryKey:`quadis-paper-${item.brand}-${item.model}-${item.version}-${campaignKey}`,power:item.power_cv,source_url:null});
  for(const audience of item.audiences??["empresa"])for(const price of item.prices){
    const isParticular=audience==="particular";
    const displayed=isParticular?price.monthly_price_inc_vat:price.monthly_price_ex_vat;
    if(!(displayed>0))continue;
    offers.push({id:`off-${slugify(id+'-paper-'+audience+'-'+price.duration_months+'-'+price.annual_km)}`,vehicleId:id,provider:item.provider,audience,monthlyPrice:displayed,priceIncludesVat:isParticular,monthlyPriceExVat:price.monthly_price_ex_vat,monthlyPriceIncVat:price.monthly_price_inc_vat,initialPayment:0,duration:price.duration_months,kilometers:price.annual_km,maintenance:true,insurance:true,tyres:true,coverage:item.coverage.map(detail=>({item:detail,detail:"Incluido"})),availability:availability(item.availability),sourceUrl:null,verifiedAt:q.generated_at});
  }
}
const inventory={generatedAt:new Date().toISOString(),vehicles:[...vehicleMap.values()],offers};
await fs.writeFile(path.resolve("src/data/imported-inventory.json"),`${JSON.stringify(inventory,null,2)}\n`);
console.log(`Inventario normalizado: ${inventory.vehicles.length} vehículos y ${offers.length} ofertas`);
