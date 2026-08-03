# -*- coding: utf-8 -*-
"""
ENRIQUECER MODELOS (upsert) — hace que data/master/modelos.json cubra TODOS los coches.
Por cada modelo del catálogo:
  - si NO está en modelos.json -> lo AÑADE (con las specs que tengamos)
  - si SÍ está -> rellena solo los campos vacíos (no pisa lo que ya haya)
Fuente de specs: index.html (cars: potencia, etiqueta, combustible, consumo, plazas, imagen).
Es idempotente: se puede correr siempre.
"""
import json, re, unicodedata, os
import pathlib as _pl; REPO=str(_pl.Path(__file__).resolve().parents[2])
def norm(s): return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()).strip()
def slug(s): return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()).strip('-')

# --- fuente de specs: cars del index ---
h=open(f"{REPO}/index.html",encoding='utf-8').read()
s=h.index('const cars=[')+len('const cars='); cars,_=json.JSONDecoder().raw_decode(h[s:])
SRC={}
for c in cars:
    k=norm(c['t'])
    cons=c.get('cons') or ''
    l100=kwh=None
    mm=re.search(r'([\d,\.]+)\s*L/100',cons);  l100=float(mm.group(1).replace(',','.')) if mm else None
    mk=re.search(r'([\d,\.]+)\s*kWh',cons);     kwh=float(mk.group(1).replace(',','.')) if mk else None
    SRC[k]={
     "potencia": c.get('cv') if c.get('cv') not in ('','—') else None,
     "etiqueta_dgt": c.get('dgt') if c.get('dgt') not in ('','—') else None,
     "fuels": [c['fuel']] if c.get('fuel') not in ('','—') else None,
     "consumo_l100": l100, "consumo_kwh100": kwh,
     "asientos": int(re.sub(r'\D','',c.get('seats') or '') or 0) or None,
     "category": c.get('cat') if c.get('cat') not in ('','—') else None,
     "imagen_local": f"/img/modelos/{slug(c['t'])}.webp",
    }

# índice extra "sin espacios" para pescar claves sucias (CX-30 AT, eberlingo...)
SRC_DESP={ nk.replace(' ',''):v for nk,v in SRC.items() }
def find_src(nk):
    if nk in SRC: return SRC[nk]
    d=nk.replace(' ','')
    if d in SRC_DESP: return SRC_DESP[d]
    for sk,v in SRC_DESP.items():           # prefijo por si sobra un token (AT, plus...)
        if d.startswith(sk) or sk.startswith(d): return v
    return None

modelos=json.load(open(f"{REPO}/data/master/modelos.json",encoding='utf-8'))
cat=json.load(open(f"{REPO}/data/build/catalogo.json",encoding='utf-8'))["modelos"]

# índice normalizado de modelos.json existentes
idx={ norm(k.replace('||',' ')):k for k in modelos }

CAMPOS=["potencia","etiqueta_dgt","fuels","consumo_l100","consumo_kwh100","asientos","category","imagen_local"]
add=0; fill=0
for ck,m in cat.items():
    nk=norm(m['make']+' '+m['model'])
    src=find_src(nk) or find_src(norm(m['model']))
    # localizar (o crear) entrada en modelos.json
    key=idx.get(nk)
    if not key:
        key=f"{m['make'].upper()}||{m['model'].upper()}"
        modelos[key]={"imagen_local":f"/img/modelos/{m['slug']}.webp","precio_desde":m['precio_desde'],
                      "fuentes":m['fuentes'],"category":(src or {}).get('category')}
        idx[nk]=key; add+=1
    v=modelos[key]
    if src:
        for f in CAMPOS:
            if src.get(f) and not v.get(f):
                v[f]=src[f]; fill+=1

json.dump(modelos, open(f"{REPO}/data/master/modelos.json","w",encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"modelos.json: {len(modelos)} entradas | {add} añadidas | {fill} campos rellenados")
