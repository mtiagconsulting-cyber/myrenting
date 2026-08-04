# -*- coding: utf-8 -*-
"""
CAPA 3 · GENERAR
Lee:   data/build/catalogo.json + data/master/ciudades-zbe.json
Escribe:
   renting-<modelo>.html            · fichas de modelo en la raíz (se publican en Pages)
   llms.txt                          · índice para IAs (GEO)
   robots.txt                        · permite bots de IA + sitemap
   sitemap-modelos.xml               · sitemap de las landings nuevas
NOTA: la home (index.html) y las landings de ciudad se enganchan aquí como módulos
      adicionales una vez validado el modelo base.
"""
import json, os, re, html as H
import pathlib as _pl; REPO=str(_pl.Path(__file__).resolve().parents[2]); DOMAIN="https://myrenting.es"
cat=json.load(open(f"{REPO}/data/build/catalogo.json",encoding='utf-8'))
ZBE=json.load(open(f"{REPO}/data/master/ciudades-zbe.json",encoding='utf-8'))
MODS=cat["modelos"]
OUT=REPO   # publicar las fichas en la raíz (GitHub Pages las sirve). Se regeneran cada semana.
e=H.escape

def geo_line(m):
    s=m.get("specs") or {}; name=f"{m['make']} {m['model']}"
    bits=[s.get("combustible") or "", s.get("potencia") or "", f"{s.get('plazas')} plazas" if s.get('plazas') else "",
          f"etiqueta {s['etiqueta_dgt']}" if s.get("etiqueta_dgt") else ""]
    bits=[b for b in bits if b]
    return f"El renting del {name} cuesta desde {int(m['precio_desde'])} €/mes ({', '.join(bits)}), sin entrada y con seguro y mantenimiento incluidos."

# ---------- llms.txt (GEO) ----------
def build_llms():
    L=["# MyRenting — myrenting.es",
       "> Comparador de renting de coches en España con precios reales de varias fuentes (M Automoción, Quadis, Kia Renting). Sin entrada, cuota todo incluido.",
       "","## Qué ofrecemos","- Renting para particulares, autónomos y empresas.","- Precios reales actualizados semanalmente.","",
       "## Modelos y precios (dato directo)"]
    for k,m in sorted(MODS.items(), key=lambda kv:kv[1]['precio_desde']):
        if not os.path.exists(f"{REPO}/renting-{m['slug']}.html"): continue  # no enlazar páginas inexistentes
        L.append(f"- [{m['make']} {m['model']}]({DOMAIN}/renting-{m['slug']}.html): {geo_line(m)}")
    L+=["","## ZBE (Zonas de Bajas Emisiones)","Cubrimos la compatibilidad de cada coche con la ZBE de: "+
        ", ".join(sorted(c['n'] for c in ZBE.values()))+"."]
    open(f"{REPO}/llms.txt","w",encoding='utf-8').write("\n".join(L)+"\n")
    return len(MODS)

# ---------- robots.txt (permitir IAs) ----------
def build_robots():
    bots=["GPTBot","OAI-SearchBot","ChatGPT-User","ClaudeBot","anthropic-ai","Claude-Web",
          "PerplexityBot","Perplexity-User","Google-Extended","Applebot-Extended","CCBot","Bytespider"]
    lines=["# robots.txt — myrenting.es","User-agent: *","Allow: /",""]
    for b in bots: lines+=[f"User-agent: {b}","Allow: /",""]
    lines+=[f"Sitemap: {DOMAIN}/sitemap.xml",f"Sitemap: {DOMAIN}/sitemap-modelos.xml"]
    open(f"{REPO}/robots.txt","w",encoding='utf-8').write("\n".join(lines)+"\n")
    return len(bots)

