# -*- coding: utf-8 -*-
"""
CAPA 3 · LANDINGS DE CIUDAD (SEO + GEO con valor real)
Lee:  data/build/catalogo.json + data/master/ciudades-zbe.json
Cada página cruza la ETIQUETA del coche con la NORMA ZBE de la ciudad -> contenido único.
Salida: _site/renting-<modelo>-<ciudad>.html  (preview; no pisa producción)
Uso:   python3 scripts/3_generate/generar_ciudades.py [--solo modelo1,modelo2] [--ciudades madrid,barcelona]
"""
import json, os, re, html as H, sys
REPO="/workspace/myrenting"; DOMAIN="https://myrenting.es"
cat=json.load(open(f"{REPO}/data/build/catalogo.json",encoding='utf-8'))["modelos"]
ZBE=json.load(open(f"{REPO}/data/master/ciudades-zbe.json",encoding='utf-8'))
OUT=f"{REPO}/_site"; os.makedirs(OUT,exist_ok=True)
e=H.escape

def verdict(dgt, ci):
    d=(dgt or "").upper()
    if d in ("CERO","0"): return True, f"Con la etiqueta CERO circula y aparca sin ninguna restricción en la {ci['zbe']}, incluso en episodios de alta contaminación, con ventajas de aparcamiento."
    if d=="ECO": return True, f"Con la etiqueta ECO circula sin limitaciones por la {ci['zbe']} y mantiene el acceso incluso en episodios en los que se restringe a otras etiquetas."
    if d=="C":
        extra=" en circulación normal" if ci.get("multa") else " salvo puntualmente en episodios de alta contaminación"
        return True, f"Con la etiqueta C accede a la {ci['zbe']}{extra}. Al ser un coche nuevo no le afectan las prohibiciones que sí alcanzan a los diésel y gasolina antiguos."
    if d=="B":
        if ci.get("b_centro"): return True, f"Con la etiqueta B circula por la {ci['zbe']}, aunque es la etiqueta con más limitaciones a futuro."
        return False, f"La etiqueta B tiene el acceso restringido a la zona central de la {ci['zbe']}. Un coche nuevo con C, ECO o 0 evita el problema."
    return True, f"Este vehículo puede circular por la {ci['zbe']}."

def audience(s):
    f=(s.get('combustible') or '').lower(); n=s.get('plazas') or 5; out=[]
    if 'eléctr' in f: out.append("uso urbano y trayectos diarios con coste por km muy bajo")
    elif 'enchuf' in f: out.append("quien combina ciudad en modo eléctrico y viajes largos")
    elif 'híbr' in f: out.append("ciudad y carretera con consumos contenidos y etiqueta favorable")
    elif 'diésel' in f: out.append("quien hace muchos kilómetros por autopista")
    elif 'glp' in f: out.append("quien busca el menor coste de combustible con gran autonomía")
    else: out.append("uso mixto con mecánica sencilla")
    if n and int(n)>=7: out.append("familias grandes o traslados de varios pasajeros")
    if n and int(n)<=3: out.append("autónomos y empresas por su uso profesional y ventajas fiscales")
    return out

def consumo(s):
    if s.get('consumo_l100'): return f"{str(s['consumo_l100']).replace('.',',')} L/100"
    if s.get('consumo_kwh100'): return f"{str(s['consumo_kwh100']).replace('.',',')} kWh/100"
    return None

