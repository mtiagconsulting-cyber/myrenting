# -*- coding: utf-8 -*-
"""
CAPA 2-3 · HUBS SEO (marca / etiqueta DGT / carrocería / combustible / plazas / segmento)
Lee:  data/build/catalogo.json
Cada hub LISTA los coches que cumplen un criterio (conjunto distinto por página =
contenido único). Publica en la raíz: renting-<criterio>.html + los añade al sitemap.

Puerta de calidad: un hub solo se genera si tiene >= MIN_COCHES modelos.
"""
import json, re, html as H, unicodedata
import pathlib as _pl; REPO=str(_pl.Path(__file__).resolve().parents[2]); DOMAIN="https://myrenting.es"
cat=json.load(open(f"{REPO}/data/build/catalogo.json",encoding='utf-8'))["modelos"]
e=H.escape
MIN_COCHES=3          # bajo este umbral no se publica (evita páginas thin)
MIN_MARCA=2

def slug(s):
    s=unicodedata.normalize("NFKD",str(s or "")).encode("ascii","ignore").decode().lower()
    return re.sub(r"-+","-",re.sub(r"[^a-z0-9]+","-",s)).strip("-")

MODS=list(cat.values())

def fuel_bucket(s):
    f=(s.get("combustible") or "").lower()
    if "eléctr" in f or "electric" in f: return "electricos"
    if "enchuf" in f or "phev" in f: return "hibridos-enchufables"
    if "híbr" in f or "hibr" in f: return "hibridos"
    if "diésel" in f or "diesel" in f: return "diesel"
    if "gasolina" in f: return "gasolina"
    return None

# ---- definición de hubs: (slug, título, H1, intro, filtro) ----
def build_hubs():
    hubs=[]
    # 2) marcas
    marcas={}
    for m in MODS: marcas.setdefault(m["make"],[]).append(m)
    for mk,ms in marcas.items():
        if len(ms)>=MIN_MARCA:
            hubs.append((f"renting-{slug(mk)}", f"Renting {mk}", f"Renting {mk}",
                f"Todos los modelos {mk} disponibles en renting, con cuota fija sin entrada y todo incluido. Compara precios reales y elige el tuyo.", ms))
    # 3a) etiqueta DGT
    for dgt,nom,txt in [("CERO","etiqueta CERO","Coches con etiqueta CERO: acceso total a cualquier ZBE, sin restricciones ni en episodios de contaminación."),
                        ("ECO","etiqueta ECO","Coches con etiqueta ECO: circulan por todas las Zonas de Bajas Emisiones sin limitaciones."),
                        ("C","etiqueta C","Coches nuevos con etiqueta C: acceso a las ZBE al ser vehículos nuevos, sin las prohibiciones de los antiguos.")]:
        ms=[m for m in MODS if (m.get("specs") or {}).get("etiqueta_dgt")==dgt]
        if len(ms)>=MIN_COCHES:
            hubs.append((f"renting-{slug(nom)}", f"Renting con {nom}", f"Renting con {nom}",
                txt+" Cuota fija, sin entrada y con seguro y mantenimiento incluidos.", ms))
    # 3b) carrocería
    cars_by_cat={}
    for m in MODS:
        c=(m.get("specs") or {}).get("category")
        if c: cars_by_cat.setdefault(c,[]).append(m)
    for c,ms in cars_by_cat.items():
        if len(ms)>=MIN_COCHES:
            hubs.append((f"renting-{slug(c)}", f"Renting de {c}", f"Renting de {c}",
                f"Los mejores {c} en renting: compara cuotas reales, specs y etiqueta de cada modelo. Sin entrada, todo incluido.", ms))
    # 3c) combustible
    fb={"electricos":("coches eléctricos","Renting de coches 100% eléctricos: etiqueta CERO, coste por km mínimo y acceso total a las ZBE."),
        "hibridos-enchufables":("coches híbridos enchufables","Renting de híbridos enchufables (PHEV): modo eléctrico en ciudad y autonomía de gasolina en viaje."),
        "hibridos":("coches híbridos","Renting de coches híbridos: consumos contenidos y etiqueta favorable para ciudad y carretera."),
        "diesel":("coches diésel","Renting de coches diésel nuevos: ideales para quien hace muchos kilómetros por carretera."),
        "gasolina":("coches de gasolina","Renting de coches de gasolina: mecánica sencilla y cuota ajustada.")}
    buckets={}
    for m in MODS:
        b=fuel_bucket(m.get("specs") or {})
        if b: buckets.setdefault(b,[]).append(m)
    for b,ms in buckets.items():
        if len(ms)>=MIN_COCHES:
            nom,txt=fb[b]
            hubs.append((f"renting-{b}", f"Renting de {nom}", f"Renting de {nom}", txt+" Cuota fija sin entrada.", ms))
    # 3d) plazas grandes
    ms7=[m for m in MODS if (m.get("specs") or {}).get("plazas") and int((m["specs"]["plazas"]))>=7]
    if len(ms7)>=MIN_COCHES:
        hubs.append(("renting-7-plazas","Renting de coches de 7 plazas","Renting de 7 plazas",
            "Coches de 7 plazas en renting para familias grandes o traslados: espacio, seguridad y cuota fija sin entrada.", ms7))
    # 5) segmento
    for seg,nom,txt in [("autonomo","autónomos","Renting para autónomos: 100% deducible, sin inmovilizar capital y con todo incluido en la cuota."),
                        ("empresa","empresas","Renting para empresas: flota flexible, deducible y sin gestión de mantenimiento ni seguros."),
                        ("particular","particulares","Renting para particulares: cuota fija con IVA incluido, seguro y mantenimiento, sin entrada.")]:
        ms=[m for m in MODS if seg in (m.get("tipos") or [])]
        if len(ms)>=MIN_COCHES:
            hubs.append((f"renting-{slug(nom)}", f"Renting para {nom}", f"Renting para {nom}", txt, ms))
    return hubs

