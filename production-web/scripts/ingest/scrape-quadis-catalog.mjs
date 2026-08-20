import fs from "node:fs/promises";
import path from "node:path";
import * as cheerio from "cheerio";

const BASE="https://www.quadis.es";
const ua="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36";
const sleep=(ms)=>new Promise(resolve=>setTimeout(resolve,ms));
async function get(url){
  const page=url.match(/[?&]page=(\d+)/)?.[1];
  const id=url.match(/\/(\d+)$/)?.[1];
  const local=page?`work/quadis-catalog/api-${page}.json`:id?`work/quadis-catalog/details/${id}.html`:null;
  if(local){try{return await fs.readFile(local,"utf8");}catch{}}
  let lastError;for(let attempt=1;attempt<=3;attempt++){try{const r=await fetch(url,{headers:{"user-agent":ua,"accept-language":"es-ES,es;q=0.9"},signal:AbortSignal.timeout(30000)});if(!r.ok)throw new Error(`${r.status} ${url}`);return r.text();}catch(error){lastError=error;await sleep(600*attempt);}}throw lastError;
}

const urls=[];
let expected=0;
for(let page=1;page<=10;page++){
  const payload=JSON.parse(await get(`${BASE}/api-vehicles/coches-renting?page=${page}&limit=14`));
  expected=Number(payload.total_count);
  const $=cheerio.load(payload.html);
  $(".car-card a[href*='/coches-renting/']").each((_,a)=>urls.push(new URL($(a).attr("href"),BASE).href));
  if(new Set(urls).size>=expected)break;
  await sleep(300);
}

const products=[];
for(const [index,url] of [...new Set(urls)].entries()){
  const $=cheerio.load(await get(url));
  const raw=$("contact-renting-modal[\\:vehicle], contact-modal[\\:vehicle]").first().attr(":vehicle");
  if(!raw){console.error(`Sin datos estructurados: ${url}`);continue;}
  const v=JSON.parse(raw);
  products.push({
    external_id:String(v.id), source_url:url, provider:"Quadis Empresas", brand:v.make, model:v.model,
    version:v.version, full_name:v.fullname, body_type:v.category?.name??null, fuel:v.fuel??null,
    transmission:v.transmission??null, drive:v.driveTrain??null, power_cv:v.powerCV??null,
    doors:v.doors??null, seats:v.seats??null, consumption:v.consumption??null,
    emissions_label:String(v.environmentalLabel??"").replace("environmental-","").toUpperCase()||null,
    color:v.color??null, availability:v.availability??"Consultar", audiences:(v.tags??[]).filter(tag=>["particulares","autonomos","empresas"].includes(tag)),
    prices:(v.pricesRenting??[]).map(price=>({monthly_price_inc_vat:Number(price.price),monthly_price_ex_vat:Math.round(Number(price.price)/1.21),annual_km:Number(String(price.kilometers).replace(/\D/g,"")),duration_months:Number(price.months)})),
    coverage:["Mantenimiento y reparaciones mecánicas","Neumáticos según plazo y kilómetros contratados","Seguro a todo riesgo","Gestión de multas e impuestos municipales","Asistencia en carretera 24/365","Sin entrada"],
    verified_at:new Date().toISOString(),
  });
  process.stdout.write(`\r${index+1}/${expected} fichas Quadis`);
  await sleep(350);
}
process.stdout.write("\n");
// Quadis uses the untagged/default catalogue for particulares. The audience
// tags only opt a product into the autonomos and empresas catalogues.
const counts={particular:products.length,autonomo:products.filter(p=>p.audiences.includes("autonomos")).length,empresa:products.filter(p=>p.audiences.includes("empresas")).length};
const output=path.resolve("outputs/quadis-catalog.json");
await fs.writeFile(output,`${JSON.stringify({generated_at:new Date().toISOString(),expected_base_products:expected,base_product_count:products.length,audience_counts:counts,image_policy:"No contiene imágenes ni URLs de imágenes",products},null,2)}\n`);
console.log(`Quadis: ${products.length} productos; P ${counts.particular}, A ${counts.autonomo}, E ${counts.empresa}`);
if(products.length!==36||counts.particular!==36||counts.autonomo!==32||counts.empresa!==31)process.exitCode=2;