def render(m, city, ci):
    s=m.get("specs") or {}; name=f"{m['make']} {m['model']}"; sl=m['slug']
    q=round(m['precio_desde']); cityn=ci['n']; url=f"{DOMAIN}/renting-{sl}-{city}.html"
    dgt=s.get('etiqueta_dgt'); cons=consumo(s); pot=s.get('potencia'); fuel=s.get('combustible') or ''
    plazas=s.get('plazas') or 5; puede,zbe_txt=verdict(dgt,ci)
    especs=[x for x in [fuel,pot,(f"consumo {cons}" if cons else ""),f"{plazas} plazas",(f"etiqueta {dgt}" if dgt else "")] if x]
    geo=(f"El renting del {name} en {cityn} cuesta desde {q} €/mes ({', '.join(especs)}), sin entrada y con seguro, "
         f"mantenimiento e impuestos incluidos."+(f" Con su etiqueta {dgt}, {'entra en' if puede else 'atención con'} la {ci['zbe']}." if dgt else ""))
    title=(f"Renting {name} en {cityn} desde {q}€/mes | MyRenting")[:62]
    meta=(f"Renting del {name} en {cityn} por {q}€/mes, sin entrada, todo incluido."+(f" Etiqueta {dgt}, entra en la {ci['zbe']}." if dgt else ""))[:158]
    ld={"@context":"https://schema.org","@graph":[
      {"@type":"Product","name":f"Renting {name} en {cityn}","description":geo,"brand":{"@type":"Brand","name":m['make']},
       "image":f"{DOMAIN}{s.get('imagen','')}","offers":{"@type":"AggregateOffer","lowPrice":str(q),"priceCurrency":"EUR",
        "offerCount":str(len(m['ofertas'])),"availability":"https://schema.org/InStock","areaServed":cityn,"url":url}},
      {"@type":"Car","name":name,"fuelType":fuel,"seatingCapacity":str(plazas),
       **({"vehicleEngine":{"@type":"EngineSpecification","enginePower":{"@type":"QuantitativeValue","value":re.sub(r'\D','',pot),"unitText":"CV"}}} if pot else {})},
      {"@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":f"¿Cuánto cuesta el renting del {name} en {cityn}?","acceptedAnswer":{"@type":"Answer","text":f"Desde {q} €/mes, sin entrada y con seguro, mantenimiento e impuestos incluidos."}},
        {"@type":"Question","name":f"¿Puede el {name} circular por la {ci['zbe']}?","acceptedAnswer":{"@type":"Answer","text":zbe_txt}},
        {"@type":"Question","name":f"¿Entregáis el {name} en {cityn}?","acceptedAnswer":{"@type":"Answer","text":f"Sí, en {cityn} ({ci['prov']}) y en toda España."}}]},
      {"@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Inicio","item":f"{DOMAIN}/"},
        {"@type":"ListItem","position":2,"name":f"Renting {name}","item":f"{DOMAIN}/renting-{sl}.html"},
        {"@type":"ListItem","position":3,"name":cityn,"item":url}]}]}
    ficha="".join(f"<tr><th>{a}</th><td>{b}</td></tr>" for a,b in
        [("Potencia",pot or "—"),("Combustible",fuel or "—"),("Consumo",cons or "—"),("Plazas",plazas),("Etiqueta DGT",dgt or "—"),("Categoría",s.get('category') or "—")])
    precios="".join(f"<tr><td>{t.title()}</td><td class='p'>{round(min(o['precio_desde'] for o in m['ofertas'] if o.get('tipo')==t))}€</td></tr>"
        for t in m['tipos'] if any(o.get('tipo')==t for o in m['ofertas']))
    aud="".join(f"<li>{x}</li>" for x in audience(s))
    alts=[x for x in sorted(cat.values(),key=lambda z:abs(z['precio_desde']-m['precio_desde'])) if x['slug']!=sl][:3]
    altlinks="".join(f'<a href="/renting-{a["slug"]}-{city}.html">{a["make"]} {a["model"]} · {round(a["precio_desde"])}€</a>' for a in alts)
    vcls="ok" if puede else "no"; vic="✓" if puede else "✕"
    faq="".join(f"<details{' open' if i==0 else ''}><summary>{qq}</summary><p>{aa}</p></details>" for i,(qq,aa) in enumerate([
        (f"¿Cuánto cuesta el renting del {name} en {cityn}?", f"Desde <strong>{q} €/mes</strong>, sin entrada y con seguro a todo riesgo, mantenimiento, impuestos y asistencia."),
        (f"¿Puede el {name} circular por la {ci['zbe']}?", zbe_txt),
        (f"¿Entregáis el {name} en {cityn}?", f"Sí. Entregamos en {cityn} y su área ({ci['prov']}) y en el resto de España."),
        ("¿Particular, autónomo o empresa?", "Las tres. Autónomos y empresas con ventajas fiscales; particulares con IVA incluido.")]))
    wa=f"https://wa.me/34691766768?text=Hola%2C%20me%20interesa%20el%20renting%20del%20{name.replace(' ','%20')}%20en%20{cityn.replace(' ','%20')}"
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(meta)}"><meta name="robots" content="index, follow">
<link rel="canonical" href="{url}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(meta)}">
<meta property="og:image" content="{DOMAIN}{s.get('imagen','')}"><meta property="og:type" content="product">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
<style>:root{{--o:#FF5C00;--o2:#F04E00;--navy:#16224e;--ink:#1c2233;--ink2:#5a6072;--line:#e9e2d6;--bg:#f6f3ee;--ok:#0a7d43;--no:#c0392b}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;line-height:1.6}}
.wrap{{max-width:860px;margin:0 auto;padding:0 20px}}nav{{background:#fff;border-bottom:1px solid var(--line);padding:14px 0}}nav .wrap{{display:flex;justify-content:space-between}}
.logo{{font-weight:850;font-size:20px;text-decoration:none;color:var(--ink)}}.logo span{{color:var(--o)}}.back{{color:var(--ink2);text-decoration:none;font-size:14px}}
.crumb{{font-size:13px;color:var(--ink2);padding:16px 0}}.crumb a{{color:var(--ink2)}}h1{{font-size:clamp(26px,5vw,36px);font-weight:850;margin:6px 0 4px}}h1 em{{color:var(--o);font-style:normal}}
.lede{{font-size:17px;color:var(--ink2);margin:0 0 16px}}.hero{{display:grid;grid-template-columns:1.1fr .9fr;gap:16px;align-items:center}}
.hero img{{width:100%;border-radius:14px;background:#fff;border:1px solid var(--line)}}
.ph{{background:var(--navy);color:#fff;border-radius:16px;padding:18px 20px;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}}
.ph .big{{font-size:30px;font-weight:850}}.ph .big small{{font-size:14px;opacity:.8}}.ph .lbl{{font-size:12px;opacity:.85}}
.btn{{background:var(--o);color:#fff;border-radius:99px;padding:11px 18px;font-weight:700;text-decoration:none;display:inline-block}}
.key{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:12px 16px;margin:14px 0;font-size:14.5px}}
h2{{font-size:21px;font-weight:800;margin:28px 0 12px}}p{{color:var(--ink2)}}
table{{width:100%;border-collapse:collapse;font-size:14px;background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden}}
th,td{{padding:10px 14px;text-align:left;border-bottom:1px solid var(--line)}}th{{background:var(--bg);width:42%;font-size:12px;text-transform:uppercase;color:var(--ink2)}}td.p{{font-weight:800;color:var(--o2)}}
.zbe{{border-radius:14px;padding:16px 18px;margin:16px 0;border:1.5px solid}}.zbe.ok{{background:#eaf7ef;border-color:#bfe6cd}}.zbe.no{{background:#fdecea;border-color:#f5c6c0}}
.zbe .tag{{display:inline-flex;align-items:center;gap:8px;font-weight:800;margin-bottom:4px}}.zbe.ok .tag{{color:var(--ok)}}.zbe.no .tag{{color:var(--no)}}
.zbe .ic{{width:22px;height:22px;border-radius:50%;color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px}}.zbe.ok .ic{{background:var(--ok)}}.zbe.no .ic{{background:var(--no)}}
.zbe p{{margin:4px 0 0;color:var(--ink)}}ul.aud{{padding-left:18px}}ul.aud li{{color:var(--ink2)}}
.faq{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:6px 20px}}.faq details{{border-bottom:1px solid var(--line);padding:13px 0}}.faq details:last-child{{border:none}}.faq summary{{font-weight:700;cursor:pointer}}.faq p{{margin:10px 0 0;font-size:14px}}
.alts{{display:flex;flex-wrap:wrap;gap:8px}}.alts a{{font-size:13px;background:#fff;border:1px solid var(--line);border-radius:99px;padding:7px 13px;color:var(--ink);text-decoration:none}}
.cta{{background:#fff;border:1px solid var(--line);border-radius:16px;padding:22px;margin:24px 0;text-align:center}}.src{{font-size:12px;color:var(--ink2)}}
footer{{border-top:1px solid var(--line);padding:20px 0;font-size:13px;color:var(--ink2);margin-top:26px}}@media(max-width:600px){{.hero{{grid-template-columns:1fr}}}}</style></head><body>
<nav><div class="wrap"><a class="logo" href="/">My<span>Renting</span></a><a class="back" href="/renting-{sl}.html">&larr; Oferta nacional</a></div></nav>
<div class="wrap"><div class="crumb"><a href="/">Inicio</a> › <a href="/renting-{sl}.html">Renting {e(name)}</a> › {e(cityn)}</div>
<h1>Renting <em>{e(name)}</em> en {e(cityn)}</h1><p class="lede">{e(geo)}</p>
<div class="hero"><div class="ph"><div><div class="lbl">Cuota desde · sin entrada · todo incluido</div><div class="big">{q}€<small>/mes</small></div></div><a class="btn" href="#s">Solicitar</a></div>
<img src="{s.get('imagen','')}" alt="Renting {e(name)} en {e(cityn)}" loading="lazy"></div>
<div class="key"><b>Datos clave:</b> {e(', '.join(especs))} · desde {q}€/mes en {e(cityn)}.</div>
<div class="zbe {vcls}"><span class="tag"><span class="ic">{vic}</span>{('Circula por la '+ci['zbe']) if puede else ('Atención con la '+ci['zbe'])}</span><p>{e(zbe_txt)} {e(ci['nota'])}</p></div>
<h2>Ficha técnica</h2><table>{ficha}</table>
<h2>Precio en {e(cityn)} por tipo de cliente</h2><table><tr><th>Cliente</th><th>Cuota/mes</th></tr>{precios}</table>
<p class="src">Precios: {e(', '.join(m['fuentes']))}. Normativa ZBE: Ayuntamiento de {e(cityn)} y DGT.</p>
<h2>¿Para quién encaja en {e(cityn)}?</h2><ul class="aud">{aud}</ul>
<h2>Qué incluye</h2><p>Seguro a todo riesgo sin franquicia, mantenimiento, impuestos e ITV, asistencia 24 h y neumáticos. Sin entrada ni cuota final.</p>
<h2>Alternativas por precio</h2><div class="alts">{altlinks}<a href="/renting-{sl}.html">Oferta nacional →</a></div>
<h2>Preguntas frecuentes</h2><div class="faq">{faq}</div>
<div class="cta" id="s"><h2 style="margin-top:0">¿Te interesa el {e(name)} en {e(cityn)}?</h2><p>Te enviamos la oferta sin compromiso.</p>
<a class="btn" href="{wa}" style="background:#25D366;margin:4px" target="_blank" rel="noopener">WhatsApp</a>
<a class="btn" href="mailto:mtiagconsulting@gmail.com?subject=Renting%20{name.replace(' ','%20')}%20{cityn.replace(' ','%20')}" style="margin:4px">Email</a></div>
</div><footer><div class="wrap">MyRenting · Renting {e(name)} en {e(cityn)} · ZBE {e(ci['zbe'])}.</div></footer></body></html>"""

if __name__=="__main__":
    args=sys.argv[1:]
    solo=None; ciudades=list(ZBE.keys())
    if "--solo" in args: solo=set(args[args.index("--solo")+1].split(","))
    if "--ciudades" in args: ciudades=args[args.index("--ciudades")+1].split(",")
    n=0
    for k,m in cat.items():
        if solo and m['slug'] not in solo: continue
        for city in ciudades:
            ci=ZBE.get(city)
            if not ci: continue
            open(f"{OUT}/renting-{m['slug']}-{city}.html","w",encoding='utf-8').write(render(m,city,ci))
            n+=1
    print(f"✅ {n} landings de ciudad generadas en _site/ ({len(ciudades)} ciudades)")
