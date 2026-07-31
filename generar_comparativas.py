#!/usr/bin/env python3
"""Genera comparativas/guías ancla (Pilar 5) con datos reales de index.html.
Captan búsqueda informacional, enlazan a las fichas y son citables por IA."""
import re, json, sys, html as _h
from collections import defaultdict
DRY = '--apply' not in sys.argv
WA='34691766768'; MAIL='mtiagconsulting@gmail.com'

d=json.loads(re.search(r'const _OFERTAS = (\[.*?\]);',open('index.html').read(),re.DOTALL).group(1))
grp=defaultdict(list)
for o in d: grp[(o['make'],o['model'])].append(o)
def slug(s):
    s=s.lower()
    for a,b in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u'),('ñ','n')]: s=s.replace(a,b)
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')
def esc(s): return _h.escape(str(s))
def M(make,model):
    offs=grp.get((make,model),[])
    if not offs: return None
    mn=int(min(o['precio_desde'] for o in offs))
    by={}
    for o in offs:
        t=o['tipo']
        if t not in by or o['precio_desde']<by[t]['precio_desde']: by[t]=o
    return dict(mn=mn,by=by,fuels=sorted(set(o.get('fuel','') for o in offs if o.get('fuel'))),
                cat=offs[0].get('category','') or 'SUV',n=len(offs),
                gest=sorted(set(o['fuente'] for o in offs)),
                fichaslug='renting-'+slug(make+' '+model))

CSS="""
:root{--accent:#F04E00;--navy:#16224e;--ink:#1c2233;--ink2:#5a6072;--line:#e9e2d6;--bg:#f6f3ee;--panel:#fff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;line-height:1.65}
.wrap{max-width:820px;margin:0 auto;padding:0 20px}
nav{background:var(--panel);border-bottom:1px solid var(--line);padding:14px 0}nav .wrap{display:flex;justify-content:space-between;align-items:center}
.logo{font-weight:850;font-size:20px;color:var(--ink);text-decoration:none}.logo span{color:var(--accent)}
.back{color:var(--ink2);text-decoration:none;font-size:14px}
.crumb{font-size:13px;color:var(--ink2);padding:16px 0}.crumb a{color:var(--ink2)}
h1{font-size:clamp(27px,5vw,38px);font-weight:850;letter-spacing:-.02em;line-height:1.12;margin:6px 0 10px}
h2{font-size:22px;font-weight:800;margin:34px 0 12px;letter-spacing:-.01em}
h3{font-size:17px;font-weight:750;margin:20px 0 6px}
.lede{font-size:18px;color:var(--ink2);margin:0 0 8px}
.upd{font-size:13px;color:var(--ink2);margin:0 0 22px}
p{color:var(--ink2);margin:0 0 14px}a{color:var(--accent)}
.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--panel);margin:14px 0}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{padding:11px 13px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{background:var(--bg);font-size:11.5px;text-transform:uppercase;letter-spacing:.04em;color:var(--ink2)}
tr:last-child td{border-bottom:none}td.p{font-weight:800;color:var(--accent);font-variant-numeric:tabular-nums;white-space:nowrap}
.win{background:#e3f4ec;color:#0f7a52;font-weight:700;font-size:11px;padding:2px 8px;border-radius:99px}
.rank td:first-child{font-weight:800;color:var(--navy)}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin:14px 0}
.faq details{border-bottom:1px solid var(--line);padding:14px 0}.faq details:last-child{border-bottom:none}
.faq summary{font-weight:700;cursor:pointer}.faq{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:4px 20px}
.cta{background:var(--navy);color:#fff;border-radius:16px;padding:24px;text-align:center;margin:28px 0}
.cta h2{color:#fff;margin:0 0 8px}.cta p{color:rgba(255,255,255,.8)}
.btn{display:inline-block;background:var(--accent);color:#fff;border-radius:99px;padding:12px 22px;font-weight:700;text-decoration:none;margin:4px}
.btn.wa{background:#25D366}
footer{border-top:1px solid var(--line);padding:24px 0;font-size:13px;color:var(--ink2);margin-top:30px}
.wafloat{position:fixed;bottom:20px;right:20px;z-index:400;width:56px;height:56px;border-radius:50%;background:#25D366;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(0,0,0,.28)}
"""

