# -*- coding: utf-8 -*-
"""
MIGRACIÓN ÚNICA (se corre una sola vez) de los ficheros antiguos a la estructura nueva.
NO scrapea. Solo reorganiza lo que ya existe.
  coches-specs.json        -> data/master/modelos.json   (+ potencia + etiqueta_dgt)
  ofertas-manuales.json    -> data/raw/mautomocion.json + data/raw/quadis.json  (split por fuente)
  (crea)                   -> data/master/ofertas-manuales.json  (SOLO overrides a mano: Kia, correcciones)
  (crea)                   -> data/master/ciudades-zbe.json      (dataset ZBE para GEO)
"""
import json, os, re, unicodedata, collections
import pathlib as _pl; REPO=str(_pl.Path(__file__).resolve().parents[2])

def norm(s):
    return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()).strip()

# ---------- 1) MODELOS (specs) ----------
specs=json.load(open(f"{REPO}/coches-specs.json",encoding='utf-8'))
# specs de potencia/etiqueta que sacamos: leerlas del index.html (cars) y del SPECS_MODELOS.csv
import csv
pot={}; dgt={}
# del CSV que generamos (marca,modelo,version,potencia,combustible,consumo,plazas)
with open(f"{REPO}/SPECS_MODELOS.csv",encoding='utf-8') as f:
    for r in csv.DictReader(f):
        k=norm(r['Marca'])+" "+norm(r['Modelo'])
        if r['Potencia'].strip() not in ('','—'): pot[k]=r['Potencia'].strip()
# etiqueta DGT desde index.html (cars llevan dgt)
h=open(f"{REPO}/index.html",encoding='utf-8').read()
try:
    import json as J; s=h.index('const cars=[')+len('const cars='); cars,_=J.JSONDecoder().raw_decode(h[s:])
    for c in cars:
        k=norm(c['t'])
        if c.get('dgt') and c['dgt']!='—': dgt[k]=c['dgt']
        # potencia por titulo tambien
        if c.get('cv') and c['cv']!='—': pot.setdefault(k,c['cv'])
except Exception as e:
    print("aviso: no pude leer cars de index.html:",e)

enriquecidos=0
for key,v in specs.items():
    if not isinstance(v,dict): continue
    marca,_,modelo = key.partition("||")
    nk=norm(marca)+" "+norm(modelo)
    # potencia
    if 'potencia' not in v:
        p = pot.get(nk) or pot.get(norm(modelo))
        if p: v['potencia']=p; enriquecidos+=1
    # etiqueta dgt
    if 'etiqueta_dgt' not in v:
        d = dgt.get(nk) or dgt.get(norm(modelo))
        if d: v['etiqueta_dgt']=d

os.makedirs(f"{REPO}/data/master",exist_ok=True)
json.dump(specs, open(f"{REPO}/data/master/modelos.json","w",encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"modelos.json: {len(specs)} modelos ({enriquecidos} con potencia añadida)")

# ---------- 2) OFERTAS -> raw split por fuente ----------
ofertas=json.load(open(f"{REPO}/ofertas-manuales.json",encoding='utf-8'))
by=collections.defaultdict(list)
for o in ofertas:
    fu=(o.get('fuente') or 'otras')
    slug={'M Automoción':'mautomocion','Quadis':'quadis'}.get(fu, norm(fu).replace(' ','-'))
    by[slug].append(o)
os.makedirs(f"{REPO}/data/raw",exist_ok=True)
for slug,items in by.items():
    json.dump(items, open(f"{REPO}/data/raw/{slug}.json","w",encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"data/raw/{slug}.json: {len(items)} ofertas")

# ---------- 3) OFERTAS-MANUALES (nuevo, solo overrides: Kia va aquí) ----------
manual_path=f"{REPO}/data/master/ofertas-manuales.json"
if not os.path.exists(manual_path):
    ejemplo=[{
      "fuente":"Kia Renting","tipo":"particular","make":"KIA","model":"NIRO",
      "version":"KIA NIRO HEV CONCEPT","fuel":"Híbrido","precio_desde":0,"duracion":60,"km":10000,
      "url":"","image":"","category":"SUV",
      "combinaciones":[{"km":10000,"meses":60,"precio":0}],
      "_nota":"PLANTILLA. Rellena aquí las ofertas de Kia u otras correcciones a mano. Estas GANAN sobre lo scrapeado."
    }]
    json.dump(ejemplo, open(manual_path,"w",encoding='utf-8'), ensure_ascii=False, indent=1)
    print("data/master/ofertas-manuales.json: creado (plantilla Kia)")

print("MIGRACIÓN OK")
