# -*- coding: utf-8 -*-
"""
CAPA 2 · CONSTRUIR CATÁLOGO
Lee:   data/raw/*.json            (ofertas scrapeadas: M Automoción, Quadis, Kia...)
       data/master/ofertas-manuales.json  (overrides a mano — GANAN)
       data/master/modelos.json    (specs: potencia, etiqueta, consumo, plazas, imagen)
Escribe: data/build/catalogo.json  (lo único que consumen los generadores)

Reglas:
 - Se agrupa por modelo (make+model). El precio del modelo = el más barato disponible.
 - ofertas-manuales GANA sobre lo scrapeado si coinciden make+model+tipo.
 - Se caducan ofertas sin precio (precio_desde<=0) salvo que sean manuales.
"""
import json, os, glob, re, unicodedata, collections, datetime
import pathlib as _pl; REPO=str(_pl.Path(__file__).resolve().parents[2])

def norm(s): return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()).strip()
def slug(s): return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()).strip('-')

def load(p, default):
    return json.load(open(p,encoding='utf-8')) if os.path.exists(p) else default

# --- 1. ofertas: raw + manuales ---
raw=[]
for f in sorted(glob.glob(f"{REPO}/data/raw/*.json")):
    raw += load(f,[])
manuales=[o for o in load(f"{REPO}/data/master/ofertas-manuales.json",[]) if o.get('precio_desde',0)>0]
modelos=load(f"{REPO}/data/master/modelos.json",{})
# detalle Quadis (specs + FAQ) scrapeado aparte -> {MAKE|MODEL: {especificaciones, faq}}
quadis_det=load(f"{REPO}/data/master/quadis-detalle.json",{})
def _qdet(make,model):
    return quadis_det.get(f"{(make or '').upper()}|{(model or '').upper()}")

# índice de overrides manuales por (make,model,tipo)
man_idx={ (norm(o.get('make')),norm(o.get('model')),o.get('tipo')): o for o in manuales }

ofertas=[o for o in raw if o.get('precio_desde',0)>0]
# aplicar overrides manuales (sustituyen / se añaden)
seen=set()
final=[]
for o in ofertas:
    k=(norm(o.get('make')),norm(o.get('model')),o.get('tipo'))
    if k in man_idx:
        if k not in seen: final.append(man_idx[k]); seen.add(k)
    else:
        final.append(o)
for k,o in man_idx.items():
    if k not in seen: final.append(o); seen.add(k)

# --- 2. agrupar por modelo ---
cat={}
for o in final:
    make=(o.get('make') or '').strip(); model=(o.get('model') or '').strip()
    if not make or not model: continue
    key=f"{make.upper()}||{model.upper()}"
    m=cat.setdefault(key,{"make":make.title(),"model":model.title(),"slug":slug(f"{make} {model}"),
        "precio_desde":10**9,"ofertas":[],"tipos":set(),"fuentes":set(),"detalle":None})
    m["ofertas"].append({k:o.get(k) for k in ("tipo","version","fuel","precio_desde","duracion","km","url","image","combinaciones")})
    m["precio_desde"]=min(m["precio_desde"],o.get("precio_desde",10**9))
    if o.get("tipo"): m["tipos"].add(o["tipo"])
    if o.get("fuente"): m["fuentes"].add(o["fuente"])
    # detalle a nivel modelo: M Automoción lo trae en la oferta; Quadis, del mapa
    if not m["detalle"]:
        m["detalle"]=o.get("detalle") or _qdet(make,model)

# --- 3. enriquecer con specs de modelos.json (match normalizado) ---
spec_norm={ norm(k.replace('||',' ')):v for k,v in modelos.items() }
enr=0
for key,m in cat.items():
    sp=modelos.get(key) or spec_norm.get(norm(m['make']+' '+m['model'])) or spec_norm.get(norm(m['model'])) or {}
    m["specs"]={
      "potencia": sp.get("potencia"),
      "etiqueta_dgt": sp.get("etiqueta_dgt"),
      "combustible": (sp.get("fuels") or [None])[0],
      "consumo_l100": sp.get("consumo_l100"),
      "consumo_kwh100": sp.get("consumo_kwh100"),
      "plazas": sp.get("asientos"),
      "category": sp.get("category"),
      "imagen": sp.get("imagen_local") or f"/img/modelos/{m['slug']}.webp",
      "descripcion": sp.get("descripcion"),
    }
    if sp: enr+=1
    m["tipos"]=sorted(m["tipos"]); m["fuentes"]=sorted(m["fuentes"])

os.makedirs(f"{REPO}/data/build",exist_ok=True)
out={"generado": datetime.datetime.now().isoformat(timespec="seconds"),
     "n_modelos":len(cat),"n_ofertas":len(final),"modelos":cat}
json.dump(out, open(f"{REPO}/data/build/catalogo.json","w",encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"catalogo.json: {len(cat)} modelos, {len(final)} ofertas ({enr} con specs). Overrides manuales: {len(man_idx)}")
