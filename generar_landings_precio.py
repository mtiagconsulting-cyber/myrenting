#!/usr/bin/env python3
"""Landings de renting por precio/segmento (frente 1 del plan de crecimiento).
Captan long-tail real de GSC: 'renting SUV por menos de 300', 'coches renting
por 500', 'renting hibrido barato'... Datos reales, no doorway."""
import re,json,os,sys,html as _h
from collections import defaultdict
DRY='--apply' not in sys.argv
WA='34691766768'
def slug(s):
    s=s.lower()
    for a,b in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u'),('ñ','n')]: s=s.replace(a,b)
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')
def tc(s): return ' '.join(w.capitalize() for w in s.split())
def esc(s): return _h.escape(str(s))

d=json.loads(re.search(r'const _OFERTAS = (\[.*?\]);',open('index.html').read(),re.DOTALL).group(1))
grp=defaultdict(list)
for o in d: grp[(o['make'],o['model'])].append(o)
MODELS=[]
for (mk,md),offs in grp.items():
    s=slug(mk+' '+md)
    img=f'/img/modelos/{s}.png' if os.path.exists(f'img/modelos/{s}.png') else next((o.get('image') for o in offs if o.get('image')),'')
    if not (img and img.startswith('/')):
        import glob
        g=glob.glob(f'img/modelos/ma-{s}-*.jpg')
        if g: img='/'+g[0]
    MODELS.append(dict(mk=mk,md=md,slug=s,mn=int(min(o['precio_desde'] for o in offs)),
        cat=(offs[0].get('category') or '').lower(),
        fuels=' '.join(o.get('fuel','').lower() for o in offs), img=img,
        n=len(offs)))

CSS=""":root{--accent:#F04E00;--navy:#16224e;--ink:#1c2233;--ink2:#5a6072;--line:#e9e2d6;--bg:#f6f3ee;--panel:#fff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;line-height:1.6}
.mrnav{position:sticky;top:0;z-index:100;display:flex;align-items:center;gap:20px;background:#fff;border-bottom:1px solid #ece7e2;padding:0 32px;height:64px;}
.mrnav-logo{display:flex;align-items:center;gap:10px;text-decoration:none;flex-shrink:0;}
.mrnav-ic{width:34px;height:34px;border-radius:9px;background:#F04E00;color:#fff;display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:900;}
.mrnav-tx{font-size:19px;font-weight:800;color:#17120f;letter-spacing:-.6px;}.mrnav-tx span{color:#F04E00;}
.mrnav-links{display:flex;align-items:center;gap:4px;flex:1;}
.mrnav-links a{font-size:14px;font-weight:500;color:#5c534d;padding:6px 12px;border-radius:8px;text-decoration:none;}
.mrnav-links a:hover{color:#17120f;background:#f5f2ef;}
.mrnav-cta{background:#F04E00;color:#fff;text-decoration:none;font-size:13.5px;font-weight:700;padding:9px 18px;border-radius:10px;flex-shrink:0;}
@media(max-width:760px){.mrnav{padding:0 18px;gap:12px;}.mrnav-links{display:none;}}
.wrap{max-width:1100px;margin:0 auto;padding:0 24px}
.crumb{font-size:13px;color:var(--ink2);padding:16px 0}.crumb a{color:var(--ink2)}
h1{font-size:clamp(26px,4.5vw,36px);font-weight:850;letter-spacing:-.02em;margin:6px 0 8px;line-height:1.12}
h1 em{font-style:normal;color:var(--accent)}
.lede{font-size:17px;color:var(--ink2);max-width:64ch;margin:0 0 8px}
.count{font-size:13px;color:var(--ink2);margin:0 0 18px}
h2{font-size:21px;font-weight:800;margin:30px 0 12px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
@media(max-width:900px){.grid{grid-template-columns:1fr 1fr}}
.card{background:#fff;border:1px solid #ebebeb;border-radius:14px;overflow:hidden;display:block;text-decoration:none;transition:box-shadow .15s,transform .15s}
.card:hover{box-shadow:0 10px 26px rgba(30,20,15,.10);transform:translateY(-2px)}
.card-img{background:#faf7f5;height:120px;display:flex;align-items:center;justify-content:center;border-bottom:1px solid #f0ece8}
.card-img img{width:100%;height:100%;object-fit:contain;padding:10px}
.card-b{padding:12px 14px}.card-n{font-size:13.5px;font-weight:800;color:#17120f;margin-bottom:5px}
.card-p{font-size:21px;font-weight:850;color:#F04E00;letter-spacing:-.5px;margin-bottom:9px}.card-p span{font-size:11px;color:#999;font-weight:600}
.card-cta{background:#17120f;color:#fff;text-align:center;padding:8px;border-radius:8px;font-size:11.5px;font-weight:700}
p{color:var(--ink2)}
.faq{background:#fff;border:1px solid var(--line);border-radius:12px;padding:4px 20px;margin-top:8px}
.faq details{border-bottom:1px solid var(--line);padding:14px 0}.faq details:last-child{border-bottom:none}
.faq summary{font-weight:700;cursor:pointer}
.rel{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 30px}
.rel a{font-size:13px;background:#fff;border:1px solid var(--line);border-radius:99px;padding:7px 14px;color:#17120f;text-decoration:none}
footer{border-top:1px solid var(--line);padding:22px 0;font-size:13px;color:var(--ink2);margin-top:30px}
.wafloat{position:fixed;bottom:20px;right:20px;z-index:400;width:56px;height:56px;border-radius:50%;background:#25D366;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(0,0,0,.28)}"""

