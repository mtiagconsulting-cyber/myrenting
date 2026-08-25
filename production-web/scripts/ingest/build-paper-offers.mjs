import fs from "node:fs/promises";
import path from "node:path";

const km5 = [10000, 15000, 20000, 25000, 30000];
const km6 = [5000, 10000, 15000, 20000, 25000, 30000];
const quadisCoverage = [
  "Mantenimiento y reparaciones mecánicas",
  "Neumáticos según plazo y kilómetros contratados",
  "Seguro a todo riesgo",
  "Gestión de multas e impuestos municipales",
  "Asistencia en carretera 24/365",
  "Sin entrada",
];
const kiaCoverage = [
  "Reposición ilimitada de neumáticos",
  "Gestión de flota, matriculación e impuestos",
  "Asistencia en carretera",
  "Mantenimiento y reparaciones en red oficial Kia",
  "Seguro a todo riesgo sin franquicia",
  "Gestión online de multas",
];

const rows = (kms, durations, exVat, incVat) => kms.flatMap((annualKm, row) =>
  durations.flatMap((durationMonths, column) => {
    const ex = exVat?.[row]?.[column] ?? null;
    const inc = incVat?.[row]?.[column] ?? null;
    return ex === null && inc === null ? [] : [{ annual_km: annualKm, duration_months: durationMonths, monthly_price_ex_vat: ex, monthly_price_inc_vat: inc }];
  }),
);
const q = (data) => ({ provider: "Quadis Empresas", audiences: ["particular", "autonomo", "empresa"], coverage: quadisCoverage, source_document: "BROKERS 25.08.2026.pdf", ...data });

