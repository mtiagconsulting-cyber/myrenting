import fs from "node:fs/promises";
import * as cheerio from "cheerio";

const audit=JSON.parse(await fs.readFile("outputs/cloudflare-public-audit.json","utf8"));
const blogUrls=audit.all_urls.filter(url=>new URL(url).pathname.startsWith("/blog/")&&!url.endsWith("/index.html"));
const articles=[];
for(const [index,url] of blogUrls.entries()){
  const response=await fetch(url,{signal:AbortSignal.timeout(20000)});
  if(!response.ok)throw new Error(`${response.status} ${url}`);
  const $=cheerio.load(await response.text());
  const content=$(".container").first().length?$(".container").first():$("main").first();
  content.find("script,style,form,.cta-box,.nav,.footer").remove();
  content.find("a").each((_,element)=>{const href=$(element).attr("href");if(href?.startsWith("/"))$(element).attr("href",href.replace(/\.html$/,""));});
  articles.push({slug:new URL(url).pathname.split("/").at(-1),url,title:$("title").text().trim(),description:$("meta[name='description']").attr("content")??"",headline:$("h1").first().text().trim(),intro:$(".hero p").first().text().trim(),html:content.html()??""});
  process.stdout.write(`\r${index+1}/${blogUrls.length} artículos`);
}
process.stdout.write("\n");
await fs.writeFile("src/data/legacy-articles.json",`${JSON.stringify({generatedAt:new Date().toISOString(),articles},null,2)}\n`);

const legalSources=[{source:"aviso-legal.html",slug:"aviso-legal"},{source:"politica-privacidad.html",slug:"privacidad"},{source:"politica-cookies.html",slug:"cookies"}];
const legal=[];
for(const item of legalSources){const url=`https://myrenting.es/${item.source}`;const response=await fetch(url,{signal:AbortSignal.timeout(20000)});if(!response.ok)throw new Error(`${response.status} ${url}`);const $=cheerio.load(await response.text());const content=$("main").first().length?$("main").first():$(".container").first();content.find("script,style,form,.nav,.footer,header").remove();legal.push({...item,title:$("title").text().trim(),description:$("meta[name='description']").attr("content")??"",headline:$("h1").first().text().trim(),html:content.html()??""});}
await fs.writeFile("src/data/legacy-legal.json",`${JSON.stringify({generatedAt:new Date().toISOString(),pages:legal},null,2)}\n`);

const inventory=JSON.parse(await fs.readFile("src/data/imported-inventory.json","utf8"));
const normalize=value=>value.normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/[^a-z0-9]/g,"");
const oldModelUrls=audit.sitemaps["sitemap-modelos.xml"].urls;
const redirects=[];
for(const url of oldModelUrls){
  const pathname=new URL(url).pathname;
  const key=normalize(pathname.replace(/^\/renting-/,"").replace(/\.html$/,"").replace(/-at$/,""));
  const candidates=inventory.vehicles.filter(vehicle=>{const vehicleKey=normalize(vehicle.brand+vehicle.model);return vehicleKey===key||vehicleKey.startsWith(key)||key.startsWith(vehicleKey);});
  const vehicle=candidates.find(item=>item.id.startsWith("veh-quadis-"))??candidates.find(item=>item.id.startsWith("veh-m-particular-"))??candidates[0];
  redirects.push({source:pathname,destination:vehicle?`/coches/${vehicle.slug}?publico=particular`:"/coches",permanent:true});
}
const hubMap={
  "renting-autonomos.html":"/coches?publico=autonomo","renting-empresas.html":"/coches?publico=empresa","renting-particulares.html":"/coches?publico=particular",
  "renting-electricos.html":"/renting-electricos","renting-hibridos.html":"/renting-hibridos","renting-suv.html":"/renting-suv","renting-urbano.html":"/categorias/urbanos","renting-furgoneta.html":"/categorias/furgonetas","renting-hatchback.html":"/categorias/urbanos","renting-crossover.html":"/categorias/suv",
  "renting-gasolina.html":"/coches?combustible=gasolina","renting-diesel.html":"/coches?combustible=diésel","renting-hibridos-enchufables.html":"/coches?combustible=híbrido%20enchufable","renting-etiqueta-c.html":"/coches","renting-etiqueta-cero.html":"/renting-electricos","renting-etiqueta-eco.html":"/renting-hibridos"
};
for(const url of audit.sitemaps["sitemap-hubs.xml"].urls){const pathname=new URL(url).pathname;const filename=pathname.slice(1);const brand=filename.match(/^renting-(.+)\.html$/)?.[1];const destination=hubMap[filename]??(brand?`/marcas/${brand}`:"/coches");redirects.push({source:pathname,destination,permanent:true});}
redirects.push({source:"/blog/index.html",destination:"/blog",permanent:true},{source:"/aviso-legal.html",destination:"/legal/aviso-legal",permanent:true},{source:"/politica-privacidad.html",destination:"/legal/privacidad",permanent:true},{source:"/politica-cookies.html",destination:"/legal/cookies",permanent:true});
await fs.writeFile("src/data/legacy-redirects.json",`${JSON.stringify(redirects,null,2)}\n`);
console.log(`${articles.length} artículos, ${legal.length} páginas legales y ${redirects.length} redirecciones preparados.`);
