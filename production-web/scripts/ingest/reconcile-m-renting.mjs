import fs from "node:fs/promises";
import * as cheerio from "cheerio";

const file="outputs/m-renting-offers.json";
const payload=JSON.parse(await fs.readFile(file,"utf8"));
const expected={particular:47,autonomo:61,empresa:61};
const pages={particular:4,autonomo:6,empresa:6};
const existing=new Set(payload.offers.map(offer=>`${offer.audience}:${offer.external_id}`));
const clean=(value="")=>value.replace(/\s+/g," ").trim();
const amount=(value="")=>Number(value.replace(/[^\d,]/g,"").replace(",","."))||null;

for(const [audience,pageCount] of Object.entries(pages)){
  for(let page=1;page<=pageCount;page++){
    const $=cheerio.load(await fs.readFile(`work/m-renting-listings/${audience}-${page}.html`,"utf8"));
    $("article[data-id-product]").each((_,article)=>{
      const id=$(article).attr("data-id-product");
      if(!id||existing.has(`${audience}:${id}`))return;
      const href=$(article).find("a[href]").first().attr("href")?.split("#")[0]??null;
      const originalHref=$(article).find("a[href]").first().attr("href")??"";
      const title=clean($(article).find("img[alt]").first().attr("alt")?.split("|")[0]??$(article).text());
      const brand=clean($(article).find(".manufacturer").first().text())||title.split(" ")[0];
      const model=clean(title.toUpperCase().startsWith(brand.toUpperCase())?title.slice(brand.length):title);
      const advertised=amount($(article).find(".price").first().text());
      const annualKm=Number(originalHref.match(/kms_al_ano-(\d+)/)?.[1]??10000);
      const duration=Number(originalHref.match(/plazos-(\d+)_meses/)?.[1]??60);
      const inc=audience==="particular"?advertised:advertised===null?null:Number((advertised*1.21).toFixed(2));
      const ex=audience==="particular"?(advertised===null?null:Number((advertised/1.21).toFixed(2))):advertised;
      payload.offers.push({provider:"M-Automoción / M-Renting",audience,source_url:href,external_id:id,brand,model,version:clean($(article).find(".product-desc").first().text()),status:"NUEVO",body_type:null,fuel:null,transmission:null,power:null,emissions_label:null,doors:null,seats:null,color:null,annual_km:annualKm,duration_months:duration,monthly_price_ex_vat:ex,monthly_price_inc_vat:inc,advertised_price:advertised,advertised_tax_label:audience==="particular"?"IVA incluido":"+ IVA",vat_included_in_advertised_price:audience==="particular",initial_payment_eur:0,availability:"En stock",coverage:[],verified_at:new Date().toISOString(),data_quality_note:"Ficha de detalle no disponible durante la extracción; datos recuperados de la tarjeta del catálogo."});
      existing.add(`${audience}:${id}`);
    });
  }
}
payload.count=payload.offers.length;
payload.reconciled_at=new Date().toISOString();
payload.reconciliation=Object.fromEntries(Object.entries(expected).map(([audience,count])=>[audience,{expected:count,actual:payload.offers.filter(o=>o.audience===audience).length}]));
await fs.writeFile(file,`${JSON.stringify(payload,null,2)}\n`);
const columns=["provider","audience","external_id","brand","model","version","body_type","fuel","transmission","power","emissions_label","doors","seats","color","annual_km","duration_months","monthly_price_ex_vat","monthly_price_inc_vat","advertised_price","advertised_tax_label","vat_included_in_advertised_price","initial_payment_eur","availability","source_url","verified_at","data_quality_note"];
const csvCell=value=>{const text=value==null?"":String(value);return /[",\n]/.test(text)?`"${text.replaceAll('"','""')}"`:text;};
const csv=[columns.join(","),...payload.offers.map(offer=>columns.map(column=>csvCell(offer[column])).join(","))].join("\n");
await fs.writeFile("outputs/m-renting-offers.csv",`${csv}\n`);
console.log(payload.reconciliation);
if(Object.values(payload.reconciliation).some(row=>row.expected!==row.actual))process.exitCode=2;