def card(m):
    s=m.get("specs") or {}; name=f"{m['make']} {m['model']}"
    bits=[x for x in [s.get("combustible"), s.get("potencia"),
          (f"{s['plazas']} plazas" if s.get("plazas") else ""),
          (f"etiqueta {s['etiqueta_dgt']}" if s.get("etiqueta_dgt") else "")] if x]
    img=s.get("imagen") or f"/img/modelos/{m['slug']}.webp"
    return (f'<a class="c" href="/renting-{m["slug"]}.html"><img src="{img}" alt="Renting {e(name)}" loading="lazy">'
            f'<div class="cn">{e(name)}</div><div class="cs">{e(" · ".join(bits))}</div>'
            f'<div class="cp">desde <b>{round(m["precio_desde"])}€</b>/mes</div></a>')

def render(sl, title, h1, intro, ms):
    ms=sorted(ms, key=lambda m:m["precio_desde"])
    url=f"{DOMAIN}/{sl}.html"; desde=round(min(m["precio_desde"] for m in ms))
    grid="".join(card(m) for m in ms)
    ld={"@context":"https://schema.org","@graph":[
      {"@type":"ItemList","name":title,"numberOfItems":len(ms),"itemListElement":[
        {"@type":"ListItem","position":i+1,"url":f"{DOMAIN}/renting-{m['slug']}.html","name":f"{m['make']} {m['model']}"}
        for i,m in enumerate(ms)]},
      {"@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Inicio","item":f"{DOMAIN}/"},
        {"@type":"ListItem","position":2,"name":h1,"item":url}]}]}
    meta=f"{intro}"[:158]
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} desde {desde}€/mes | MyRenting</title><meta name="description" content="{e(meta)}">
<link rel="canonical" href="{url}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(meta)}">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
<style>:root{{--o:#FF5C00;--o2:#F04E00;--ink:#1c2233;--ink2:#5a6072;--line:#e9e2d6;--bg:#f6f3ee}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;line-height:1.6}}
.wrap{{max-width:1100px;margin:0 auto;padding:0 20px}}nav{{background:#fff;border-bottom:1px solid var(--line);padding:14px 0}}
.logo{{font-weight:850;font-size:20px;text-decoration:none;color:var(--ink)}}.logo span{{color:var(--o)}}
h1{{font-size:clamp(26px,5vw,38px);font-weight:850;margin:20px 0 6px}}.lede{{font-size:17px;color:var(--ink2);max-width:760px;margin:0 0 8px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:16px;margin:24px 0}}
a.c{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px;text-decoration:none;color:var(--ink);transition:.15s;display:flex;flex-direction:column}}
a.c:hover{{transform:translateY(-3px);box-shadow:0 12px 24px rgba(0,0,0,.08);border-color:#f5c6b0}}
a.c img{{width:100%;aspect-ratio:16/10;object-fit:contain;background:var(--bg);border-radius:10px}}
.cn{{font-weight:800;margin-top:10px}}.cs{{font-size:12.5px;color:var(--ink2)}}.cp{{margin-top:6px;font-size:13px;color:var(--ink2)}}.cp b{{font-size:18px;color:var(--o2)}}
footer{{border-top:1px solid var(--line);padding:20px 0;font-size:13px;color:var(--ink2);margin-top:26px}}</style></head><body>
<nav><div class="wrap"><a class="logo" href="/">My<span>Renting</span></a></div></nav>
<div class="wrap"><h1>{e(h1)}</h1><p class="lede">{e(intro)}</p>
<p class="lede"><b>{len(ms)} modelos</b> · desde <b>{desde}€/mes</b> · sin entrada · seguro y mantenimiento incluidos.</p>
<div class="grid">{grid}</div>
</div><footer><div class="wrap">MyRenting · {e(h1)} · precios reales actualizados.</div></footer></body></html>"""

def run():
    hubs=build_hubs(); slugs=[]
    for sl,title,h1,intro,ms in hubs:
        open(f"{REPO}/{sl}.html","w",encoding='utf-8').write(render(sl,title,h1,intro,ms))
        slugs.append(sl)
    # sitemap de hubs
    with open(f"{REPO}/sitemap-hubs.xml","w",encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for sl in sorted(slugs):
            f.write(f'  <url><loc>{DOMAIN}/{sl}.html</loc><changefreq>weekly</changefreq></url>\n')
        f.write('</urlset>\n')
    return slugs

if __name__=="__main__":
    slugs=run()
    print(f"✅ {len(slugs)} hubs SEO generados en la raíz + sitemap-hubs.xml")