const offers = [
  q({ brand:"Mercedes-Benz", model:"GLE Coupé", version:"GLE 300d 4MATIC Coupé", fuel:"Diésel mild-hybrid 48V", transmission:"Automático", power_cv:269, emissions_label:"ECO", colors:["Blanco","Azul","Gris","Plata"], availability:"Stock; cuotas orientativas", prices:rows(km5,[36,48,60],[[1382,1249,1163],[1444,1303,1204],[1487,1347,1347],[1528,1416,1416],[1601,1464,1464]],[[1672,1511,1407],[1747,1577,1457],[1799,1630,1630],[1849,1713,1713],[1937,1771,1771]]) }),
  q({ brand:"Mercedes-Benz", model:"GLE Coupé", version:"GLE 350 de 4MATIC Coupé", fuel:"Híbrido enchufable diésel", transmission:"Automático", power_cv:333, emissions_label:"CERO", colors:["Blanco","Azul","Gris","Negro"], availability:"Stock; cuotas orientativas", prices:rows(km5,[36,48,60],[[1486,1342,1250],[1555,1402,1293],[1602,1448,1372],[1646,1528,1451],[1732,1579,1515]],[[1798,1624,1513],[1882,1696,1565],[1938,1752,1660],[1992,1849,1756],[2096,1911,1833]]) }),
  q({ provider:"Quadis Empresas — ARVAL", campaign:"ARVAL", brand:"Nissan", model:"Qashqai", version:"DIG-T 103kW (140CV) mHEV 4x2 Acenta", fuel:"Gasolina microhíbrida", transmission:"Manual", power_cv:140, emissions_label:"ECO", colors:["Deep Ocean Blue"], availability:">100 unidades en stock", prices:rows(km5,[48,60],[[336,324],[356,345],[379,373],[406,402],[431,429]],[[407,392],[431,417],[459,451],[491,486],[522,519]]) }),
  q({ provider:"Quadis Empresas — ARVAL", campaign:"ARVAL", brand:"Opel", model:"Corsa", version:"1.2T XHL 74kW (100CV) GS", fuel:"Gasolina", transmission:"Manual", power_cv:100, emissions_label:"C", seats:5, colors:["Karbon Black","Grafik Grey"], availability:"Entrega prevista en septiembre", prices:rows(km5,[48,60],[[257,245],[271,261],[289,285],[311,307],[330,329]],[[311,296],[328,316],[350,345],[376,371],[399,398]]) }),
  q({ provider:"Quadis Empresas — ALPHABET", campaign:"ALPHABET — Blanco", brand:"Opel", model:"Corsa", version:"1.2T XHL 74kW (100CV) GS — Blanco", fuel:"Gasolina", transmission:"Manual", power_cv:100, emissions_label:"C", seats:5, colors:["Blanco"], availability:"Stock hasta fin de existencias", prices:rows(km5,[24,36,48,60],[[267,243,241,229],[277,256,256,244],[299,275,276,273],[310,290,307,297],[333,319,331,324]],[[323,294,292,277],[335,310,310,295],[362,333,334,330],[375,351,371,359],[403,386,401,392]]) }),
  q({ provider:"Quadis Empresas — ARVAL", campaign:"ARVAL", brand:"Peugeot", model:"208", version:"Allure Gasolina 100 S&S 6 Vel. Manual Turbo", fuel:"Gasolina", transmission:"Manual", power_cv:100, emissions_label:"C", seats:5, colors:["Blanco Okenite"], availability:"Entrega prevista en septiembre", prices:rows(km5,[48,60],[[243,234],[258,250],[276,273],[298,295],[317,317]],[[294,283],[312,303],[334,330],[361,357],[384,384]]) }),
  q({ brand:"Nissan", model:"Juke", version:"1.6 Hybrid 105kW (145CV) N-Connecta", fuel:"Híbrido gasolina", transmission:"Automático", power_cv:145, emissions_label:"ECO", colors:["Blanco"], availability:"Stock", prices:rows(km5,[36,48,60],[[321,321,319],[338,337,334],[356,353,348],[381,377,373],[406,403,397]],[[388,388,386],[409,408,404],[431,427,421],[461,456,451],[491,488,480]]) }),
  q({ brand:"Maserati", model:"Grecale", version:"L4 MHEV 300CV AWD", fuel:"Gasolina microhíbrida", transmission:"Automático", power_cv:300, emissions_label:"ECO", colors:["Bianco Astro","Nero Tempesta","Giorgio Lava"], availability:"Stock hasta fin de existencias", prices:rows(km5,[36,48,60],[[1405,1290,1191],[1447,1335,1229],[1499,1383,1275],[1550,1434,1326],[1606,1496,1380]],[[1700,1561,1441],[1751,1615,1487],[1814,1673,1543],[1876,1735,1604],[1943,1810,1670]]) }),
  q({ audiences:["empresa"], brand:"Mercedes-Benz", model:"GLC", version:"GLC 220 d 4MATIC (2022)", fuel:"Diésel", transmission:"Automático", colors:["Blanco Polar"], availability:"Stock hasta fin de existencias; solo empresa", prices:rows(km5,[48,60],[[892,831],[929,872],[976,926],[1028,983],[1082,1039]],[[1079,1006],[1124,1055],[1181,1120],[1244,1189],[1309,1257]]) }),
  q({ audiences:["empresa"], brand:"Mercedes-Benz", model:"GLC Coupé", version:"GLC 300 de 4MATIC (2023)", fuel:"Híbrido enchufable", transmission:"Automático", emissions_label:"CERO", colors:["Negro Obsidiana"], availability:"Stock hasta fin de existencias; solo empresa", prices:rows(km5,[48,60],[[963,892],[1000,934],[1048,988],[1100,1046],[1156,1104]],[[1165,1079],[1210,1130],[1268,1195],[1331,1266],[1399,1336]]) }),
  q({ audiences:["empresa"], brand:"Mercedes-Benz", model:"GLC Coupé", version:"GLC 200 4MATIC (2023)", fuel:"Gasolina", transmission:"Automático", colors:["Gris Grafito"], availability:"Solo empresa", prices:rows(km5,[48,60],[[930,866],[970,910],[1019,966],[1073,1025],[1129,1085]],[[1125,1048],[1174,1101],[1233,1169],[1298,1240],[1425,1362]]) }),
  q({ audiences:["autonomo","empresa"], brand:"Nissan", model:"Interstar Furgón", version:"N1 L2H2 (3,5t) dCi 96kW (130CV) 6M/T FWD Acenta", fuel:"Diésel", transmission:"Manual", power_cv:130, colors:["Blanco Mineral Sólido"], availability:"Stock", prices:rows(km5,[48,60],[[474,459],[506,489],[538,531],[576,569],[610,608]],[[574,555],[612,592],[651,643],[697,688],[738,736]]) }),
  q({ brand:"Skoda", model:"Fabia", version:"1.5 TSI 110kW (150CV) DSG Plus", fuel:"Gasolina", transmission:"Automático", power_cv:150, emissions_label:"C", colors:["Blanco Candy","Negro Mágico Efecto Perla"], availability:"Entrega prevista en octubre", prices:rows(km5,[48,60],[[294,286],[311,305],[332,332],[358,358],[381,384]],[[356,346],[376,369],[402,402],[433,433],[461,465]]) }),
  q({ audiences:["autonomo","empresa"], brand:"Mercedes-Benz", model:"Citan", version:"110 CDI 70kW Furgón Base Cargo", fuel:"Diésel", transmission:"Manual", power_cv:95, emissions_label:"C", colors:["Blanco"], availability:"Últimas unidades en stock", prices:rows(km5,[36,48,60],[[406,385,372],[432,409,394],[454,432,425],[474,461,454],[501,486,482]],[[491,466,450],[523,495,477],[549,523,514],[574,558,549],[606,588,583]]) }),
  q({ brand:"Audi", model:"A1", version:"Sportback Adrenalin 30 TFSI 85kW S tronic", fuel:"Gasolina", transmission:"Automático", power_cv:116, emissions_label:"C", colors:["Blanco Candy"], availability:"Stock", prices:rows(km5,[36,48,60],[[315,320,318],[333,336,333],[351,352,348],[374,374,372],[397,397,395]],[[381,387,385],[403,407,403],[425,426,421],[453,453,450],[480,480,478]]) }),
  q({ brand:"Ebro", model:"S800", version:"1.5 TGDI PHEV Luxury E-CVT — Gris", fuel:"Híbrido enchufable", transmission:"Automático", power_cv:279, emissions_label:"CERO", colors:["Gris"], availability:"Entrega aproximada 15 días", prices:rows(km5,[36,48,60],[[546,522,504],[573,549,532],[610,584,568],[644,617,605],[680,654,647]],[[661,632,610],[693,664,644],[738,707,687],[779,747,732],[823,791,783]]) }),
  q({ brand:"Ebro", model:"S800", version:"1.5 TGDI PHEV Luxury E-CVT — Blanco", fuel:"Híbrido enchufable", transmission:"Automático", power_cv:279, emissions_label:"CERO", colors:["Blanco"], availability:"Entrega inmediata", prices:rows(km5,[36,48,60],[[538,515,496],[564,541,525],[601,575,560],[635,609,596],[671,645,638]],[[651,623,600],[682,655,635],[727,696,678],[768,737,721],[812,780,772]]) }),
  q({ brand:"Honda", model:"CR-V", version:"2.0 i-MMD PHEV 4x2 Elegance Tech", fuel:"Híbrido enchufable", transmission:"Automático", power_cv:184, emissions_label:"CERO", colors:["Negro Cristal","Blanco Diamond Dust","Gris Urban Perlado","Azul Canyon"], availability:"Negro, gris y azul en stock; blanco previsto en octubre", prices:rows(km5,[36,48,60],[[446,461,464],[474,486,486],[501,511,508],[529,535,530],[557,560,552]],[[540,558,561],[574,588,588],[606,618,615],[640,647,641],[674,678,668]]) }),
  q({ provider:"Quadis Empresas — AYVENS", campaign:"AYVENS", brand:"Opel", model:"Mokka", version:"1.2T XHT Hybrid eDCT6 GS", fuel:"Gasolina híbrida", transmission:"Automático", power_cv:146, emissions_label:"ECO", colors:["Negro"], availability:"Stock", prices:rows(km5,[36,48,60],[[345,333,325],[358,345,335],[372,357,345],[391,376,364],[411,397,387]],[[417,403,393],[433,417,405],[450,432,417],[473,455,440],[497,480,468]]) }),
  q({ provider:"Quadis Empresas — AYVENS", campaign:"AYVENS — MY27", brand:"Kia", model:"Niro", version:"1.6 GDi HEV 102kW (139CV) Drive MY27", fuel:"Híbrido gasolina", transmission:"Automático", power_cv:139, emissions_label:"ECO", colors:["Snow White Pearl (metalizado)"], availability:"Entrega prevista en septiembre", prices:rows(km5,[36,48,60],[[324,320,315],[341,336,322],[359,351,345],[381,372,366],[404,395,388]],[[392,387,381],[413,407,390],[434,425,417],[461,450,443],[489,478,469]]) }),
  q({ provider:"Quadis Empresas — AYVENS", campaign:"AYVENS", brand:"Nissan", model:"Qashqai", version:"DIG-T 103kW (140CV) mHEV 4x2 Acenta", fuel:"Gasolina microhíbrida", transmission:"Manual", power_cv:140, emissions_label:"ECO", colors:["Deep Ocean Blue"], availability:">100 unidades en stock", prices:rows(km5,[36,48,60],[[319,318,315],[334,332,327],[349,345,339],[372,367,362],[395,392,384]],[[386,385,381],[404,402,396],[422,417,410],[450,444,438],[478,474,465]]) }),
  q({ provider:"Quadis Empresas — AYVENS", campaign:"AYVENS", brand:"Mercedes-Benz", model:"GLA", version:"GLA 200 d AMG Line Advanced Plus", fuel:"Diésel", transmission:"Automático 8G-DCT", power_cv:150, emissions_label:"C", colors:["Blanco Polar"], availability:">80 unidades; entrega prevista en octubre", data_note:"El correo y el equipamiento confirman Blanco/Blanco Polar; el texto Deep Ocean Blue de la creatividad se considera un error de plantilla.", prices:rows(km5,[36,48,60],[[476,467,458],[503,490,478],[529,514,499],[564,546,529],[598,577,564]],[[576,565,554],[609,593,578],[640,622,604],[682,661,640],[724,698,682]]) }),
];