# ---------- landing de modelo ----------
def landing(m):
    s=m.get("specs") or {}; name=f"{m['make']} {m['model']}"; sl=m['slug']
    q=int(m['precio_desde']); url=f"{DOMAIN}/renting-{sl}.html"; img=s.get("imagen") or f"/img/modelos/{sl}.webp"
    geo=geo_line(m); dgt=s.get("etiqueta_dgt")
    ld={"@context":"https://schema.org","@graph":[
      {"@type":"Product","name":f"Renting {name}","description":geo,"brand":{"@type":"Brand","name":m['make']},
       "image":DOMAIN+img if img.startswith('/') else img,
       "offers":{"@type":"AggregateOffer","lowPrice":str(q),"priceCurrency":"EUR","offerCount":str(len(m['ofertas'])),
        "availability":"https://schema.org/InStock","url":url}},
      {"@type":"Car","name":name,"fuelType":s.get("combustible") or "","seatingCapacity":str(s.get("plazas") or 5),
       **({"vehicleEngine":{"@type":"EngineSpecification","enginePower":{"@type":"QuantitativeValue","value":re.sub(r'\\D','',s['potencia']),"unitText":"CV"}}} if s.get("potencia") else {})}]}
    ficha="".join(f"<tr><th>{a}</th><td>{b}</td></tr>" for a,b in [
      ("Potencia",s.get("potencia") or "—"),("Combustible",s.get("combustible") or "—"),
      ("Consumo",(f"{s['consumo_l100']} L/100" if s.get('consumo_l100') else (f"{s['consumo_kwh100']} kWh/100" if s.get('consumo_kwh100') else "—"))),
      ("Plazas",s.get("plazas") or "—"),("Etiqueta DGT",dgt or "—"),("Categoría",s.get("category") or "—")] )
    precios="".join(f"<tr><td>{t.title()}</td><td class='p'>{int(min(o['precio_desde'] for o in m['ofertas'] if o.get('tipo')==t))}€</td></tr>"
        for t in m['tipos'] if any(o.get('tipo')==t for o in m['ofertas']))

    # --- bloques de detalle scrapeado (equipamiento, coberturas, notas, FAQ) ---
    det=m.get("detalle") or {}
    def _lista(items,titulo):
        items=[x for x in (items or []) if x]
        if not items: return ""
        lis="".join(f"<li>{e(x)}</li>" for x in items)
        return f"<h3>{titulo}</h3><ul class='eq'>{lis}</ul>"
    equip=_lista(det.get("equip_exterior"),"Equipamiento exterior")+_lista(det.get("equip_interior"),"Equipamiento interior")
    equip=f"<h2>Equipamiento</h2>{equip}" if equip else ""
    cob=f"<h2>Coberturas</h2><p>{e(det['coberturas'])}</p>" if det.get("coberturas") else ""
    notas=f"<p class='notas'><small>{e(det['notas'])}</small></p>" if det.get("notas") else ""
    faqs=[x for x in (det.get("faq") or []) if x.get("q") and x.get("a")]
    faq_html=""
    if faqs:
        faq_html="<h2>Preguntas frecuentes</h2>"+"".join(
            f"<details class='faq'><summary>{e(x['q'])}</summary><p>{e(x['a'])}</p></details>" for x in faqs)
        ld["@graph"].append({"@type":"FAQPage","mainEntity":[
            {"@type":"Question","name":x["q"],"acceptedAnswer":{"@type":"Answer","text":x["a"]}} for x in faqs]})
    detalle_html=equip+cob+faq_html+notas

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Renting {e(name)} desde {q}€/mes | MyRenting</title>
<meta name="description" content="{e(geo)[:158]}">
<link rel="canonical" href="{url}">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
<style>body{{font-family:Inter,system-ui,sans-serif;max-width:860px;margin:0 auto;padding:20px;color:#1c2233;line-height:1.6}}
h1{{font-size:2rem}}.k{{background:#fff4ee;border:1px solid #f5c6b0;border-radius:12px;padding:12px 16px;margin:14px 0}}
table{{width:100%;border-collapse:collapse;border:1px solid #eee;border-radius:12px;overflow:hidden}}
th,td{{padding:10px 14px;text-align:left;border-bottom:1px solid #eee}}th{{background:#faf7f5;width:45%}}td.p{{font-weight:800;color:#F04E00}}
img{{max-width:100%;border-radius:14px;background:#fff;border:1px solid #eee}}
ul.eq{{columns:2;gap:24px;padding-left:18px}}ul.eq li{{margin:4px 0;break-inside:avoid}}
h3{{font-size:1.05rem;margin:18px 0 6px}}
details.faq{{border:1px solid #eee;border-radius:10px;padding:10px 14px;margin:8px 0}}
details.faq summary{{font-weight:700;cursor:pointer}}details.faq p{{margin:8px 0 0;color:#4a5163}}
.notas{{color:#8a90a0}}@media(max-width:640px){{ul.eq{{columns:1}}}}</style></head><body>
<h1>Renting {e(name)}</h1>
<p class="k"><b>{e(geo)}</b></p>
<img src="{img}" alt="Renting {e(name)}" loading="lazy">
<h2>Ficha técnica</h2><table>{ficha}</table>
<h2>Precio por tipo de cliente</h2><table><tr><th>Cliente</th><th>Cuota/mes</th></tr>{precios}</table>
{detalle_html}
<p><small>Fuentes: {e(', '.join(m['fuentes']))}.</small></p>
</body></html>"""

def build_landings():
    for k,m in MODS.items():
        open(f"{OUT}/renting-{m['slug']}.html","w",encoding='utf-8').write(landing(m))
    # sitemap de modelos
    with open(f"{REPO}/sitemap-modelos.xml","w",encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for m in sorted(MODS.values(),key=lambda x:x['slug']):
            if not os.path.exists(f"{REPO}/renting-{m['slug']}.html"): continue
            f.write(f'  <url><loc>{DOMAIN}/renting-{m["slug"]}.html</loc><changefreq>weekly</changefreq></url>\n')
        f.write('</urlset>\n')
    return len(MODS)

if __name__=="__main__":
    n1=build_llms(); n2=build_robots(); n3=build_landings()
    print(f"✅ generado: llms.txt ({n1} modelos), robots.txt ({n2} bots IA permitidos), {n3} landings de modelo en _site/, sitemap-modelos.xml")
