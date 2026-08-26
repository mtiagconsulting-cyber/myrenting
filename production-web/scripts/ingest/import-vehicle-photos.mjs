import fs from "node:fs/promises";
import path from "node:path";
import { execFileSync } from "node:child_process";
import sharp from "sharp";

const zip=process.argv[2]??"/Users/matthiasthomassen/Downloads/fotos_organizadas.zip";
const inventory=JSON.parse(await fs.readFile("src/data/imported-inventory.json","utf8"));
const entries=execFileSync("unzip",["-Z1",zip],{encoding:"utf8",maxBuffer:10_000_000}).trim().split("\n");
const imageEntries=entries.filter(entry=>/\.(png|jpe?g|webp)$/i.test(entry));
const folders=new Map();
for(const entry of imageEntries){const parts=entry.split("/");const provider=parts[1];const folder=parts[2];const key=`${provider}/${folder}`;if(!folders.has(key))folders.set(key,[]);folders.get(key).push(entry);}

const normalize=value=>value.normalize("NFD").replace(/[\u0300-\u036f]/g,"").toUpperCase().replace(/[^A-Z0-9]/g,"");
const slug=value=>value.normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");
const folderRows=[...folders].map(([key,files])=>{const [provider,name]=key.split("/");return{key,provider,name,normalized:normalize(name),files};});

const generatedPhotos={
  "veh-quadis-494501":"generated-mercedes-benz-gla-200d",
  "veh-quadis-paper-nissan-interstar-furgon-n1-l2h2-3-5t-dci-96kw-130cv-6m-t-fwd-acenta-12":"generated-nissan-interstar",
  "veh-quadis-paper-mercedes-benz-gla-gla-200-d-amg-line-advanced-plus-ayvens":"generated-mercedes-benz-gla-200d",
};

const generatedGallery=base=>({
  hero:`/vehicle-images/${base}-hero.webp`,
  card:`/vehicle-images/${base}-card.webp`,
  interior:`/vehicle-images/${base}-hero.webp`,
  trunk:`/vehicle-images/${base}-hero.webp`,
  compare:`/vehicle-images/${base}-card.webp`,
  sourceFolder:`Generada/${base}`,
});

function folderFor(vehicle){
  if(vehicle.id==="veh-kia-niro-concept-my27")return folderRows.find(row=>row.provider==="Quadis"&&row.normalized==="KIANIRO");
  if(vehicle.id.startsWith("veh-quadis-paper-")){
    const paperModelKey=normalize(vehicle.brand+vehicle.model);
    const exactPaperFolder=folderRows.find(row=>row.provider==="Quadis"&&row.normalized===paperModelKey);
    if(exactPaperFolder)return exactPaperFolder;
    const compatiblePaperFolder=folderRows.find(row=>row.provider==="Quadis"&&(row.normalized.startsWith(paperModelKey+"_")||row.normalized.startsWith(paperModelKey)));
    if(compatiblePaperFolder)return compatiblePaperFolder;
  }
  const provider=vehicle.id.startsWith("veh-quadis-")?"Quadis":"MRenting";
  const externalId=vehicle.id.split("-").at(-1);
  const exact=folderRows.find(row=>row.provider===provider&&new RegExp(`_${externalId}$`).test(row.name));
  if(exact)return exact;
  const modelKey=normalize(vehicle.brand+vehicle.model);
  return folderRows.find(row=>row.provider===provider&&(row.normalized===modelKey||row.normalized.startsWith(modelKey+"PARTICULAR")||row.normalized.startsWith(modelKey+"AUTONOMO")||row.normalized.startsWith(modelKey+"EMPRESA")))
    ??folderRows.find(row=>row.provider===provider&&(row.normalized.startsWith(modelKey)||modelKey.startsWith(row.normalized)));
}

function preferred(files,kind){
  const matching=files.filter(file=>new RegExp(`_${kind}_`,"i").test(file));
  return (matching.length?matching:files).sort()[0];
}

const used=new Map();
for(const vehicle of inventory.vehicles){const folder=folderFor(vehicle);if(folder)used.set(folder.key,folder);}
const outDir=path.resolve("public/vehicle-images");
await fs.mkdir(outDir,{recursive:true});
const galleries={};
let processed=0;
for(const folder of used.values()){
  const base=slug(folder.key);
  const exterior=preferred(folder.files,"delantera");
  const interior=preferred(folder.files,"interior");
  const rear=preferred(folder.files,"trasera");
  const roles=[
    {name:"hero",source:exterior,width:1280,quality:78},
    {name:"card",source:exterior,width:720,quality:76},
    {name:"interior",source:interior,width:1100,quality:76},
    {name:"trunk",source:rear,width:1000,quality:76},
  ];
  const result={};
  for(const role of roles){
    const filename=`${base}-${role.name}.webp`;
    const buffer=execFileSync("unzip",["-p",zip,role.source],{maxBuffer:20_000_000});
    await sharp(buffer).rotate().resize({width:role.width,withoutEnlargement:true}).webp({quality:role.quality,effort:4}).toFile(path.join(outDir,filename));
    result[role.name]=`/vehicle-images/${filename}`;
  }
  result.compare=result.card;
  galleries[folder.key]=result;
  processed++;
  process.stdout.write(`\r${processed}/${used.size} galerías`);
}
process.stdout.write("\n");

const manifest={};
const missing=[];
for(const vehicle of inventory.vehicles){
  const generatedBase=generatedPhotos[vehicle.id];
  if(generatedBase){manifest[vehicle.id]=generatedGallery(generatedBase);continue;}
  const folder=folderFor(vehicle);
  if(!folder){missing.push(vehicle.id);continue;}
  manifest[vehicle.id]={...galleries[folder.key],sourceFolder:folder.key};
}
await fs.writeFile("src/data/photo-manifest.json",`${JSON.stringify({generatedAt:new Date().toISOString(),source:path.basename(zip),vehicleCount:Object.keys(manifest).length,missing,photos:manifest},null,2)}\n`);
console.log(`Fotos vinculadas: ${Object.keys(manifest).length}/${inventory.vehicles.length}. Sin foto: ${missing.length}.`);
if(missing.length)console.log(missing.join("\n"));