NAV='''<nav class="mrnav"><a href="/" class="mrnav-logo"><span class="mrnav-ic">M</span><span class="mrnav-tx">My<span>Renting</span></span></a>
<div class="mrnav-links"><a href="/">Ofertas</a><a href="/renting-autonomos.html">Aut&oacute;nomos</a><a href="/renting-empresas.html">Empresas</a><a href="/renting-electrico.html">El&eacute;ctrico</a><a href="/blog/">Blog</a></div>
<a href="/" class="mrnav-cta">Comparar gratis</a></nav>'''

def cardhtml(m):
    name=tc(f'{m["mk"]} {m["md"]}')
    img=f'<img src="{m["img"]}" alt="Renting {esc(name)}" loading="lazy">' if m['img'] else f'<span style="color:#ccc;font-size:12px">{esc(name)}</span>'
    return f'''<a href="/renting-{m['slug']}.html" class="card"><div class="card-img">{img}</div>
      <div class="card-b"><div class="card-n">{esc(name)}</div><div class="card-p">{m['mn']}€<span>/mes</span></div>
      <div class="card-cta">Ver oferta &rarr;</div></div></a>'''

def page(fname,title,desc,h1,intro,filt,faqs,rel):
    sel=sorted([m for m in MODELS if filt(m)],key=lambda m:m['mn'])
    if len(sel)<6: return None
    minp=sel[0]['mn']; n=len(sel); sel=sel[:28]
    cards='\n    '.join(cardhtml(m) for m in sel)
    faq_html='<div class="faq">'+''.join(f'<details{" open" if i==0 else ""}><summary>{esc(q)}</summary><p>{a}</p></details>' for i,(q,a) in enumerate(faqs))+'</div>'
    ld=[{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":re.sub('<[^>]+>','',a)}} for q,a in faqs]},
        {"@context":"https://schema.org","@type":"ItemList","numberOfItems":n,"itemListElement":[{"@type":"ListItem","position":i+1,"url":f"https://myrenting.es/renting-{m['slug']}.html","name":tc(m['mk']+' '+m['md'])} for i,m in enumerate(sel)]}]
    relh=' '.join(f'<a href="{u}">{t}</a>' for t,u in rel)
    wat="Hola%2C%20busco%20un%20renting%20"+re.sub(r'[^a-z0-9]+','%20',h1.lower())
    return f'''<!DOCTYPE html><html lang="es"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/svg+xml" href="/favicon.svg"><link rel="apple-touch-icon" href="/favicon.png">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="robots" content="index, follow">
<link rel="canonical" href="https://myrenting.es/{fname}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:type" content="website">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
<style>{CSS}</style></head><body>
{NAV}
<div class="wrap">
<div class="crumb"><a href="/">Inicio</a> › {esc(re.sub("<[^>]+>","",h1))}</div>
<h1>{h1}</h1>
<p class="lede">{intro}</p>
<p class="count"><strong>{n} modelos</strong> disponibles desde <strong>{minp}€/mes</strong> · todo incluido y sin entrada · precios reales comparados</p>
<div class="grid">
    {cards}
  </div>
<div style="text-align:center;margin:22px 0"><a href="/" style="display:inline-block;background:#F04E00;color:#fff;padding:12px 26px;border-radius:99px;font-weight:700;text-decoration:none;font-size:14px">Ver todas las ofertas &rarr;</a></div>
<h2>Preguntas frecuentes</h2>
{faq_html}
<h2>También te puede interesar</h2>
<div class="rel">{relh}</div>
</div>
<footer><div class="wrap">MyRenting · Comparador de renting con precios reales. Sin registro.</div></footer>
<a class="wafloat" href="https://wa.me/{WA}?text={wat}" target="_blank" rel="noopener" aria-label="WhatsApp"><svg width="30" height="30" viewBox="0 0 24 24" fill="#fff"><path d="M12 2C6.5 2 2 6.5 2 12c0 1.8.5 3.4 1.3 4.9L2 22l5.3-1.4c1.4.8 3 1.2 4.7 1.2 5.5 0 10-4.5 10-10S17.5 2 12 2z"/></svg></a>
</body></html>'''

RELALL=[('Renting SUV','/renting-suv.html'),('Renting eléctrico','/renting-electrico.html'),
        ('Renting híbrido','/renting-hibrido.html'),('Renting hasta 300€','/renting-hasta-300.html'),
        ('Renting para autónomos','/renting-autonomos.html'),('Renting para empresas','/renting-empresas.html')]

TARGETS=[
 ('renting-suv-menos-300.html','Renting SUV por menos de 300€/mes | Ofertas reales | MyRenting',
  'Los mejores SUV en renting por menos de 300€ al mes, todo incluido y sin entrada. Precios reales comparados entre gestoras.',
  'Renting <em>SUV por menos de 300€</em> al mes',
  'Un SUV en renting por menos de 300€/mes con seguro, mantenimiento e impuestos incluidos. Estos son los modelos reales que hoy entran en ese presupuesto.',
  lambda m:'suv' in m['cat'] and m['mn']<300,
  [('¿Qué SUV puedo tener en renting por menos de 300€ al mes?','Hay varios modelos: la lista de esta página muestra los SUV reales por debajo de 300€/mes, con todo incluido y sin entrada, según los precios actuales de MyRenting.'),
   ('¿El precio incluye todo?','Sí: seguro a todo riesgo, mantenimiento, impuestos, ITV y asistencia 24h, en una cuota fija sin entrada.'),
   ('¿Puedo contratarlo como particular, autónomo o empresa?','Sí, las tres modalidades están disponibles; autónomos y empresas tienen ventajas fiscales.')]),
 ('renting-suv-menos-400.html','Renting SUV por menos de 400€/mes | Ofertas | MyRenting',
  'SUV en renting por menos de 400€ al mes, todo incluido y sin entrada. Compara precios reales de todas las gestoras.',
  'Renting <em>SUV por menos de 400€</em> al mes',
  'Amplía tus opciones: SUV en renting por debajo de 400€/mes, incluyendo híbridos y algún eléctrico, todo incluido y sin entrada.',
  lambda m:'suv' in m['cat'] and m['mn']<400,
  [('¿Qué SUV hay en renting por menos de 400€?','En esta página tienes todos los SUV reales por debajo de 400€/mes, ordenados por precio, con todo incluido.'),
   ('¿Hay SUV híbridos y eléctricos por menos de 400€?','Sí, varios híbridos y algún eléctrico entran en ese presupuesto. Fíltralos en la ficha de cada modelo.'),
   ('¿Sin entrada?','Sí, todas las cuotas son sin entrada y con seguro y mantenimiento incluidos.')]),
 ('renting-electrico-menos-400.html','Renting de coches eléctricos por menos de 400€/mes | MyRenting',
  'Coches eléctricos en renting por menos de 400€ al mes, con etiqueta CERO, todo incluido y sin entrada. Precios reales.',
  'Renting <em>eléctrico por menos de 400€</em> al mes',
  'Un coche 100% eléctrico en renting por menos de 400€/mes, con etiqueta CERO para circular por las Zonas de Bajas Emisiones y todo incluido en la cuota.',
  lambda m:('lectric' in m['fuels'] or 'eléctric' in m['fuels']) and m['mn']<400,
  [('¿Qué coche eléctrico puedo tener por menos de 400€ al mes?','Los modelos de esta página son los eléctricos reales por debajo de 400€/mes en MyRenting, con todo incluido y sin entrada.'),
   ('¿Tienen etiqueta CERO?','Sí, los eléctricos tienen etiqueta CERO de la DGT, ideal para circular y aparcar en las ZBE.'),
   ('¿Incluye punto de carga?','La cuota incluye seguro, mantenimiento e impuestos; el punto de carga depende de la oferta, consúltalo al solicitar.')]),
 ('renting-hibrido-menos-350.html','Renting de coches híbridos por menos de 350€/mes | MyRenting',
  'Coches híbridos en renting por menos de 350€ al mes, con etiqueta ECO, todo incluido y sin entrada. Compara precios reales.',
  'Renting <em>híbrido por menos de 350€</em> al mes',
  'Un híbrido en renting por menos de 350€/mes: bajo consumo, etiqueta ECO y cuota fija con todo incluido. Estos son los modelos reales que entran en presupuesto.',
  lambda m:'brido' in m['fuels'] and m['mn']<350,
  [('¿Qué híbrido puedo tener por menos de 350€ al mes?','Consulta la lista: son los híbridos reales por debajo de 350€/mes, ordenados por precio, con todo incluido.'),
   ('¿Tienen etiqueta ECO?','Sí, los híbridos tienen etiqueta ECO, que facilita circular por las Zonas de Bajas Emisiones.'),
   ('¿Sin entrada y todo incluido?','Sí: seguro, mantenimiento, impuestos, ITV y asistencia, sin entrada.')]),
 ('renting-familiar.html','Renting de coches familiares | SUV y monovolúmenes | MyRenting',
  'Renting de coches familiares: berlinas, compactos y monovolúmenes amplios, todo incluido y sin entrada. Precios reales.',
  'Renting de coches <em>familiares</em>',
  'Coches amplios y prácticos para la familia en renting: berlinas, compactos y monovolúmenes, con seguro y mantenimiento incluidos y sin entrada.',
  lambda m:any(x in m['cat'] for x in ['berlina','familiar','compacto','sedan']),
  [('¿Qué coches familiares hay en renting?','En esta página tienes berlinas, compactos y monovolúmenes familiares reales, ordenados por precio y con todo incluido.'),
   ('¿Cuánto cuesta un familiar en renting?','Depende del modelo; verás el precio real de cada uno en la lista, todos con seguro y mantenimiento incluidos.'),
   ('¿Sin entrada?','Sí, todas las cuotas son sin entrada.')]),
 ('renting-coches-menos-500.html','Renting de coches por menos de 500€/mes | Todas las ofertas | MyRenting',
  'Todos los coches en renting por menos de 500€ al mes, todo incluido y sin entrada. Compara precios reales entre gestoras.',
  'Renting de coches por <em>menos de 500€</em> al mes',
  'La mayoría de coches en renting caben por debajo de 500€/mes. Aquí tienes el catálogo real ordenado por precio, todo incluido y sin entrada.',
  lambda m:m['mn']<500,
  [('¿Qué coches hay en renting por menos de 500€ al mes?','Prácticamente todo el catálogo: urbanos, SUV, híbridos y eléctricos por debajo de 500€/mes, ordenados por precio.'),
   ('¿Qué incluye la cuota?','Seguro a todo riesgo, mantenimiento, impuestos, ITV y asistencia 24h, sin entrada.'),
   ('¿Cuál es el más barato?','El primero de la lista; se actualiza con los precios reales de cada momento.')]),
 ('renting-coches-menos-350.html','Renting de coches por menos de 350€/mes | Ofertas baratas | MyRenting',
  'Coches en renting por menos de 350€ al mes, todo incluido y sin entrada. Las mejores ofertas reales comparadas.',
  'Renting de coches por <em>menos de 350€</em> al mes',
  'Coches en renting por debajo de 350€/mes con todo incluido y sin entrada: urbanos, compactos y algún SUV e híbrido. Precios reales comparados.',
  lambda m:m['mn']<350,
  [('¿Qué coche puedo tener en renting por menos de 350€ al mes?','Muchos modelos entran en ese presupuesto; esta página los lista todos, ordenados por precio y con todo incluido.'),
   ('¿Sin entrada?','Sí, sin entrada y con seguro y mantenimiento incluidos.'),
   ('¿Puedo elegir plazo y kilómetros?','Sí, cada modelo tiene varias combinaciones de plazo y km; las ves en su ficha.')]),
 ('renting-diesel.html','Renting de coches diésel | Ofertas y precios | MyRenting',
  'Coches diésel en renting, ideales para muchos kilómetros, todo incluido y sin entrada. Compara precios reales.',
  'Renting de coches <em>diésel</em>',
  'El diésel sigue siendo la opción más eficiente para quien hace muchos kilómetros. Estos son los coches diésel en renting con todo incluido y sin entrada.',
  lambda m:'diesel' in m['fuels'] or 'diésel' in m['fuels'],
  [('¿Merece la pena el renting diésel?','Sí, si haces muchos kilómetros al año: el diésel consume menos en carretera. En renting evitas además la depreciación.'),
   ('¿Qué incluye la cuota?','Seguro a todo riesgo, mantenimiento, impuestos, ITV y asistencia, sin entrada.'),
   ('¿Tienen etiqueta para las ZBE?','Los diésel más nuevos tienen etiqueta C; revisa las restricciones de tu ciudad.')]),
]

made=[]
for fname,title,desc,h1,intro,filt,faqs in [(t[0],t[1],t[2],t[3],t[4],t[5],t[6]) for t in TARGETS]:
    if os.path.exists(fname):
        print('  (existe, salto)',fname); continue
    rel=[r for r in RELALL if r[1]!='/'+fname][:5]
    html=page(fname,title,desc,h1,intro,filt,faqs,rel)
    if not html:
        print('  (pocos modelos, salto)',fname); continue
    if not DRY: open(fname,'w').write(html)
    made.append(fname)
print(f'landings creadas: {len(made)} (DRY={DRY})')
for m in made: print('  ',m)