const payload = { generated_at:new Date().toISOString(), image_policy:"No contiene imágenes ni URLs de imágenes", ended_campaigns:[
  {brand:"MG",model:"MG3",external_id:"515717",reason:"Campaña finalizada en la actualización de 10.08.2026"},
  {brand:"MG",model:"ZS",external_id:"523298",reason:"Campaña dada de baja en la actualización previa al 25.08.2026"},
  {brand:"MG",model:"ZS",external_id:"522422",reason:"Campaña dada de baja en la actualización previa al 25.08.2026"},
  {brand:"Kia",model:"Niro",campaign:"Modelo anterior — 100 € combustible",reason:"Fin de existencias comunicado el 25.08.2026"},
  {brand:"Kia",model:"Niro",external_id:"523390",reason:"Modelo anterior retirado por fin de existencias el 25.08.2026"},
], replaced_catalog_external_ids:["493813","514005","514117","523377","515717","523298","522422","523390"], offer_count:offers.length, price_combination_count:offers.reduce((sum, offer) => sum + offer.prices.length, 0), offers };
const output = path.resolve("outputs/quadis-kia-offers.json");
await fs.mkdir(path.dirname(output), { recursive:true });
await fs.writeFile(output, `${JSON.stringify(payload, null, 2)}\n`);
console.log(`Guardadas ${payload.offer_count} ofertas y ${payload.price_combination_count} combinaciones en ${output}`);
