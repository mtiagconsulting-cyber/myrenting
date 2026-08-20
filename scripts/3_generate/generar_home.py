# -*- coding: utf-8 -*-
"""
Genera index.html a partir de templates/home.html + data/build/catalogo.json.
El DISEÑO vive en templates/home.html (marcador /*__CARS__*/).
Los DATOS vienen del catálogo. Así la home sobrevive a cada regeneración.
"""
import json, re
import pathlib as _pl; REPO=str(_pl.Path(__file__).resolve().parents[2])
cat=json.load(open(f"{REPO}/data/build/catalogo.json",encoding='utf-8'))["modelos"]
tpl=open(f"{REPO}/templates/home.html",encoding='utf-8').read()

def consumo(s):
    if s.get('consumo_l100'): return f"{str(s['consumo_l100']).replace('.',',')} L/100"
    if s.get('consumo_kwh100'): return f"{str(s['consumo_kwh100']).replace('.',',')} kWh/100"
    return "—"

cars=[]
for k,m in sorted(cat.items(), key=lambda kv:kv[1]['precio_desde']):
    s=m.get("specs") or {}
    esp=(m.get("detalle") or {}).get("especificaciones") or {}
    trans=esp.get("TRANSMISIÓN") or esp.get("TRANSMISION") or esp.get("Cambio") or "—"
    # tipo más barato
    tipo_min=min(m['ofertas'], key=lambda o:o.get('precio_desde',10**9)) if m['ofertas'] else {}
    cars.append({
      "slug": m['slug'],
      "t": f"{m['make']} {m['model']}",
      "ver": (tipo_min.get('version') or f"{m['make']} {m['model']}"),
      "fuel": s.get('combustible') or "—",
      "cat": s.get('category') or "—",
      "q": round(m['precio_desde']),
      "img": s.get('imagen') or f"/img/modelos/{m['slug']}.webp",
      "fuentes": m.get('fuentes') or [],
      "ofertas": len(m['ofertas']),
      "minTipo": tipo_min.get('tipo') or "autonomo",
      "plazo": tipo_min.get('duracion') or 60,
      "cv": s.get('potencia') or "—",
      "trans": trans,
      "cons": consumo(s),
      "seats": (f"{s['plazas']} plazas" if s.get('plazas') else "—"),
      "dgt": s.get('etiqueta_dgt') or "—",
    })

# La portada enseña una selección manejable. El catálogo completo sigue
# disponible en la pestaña Catálogo y en todas las páginas de marca/categoría.
# La selección combina precio competitivo y variedad de marcas.
featured=[]
seen_brands=set()
for car in cars:
    brand=car["t"].split()[0].lower()
    if brand not in seen_brands:
        featured.append(car)
        seen_brands.add(brand)
    if len(featured)==12:
        break

out=tpl.replace("/*__CARS__*/", json.dumps(cars, ensure_ascii=False))
out=out.replace("/*__FEATURED__*/", json.dumps(featured, ensure_ascii=False))
open(f"{REPO}/index.html","w",encoding='utf-8').write(out)
print(f"index.html generado desde plantilla · {len(cars)} coches")