def page(fname,title,desc,h1,updated,body,faq_pairs):
    faq_html='<div class="faq">'+''.join(f'<details{" open" if i==0 else ""}><summary>{esc(q)}</summary><p>{a}</p></details>' for i,(q,a) in enumerate(faq_pairs))+'</div>'
    faq_ld=[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":re.sub('<[^>]+>','',a)}} for q,a in faq_pairs]
    ld=[{"@context":"https://schema.org","@type":"Article","headline":h1,"description":desc,
         "datePublished":"2026-07-21","dateModified":"2026-07-21",
         "author":{"@type":"Organization","name":"MyRenting"},"publisher":{"@type":"Organization","name":"MyRenting"}},
        {"@context":"https://schema.org","@type":"FAQPage","mainEntity":faq_ld}]
    wat="Hola,%20tengo%20una%20consulta%20sobre%20renting"
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow"><link rel="canonical" href="https://myrenting.es/blog/{fname}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="article"><link rel="icon" href="/favicon.svg">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
<style>{CSS}</style></head><body>
<nav><div class="wrap"><a class="logo" href="/">My<span>Renting</span></a><a class="back" href="/blog/">← Blog</a></div></nav>
<div class="wrap">
<div class="crumb"><a href="/">Inicio</a> › <a href="/blog/">Blog</a> › {esc(h1)}</div>
<h1>{esc(h1)}</h1>
<p class="upd">Guía de MyRenting · Actualizado julio 2026 · Precios reales comparados</p>
{body}
{'<h2>Preguntas frecuentes</h2>'+faq_html}
<div class="cta" id="cta"><h2>¿Te ayudamos a elegir?</h2><p>Te enviamos las ofertas reales sin compromiso.</p>
<a class="btn wa" href="https://wa.me/{WA}?text={wat}" target="_blank" rel="noopener">WhatsApp directo</a>
<a class="btn" href="mailto:{MAIL}">Escríbenos</a></div>
</div>
<footer><div class="wrap">MyRenting · Comparador de renting con precios reales. Sin registro.</div></footer>
<a class="wafloat" href="https://wa.me/{WA}?text={wat}" target="_blank" rel="noopener" aria-label="WhatsApp"><svg width="30" height="30" viewBox="0 0 24 24" fill="#fff"><path d="M12 2C6.5 2 2 6.5 2 12c0 1.8.5 3.4 1.3 4.9L2 22l5.3-1.4c1.4.8 3 1.2 4.7 1.2 5.5 0 10-4.5 10-10S17.5 2 12 2z"/></svg></a>
</body></html>"""

pages={}

# ---------- 1) Omoda 5 vs Jaecoo 7 ----------
o5=M('OMODA','5'); j7=M('JAECOO','7')
if o5 and j7:
    body=f"""<p class="lede">Dos de los SUV chinos más buscados en renting, comparados con cuotas reales. El Omoda 5 juega en el segmento C híbrido accesible; el Jaecoo 7 apunta más arriba, con versión híbrida enchufable (PHEV).</p>
<h2>Comparativa rápida</h2>
<div class="scroll"><table><thead><tr><th>&nbsp;</th><th>Omoda 5</th><th>Jaecoo 7</th></tr></thead><tbody>
<tr><td>Cuota desde</td><td class="p">{o5['mn']}€/mes <span class="win">más barato</span></td><td class="p">{j7['mn']}€/mes</td></tr>
<tr><td>Segmento</td><td>SUV compacto</td><td>SUV medio</td></tr>
<tr><td>Mecánica</td><td>{' / '.join(o5['fuels'])}</td><td>{' / '.join(j7['fuels'])}</td></tr>
<tr><td>Gestoras</td><td>{', '.join(o5['gest'])}</td><td>{', '.join(j7['gest'])}</td></tr>
<tr><td>Ficha</td><td><a href="/{o5['fichaslug']}.html">Ver ofertas Omoda 5</a></td><td><a href="/{j7['fichaslug']}.html">Ver ofertas Jaecoo 7</a></td></tr>
</tbody></table></div>
<h2>¿Cuál elegir?</h2>
<div class="card"><h3>Elige el Omoda 5 si…</h3><p>Buscas el SUV híbrido más económico para el día a día urbano. Desde {o5['mn']}€/mes con todo incluido, es de los SUV con etiqueta más baratos del mercado en renting.</p></div>
<div class="card"><h3>Elige el Jaecoo 7 si…</h3><p>Quieres más tamaño, equipamiento y la opción híbrida enchufable (PHEV) para hacer trayectos en eléctrico y beneficiarte de la etiqueta CERO. Parte de {j7['mn']}€/mes.</p></div>
<p>Ambos incluyen seguro a todo riesgo sin franquicia, mantenimiento, impuestos, ITV y asistencia 24h en una cuota fija, sin entrada. Consulta el precio para tu perfil (particular, autónomo o empresa) en cada ficha.</p>"""
    faq=[("¿Cuál es más barato en renting, el Omoda 5 o el Jaecoo 7?",
          f"El <strong>Omoda 5</strong> es más económico: desde <strong>{o5['mn']}€/mes</strong> frente a los {j7['mn']}€/mes del Jaecoo 7, ambos con todo incluido y sin entrada según los precios reales de MyRenting."),
         ("¿El Jaecoo 7 tiene versión híbrida enchufable?",
          "Sí, el Jaecoo 7 se ofrece en híbrido e híbrido enchufable (PHEV), lo que le da etiqueta CERO y autonomía eléctrica para el día a día."),
         ("¿Qué incluye el renting de estos SUV?",
          "Seguro a todo riesgo sin franquicia, mantenimiento en red oficial, impuestos, ITV y asistencia en carretera 24h, en una cuota mensual fija y sin entrada.")]
    pages['omoda-5-vs-jaecoo-7-renting.html']=dict(
        title="Renting Omoda 5 vs Jaecoo 7: precio real y cuál elegir (2026) | MyRenting",
        desc=f"Comparativa real en renting del Omoda 5 (desde {o5['mn']}€/mes) y el Jaecoo 7 (desde {j7['mn']}€/mes): precio, mecánica y cuál te conviene. Datos reales, sin entrada.",
        h1="Omoda 5 vs Jaecoo 7 en renting: ¿cuál elegir?",updated="2026-07-21",body=body,faq=faq)

# ---------- 2) Mejores SUV híbridos renting 2026 ----------
suvs=[('HYUNDAI','TUCSON'),('NISSAN','QASHQAI'),('OMODA','5'),('TOYOTA','YARIS CROSS'),
      ('EBRO','S400'),('TOYOTA','C-HR'),('MAZDA','CX-5'),('RENAULT','AUSTRAL')]
rows=[]
for mk,md in suvs:
    i=M(mk,md)
    if not i or not any('íb' in f or 'ib' in f.lower() for f in i['fuels']): continue
    rows.append((i['mn'],mk,md,i))
rows.sort()
tbody=''.join(f'<tr><td>{n+1}</td><td><a href="/{i["fichaslug"]}.html">{(mk+" "+md).title()}</a></td><td>{" / ".join(i["fuels"])[:22]}</td><td class="p">{mn}€/mes</td></tr>' for n,(mn,mk,md,i) in enumerate(rows))
body2=f"""<p class="lede">Los SUV híbridos son la categoría más demandada en renting: etiqueta ECO, bajo consumo y cuota con todo incluido. Este es el ranking real por precio a julio de 2026, con datos comparados entre gestoras.</p>
<div class="scroll"><table class="rank"><thead><tr><th>#</th><th>Modelo</th><th>Mecánica</th><th>Desde</th></tr></thead><tbody>{tbody}</tbody></table></div>
<p>Todos incluyen seguro a todo riesgo, mantenimiento, impuestos, ITV y asistencia 24h, sin entrada. El <strong>{(rows[0][1]+' '+rows[0][2]).title()}</strong> es el SUV híbrido más barato de la lista, desde {rows[0][0]}€/mes.</p>
<h2>Cómo elegir tu SUV híbrido en renting</h2>
<p>Fíjate en el kilometraje anual que necesitas y el plazo: a más km, algo más de cuota. Compara siempre en las mismas condiciones (mismo plazo y km) y revisa qué gestora ofrece la mejor cuota para tu perfil (particular, autónomo o empresa).</p>"""
faq2=[("¿Cuál es el SUV híbrido más barato en renting en 2026?",
       f"Según los precios reales de MyRenting, el <strong>{(rows[0][1]+' '+rows[0][2]).title()}</strong> desde <strong>{rows[0][0]}€/mes</strong>, con todo incluido y sin entrada."),
      ("¿Los SUV híbridos tienen etiqueta ECO?","Sí, los híbridos convencionales tienen etiqueta ECO y los enchufables (PHEV) pueden tener etiqueta CERO, lo que facilita circular por las Zonas de Bajas Emisiones."),
      ("¿Qué incluye la cuota?","Seguro a todo riesgo sin franquicia, mantenimiento, impuestos, ITV y asistencia 24h, en una cuota fija sin entrada.")]
pages['mejores-suv-hibridos-renting-2026.html']=dict(
    title="Mejores SUV híbridos en renting 2026: ranking por precio real | MyRenting",
    desc=f"Ranking real de los mejores SUV híbridos en renting 2026, desde {rows[0][0]}€/mes. Precios comparados entre gestoras, todo incluido y sin entrada.",
    h1="Mejores SUV híbridos en renting 2026",updated="2026-07-21",body=body2,faq=faq2)

# ---------- 3) Ebro S400 opinión y precio ----------
e=M('EBRO','S400')
if e:
    alts=[]
    for mk,md in [('OMODA','5'),('HYUNDAI','TUCSON'),('NISSAN','QASHQAI')]:
        i=M(mk,md)
        if i: alts.append(f'<li><a href="/{i["fichaslug"]}.html">{(mk+" "+md).title()}</a> — desde {i["mn"]}€/mes</li>')
    body3=f"""<p class="lede">Ebro ha vuelto con SUV fabricados en Barcelona y una propuesta agresiva en renting. Analizamos el <strong>Ebro S400</strong>: precio real, qué ofrece y con qué compite.</p>
<h2>Precio del Ebro S400 en renting</h2>
<p>El Ebro S400 (SUV híbrido) parte de <strong>{e['mn']}€/mes</strong> con todo incluido y sin entrada, a través de M Automoción. Es una de las cuotas más competitivas de su segmento: para comparar, aquí tienes su <a href="/{e['fichaslug']}.html">ficha con todas las ofertas reales</a>.</p>
<div class="scroll"><table><thead><tr><th>Tipo de cliente</th><th>Cuota/mes</th></tr></thead><tbody>
{''.join(f'<tr><td>{t.capitalize()}</td><td class="p">{int(o["precio_desde"])}€</td></tr>' for t,o in e['by'].items())}
</tbody></table></div>
<h2>Opinión: ¿merece la pena?</h2>
<p>El S400 destaca por precio, mecánica híbrida con etiqueta ECO y ser un SUV amplio a una cuota de coche más pequeño. Al ser marca fabricada en España, la disponibilidad y entrega suelen ser buenas. Como todo renting de MyRenting, incluye seguro a todo riesgo, mantenimiento, impuestos, ITV y asistencia 24h.</p>
<h2>Alternativas al Ebro S400</h2>
<ul>{''.join(alts)}</ul>"""
    faq3=[("¿Cuánto cuesta el renting del Ebro S400?",
           f"Desde <strong>{e['mn']}€/mes</strong> con todo incluido (seguro a todo riesgo, mantenimiento, impuestos, ITV y asistencia 24h), sin entrada, según los precios reales de MyRenting."),
          ("¿El Ebro S400 es híbrido?","Sí, el Ebro S400 monta mecánica híbrida con etiqueta ECO, ideal para circular por Zonas de Bajas Emisiones."),
          ("¿Dónde se fabrica el Ebro S400?","Ebro fabrica en la antigua planta de Barcelona (Zona Franca), lo que suele traducirse en buena disponibilidad y plazos de entrega.")]
    pages['renting-ebro-s400-opinion-precio.html']=dict(
        title=f"Renting Ebro S400: opinión, precio real ({e['mn']}€/mes) y alternativas | MyRenting",
        desc=f"Renting del Ebro S400 desde {e['mn']}€/mes con todo incluido y sin entrada. Opinión, precio real por tipo de cliente y alternativas comparadas.",
        h1="Ebro S400 en renting: opinión y precio real",updated="2026-07-21",body=body3,faq=faq3)

for fn,p in pages.items():
    html=page(fn,p['title'],p['desc'],p['h1'],p['updated'],p['body'],p['faq'])
    if not DRY: open('blog/'+fn,'w').write(html)
    print('  blog/'+fn)
print(f"comparativas generadas: {len(pages)} (DRY={DRY})")
