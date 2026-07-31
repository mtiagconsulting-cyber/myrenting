#!/usr/bin/env python3
"""Genera páginas ciudad x modelo para los exclusivos de M Automoción.
Contenido localizado real (no doorway): intro única por ciudad, tabla de
precios por tipo de cliente con datos reales, entrega local, FAQ + schema,
CTA formulario + WhatsApp. Enlaza con la ficha nacional y entre ciudades."""
import re, json, glob, sys
from collections import defaultdict

DRY = '--apply' not in sys.argv
WA = '34691766768'
MAIL = 'mtiagconsulting@gmail.com'

d = json.loads(re.search(r'const _OFERTAS = (\[.*?\]);', open('index.html').read(), re.DOTALL).group(1))
grp = defaultdict(list)
for o in d: grp[(o['make'], o['model'])].append(o)

def slug(s):
    s=s.lower()
    for a,b in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u'),('ñ','n')]: s=s.replace(a,b)
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')

def title_case(s): return ' '.join(w.capitalize() for w in s.split())

def find_ficha(make, model):
    for c in [f"renting-{slug(make)}-{slug(model)}.html", f"renting-{slug(model)}.html",
              f"renting-{slug(make+' '+model)}.html"]:
        if c in EXISTING: return c
    return None

EXISTING = set(glob.glob('renting-*.html'))

# ciudades con contenido localizado real
CIUDADES = {
 'madrid':{'n':'Madrid','prov':'la Comunidad de Madrid',
   'intro':"Con la Zona de Bajas Emisiones Madrid 360 y el precio del parking en el centro, el renting es la forma más cómoda de moverse por Madrid sin preocuparte de la etiqueta, el seguro ni el mantenimiento.",
   'zbe':"Madrid aplica restricciones a los vehículos sin etiqueta ambiental en toda la almendra central."},
 'barcelona':{'n':'Barcelona','prov':'el área metropolitana de Barcelona',
   'intro':"La ZBE Rondes de Barcelona es una de las más estrictas de España. Con un renting de MyRenting circulas con un coche con etiqueta y todos los servicios incluidos en una sola cuota.",
   'zbe':"La ZBE de Barcelona restringe el acceso a los vehículos más contaminantes dentro de las Rondas."},
 'valencia':{'n':'Valencia','prov':'la provincia de Valencia',
   'intro':"Valencia estrena su Zona de Bajas Emisiones y cada vez más conductores eligen el renting para tener un coche nuevo, con etiqueta y sin la inversión inicial de la compra.",
   'zbe':"Valencia ha activado su ZBE en el centro de la ciudad."},
 'sevilla':{'n':'Sevilla','prov':'la provincia de Sevilla',
   'intro':"En Sevilla el renting gana peso entre particulares y autónomos que quieren un coche nuevo con todo incluido y una cuota fija, sin sorpresas de mantenimiento ni seguro.",
   'zbe':"Sevilla trabaja en su Zona de Bajas Emisiones para el centro histórico."},
 'malaga':{'n':'Málaga','prov':'la provincia de Málaga',
   'intro':"Málaga es una de las ciudades con más crecimiento de renting de la costa. Un coche nuevo con seguro, mantenimiento e impuestos en una sola cuota, entregado donde estés.",
   'zbe':"Málaga ha puesto en marcha su Zona de Bajas Emisiones en el centro."},
 'bilbao':{'n':'Bilbao','prov':'Bizkaia',
   'intro':"Con la ZBE de Bilbao y una de las ciudades más peatonalizadas del norte, el renting te da un coche con etiqueta y todos los gastos cubiertos en una cuota mensual fija.",
   'zbe':"Bilbao aplica una Zona de Bajas Emisiones en gran parte del municipio."},
 'zaragoza':{'n':'Zaragoza','prov':'la provincia de Zaragoza',
   'intro':"En Zaragoza el renting es una opción cada vez más popular para moverse por la ciudad y hacer los trayectos a Madrid o Barcelona con un coche nuevo y todo incluido.",
   'zbe':"Zaragoza avanza en su Zona de Bajas Emisiones en el centro."},
 'marbella':{'n':'Marbella','prov':'la Costa del Sol',
   'intro':"En Marbella y la Costa del Sol el renting encaja con quien quiere un coche nuevo sin ataduras, con seguro y mantenimiento incluidos y entrega a domicilio.",
   'zbe':"Málaga y su área aplican restricciones ambientales en el centro."},
 'murcia':{'n':'Murcia','prov':'la Región de Murcia',
   'intro':"En Murcia el renting gana terreno entre particulares y autónomos que buscan un coche nuevo con cuota fija y sin la inversión inicial de la compra.",
   'zbe':"Murcia trabaja en su Zona de Bajas Emisiones."},
 'palma':{'n':'Palma de Mallorca','prov':'las Islas Baleares',
   'intro':"En Palma y Baleares el renting es ideal para tener un coche nuevo todo el año con seguro y mantenimiento incluidos, sin preocuparte de nada.",
   'zbe':"Palma estudia medidas de bajas emisiones en el centro."},
 'las-palmas':{'n':'Las Palmas de Gran Canaria','prov':'las Islas Canarias',
   'intro':"En Las Palmas el renting te permite circular con un coche nuevo y con etiqueta, con todos los gastos en una sola cuota mensual fija.",
   'zbe':"Las Palmas fomenta la movilidad de bajas emisiones."},
 'alicante':{'n':'Alicante','prov':'la provincia de Alicante',
   'intro':"En Alicante el renting es una alternativa cómoda a la compra: coche nuevo, seguro y mantenimiento incluidos y entrega donde estés.",
   'zbe':"Alicante avanza hacia su Zona de Bajas Emisiones."},
 'valladolid':{'n':'Valladolid','prov':'la provincia de Valladolid',
   'intro':"En Valladolid el renting te da un coche nuevo con todo incluido y cuota fija, perfecto para el día a día y los desplazamientos por Castilla y León.",
   'zbe':"Valladolid aplica una Zona de Bajas Emisiones en el centro."},
 'vigo':{'n':'Vigo','prov':'la provincia de Pontevedra',
   'intro':"En Vigo el renting es una opción práctica para tener un coche nuevo con seguro, mantenimiento e impuestos incluidos en una única cuota.",
   'zbe':"Vigo trabaja en su Zona de Bajas Emisiones."},
 'gijon':{'n':'Gijón','prov':'Asturias',
   'intro':"En Gijón y Asturias el renting te permite disfrutar de un coche nuevo con todo cubierto y sin entrada, con entrega a domicilio.",
   'zbe':"Gijón impulsa medidas de bajas emisiones en el centro."},
 'granada':{'n':'Granada','prov':'la provincia de Granada',
   'intro':"En Granada el renting encaja con quien quiere un coche nuevo con etiqueta para moverse por la ciudad y su entorno, con todo incluido.",
   'zbe':"Granada aplica restricciones ambientales en el centro histórico."},
}

TPL = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://myrenting.es/{fname}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://myrenting.es/{fname}">
<link rel="icon" href="/favicon.svg">
<script type="application/ld+json">{jsonld}</script>
<style>
:root{{--accent:#e8380d;--navy:#16224e;--ink:#1c2233;--ink2:#5a6072;--line:#e9e2d6;--bg:#f6f3ee;--panel:#fff}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;line-height:1.6}}
.wrap{{max-width:860px;margin:0 auto;padding:0 20px}}
nav{{background:var(--panel);border-bottom:1px solid var(--line);padding:14px 0}}
nav .wrap{{display:flex;align-items:center;justify-content:space-between}}
.logo{{font-weight:850;font-size:20px;color:var(--ink);text-decoration:none}}.logo span{{color:var(--accent)}}
.back{{color:var(--ink2);text-decoration:none;font-size:14px}}
.crumb{{font-size:13px;color:var(--ink2);padding:16px 0}}.crumb a{{color:var(--ink2)}}
h1{{font-size:clamp(26px,5vw,36px);font-weight:850;letter-spacing:-.02em;margin:6px 0 4px;line-height:1.1}}
h1 em{{color:var(--accent);font-style:normal}}
.lede{{font-size:17px;color:var(--ink2);margin:0 0 20px}}
.price-hero{{background:var(--navy);color:#fff;border-radius:16px;padding:22px 24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:14px;margin-bottom:24px}}
.price-hero .big{{font-size:34px;font-weight:850;letter-spacing:-.02em}}.price-hero .big small{{font-size:15px;font-weight:600;opacity:.8}}
.price-hero .lbl{{font-size:13px;opacity:.85}}
.btn{{background:var(--accent);color:#fff;border:none;border-radius:99px;padding:13px 22px;font-size:15px;font-weight:700;cursor:pointer;text-decoration:none;font-family:inherit;display:inline-block}}
h2{{font-size:21px;font-weight:800;letter-spacing:-.01em;margin:32px 0 12px}}
p{{color:var(--ink2);margin:0 0 14px}}
table{{width:100%;border-collapse:collapse;font-size:14px;background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden}}
th,td{{padding:11px 14px;text-align:left;border-bottom:1px solid var(--line)}}
th{{background:var(--bg);font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--ink2)}}
tr:last-child td{{border-bottom:none}}td.p{{font-weight:800;color:var(--accent);font-variant-numeric:tabular-nums}}
.inc{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin:12px 0}}
.inc div{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px;font-size:14px}}
.inc b{{color:var(--ink)}}
.faq{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:6px 20px;margin-top:8px}}
.faq details{{border-bottom:1px solid var(--line);padding:14px 0}}.faq details:last-child{{border-bottom:none}}
.faq summary{{font-weight:700;cursor:pointer;font-size:15px}}.faq p{{margin:10px 0 0;font-size:14px}}
.cta-box{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:24px;margin:28px 0;text-align:center}}
.links{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 30px}}
.links a{{font-size:13px;background:var(--panel);border:1px solid var(--line);border-radius:99px;padding:7px 14px;color:var(--ink);text-decoration:none}}
footer{{border-top:1px solid var(--line);padding:24px 0;font-size:13px;color:var(--ink2);margin-top:30px}}
.wafloat{{position:fixed;bottom:20px;right:20px;z-index:400;width:56px;height:56px;border-radius:50%;background:#25D366;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(0,0,0,.28)}}
@media(max-width:600px){{.inc{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<nav><div class="wrap"><a class="logo" href="/">My<span>Renting</span></a><a class="back" href="/{ficha}">&larr; Ver oferta nacional</a></div></nav>
<div class="wrap">
<div class="crumb"><a href="/">Inicio</a> › <a href="/{ficha}">Renting {modelo}</a> › {ciudad}</div>
<h1>Renting <em>{modelo}</em> en {ciudad}</h1>
<p class="lede">{intro}</p>
<div class="price-hero">
  <div><div class="lbl">Cuota desde, todo incluido y sin entrada</div><div class="big">{precio}€<small>/mes + IVA</small></div></div>
  <a class="btn" href="#solicitar">Solicitar oferta</a>
</div>

<h2>Precios del renting del {modelo} en {ciudad}</h2>
<p>Cuotas reales para {plazo} meses y {km} km/año, según el tipo de cliente. Precios sin IVA salvo particulares (IVA incluido).</p>
<table><thead><tr><th>Tipo de cliente</th><th>Versión</th><th>Cuota/mes</th></tr></thead><tbody>{rows}</tbody></table>

<h2>Qué incluye</h2>
<div class="inc">
<div><b>Seguro a todo riesgo</b> sin franquicia</div>
<div><b>Mantenimiento</b> en red oficial</div>
<div><b>Impuestos e ITV</b> incluidos</div>
<div><b>Asistencia 24h</b> en carretera</div>
<div><b>Neumáticos</b> y desgaste</div>
<div><b>Sin entrada</b> ni cuota final</div>
</div>

<h2>Entrega en {ciudad}</h2>
<p>Entregamos el {modelo} en {prov} y en toda España. {zbe} Un renting con {modelo} te permite circular con un vehículo con la etiqueta ambiental correspondiente y todos los gastos cubiertos en una única cuota mensual fija.</p>

<h2>Preguntas frecuentes</h2>
<div class="faq">
<details open><summary>¿Cuánto cuesta el renting del {modelo} en {ciudad}?</summary><p>El renting del {modelo} en {ciudad} parte de <strong>{precio}€/mes</strong> con todo incluido: seguro a todo riesgo sin franquicia, mantenimiento, impuestos, ITV y asistencia 24h. Es la cuota más baja disponible en MyRenting, sin entrada ni permanencia oculta.</p></details>
<details><summary>¿Entregáis el {modelo} en {ciudad}?</summary><p>Sí. Entregamos el {modelo} en {prov} y en el resto de España, coordinando la entrega contigo tras formalizar el contrato.</p></details>
<details><summary>¿Puedo contratarlo como particular, autónomo o empresa?</summary><p>Sí, las tres modalidades están disponibles. Autónomos y empresas se benefician de ventajas fiscales adicionales; los particulares ven el precio con IVA incluido.</p></details>
</div>

<div class="cta-box" id="solicitar">
<h2 style="margin-top:0">¿Te interesa el {modelo} en {ciudad}?</h2>
<p>Te enviamos la oferta personalizada sin compromiso.</p>
<a class="btn" href="https://wa.me/{wa}?text={watext}" target="_blank" rel="noopener" style="background:#25D366;margin:4px">WhatsApp directo</a>
<a class="btn" href="mailto:{mail}?subject=Renting%20{modelo}%20en%20{ciudad}" style="margin:4px">Escríbenos</a>
</div>

<h2>Renting {modelo} en otras ciudades</h2>
<div class="links">{otras}</div>

</div>
<footer><div class="wrap">MyRenting · Comparador de renting con precios reales. Sin registro. Renting {modelo} en {ciudad}.</div></footer>
<a class="wafloat" href="https://wa.me/{wa}?text={watext}" target="_blank" rel="noopener" aria-label="WhatsApp"><svg width="30" height="30" viewBox="0 0 24 24" fill="#fff"><path d="M12 2C6.5 2 2 6.5 2 12c0 1.8.5 3.4 1.3 4.9L2 22l5.3-1.4c1.4.8 3 1.2 4.7 1.2 5.5 0 10-4.5 10-10S17.5 2 12 2z"/></svg></a>
</body>
</html>"""

import urllib.parse
def esc(s): return s.replace('&','&amp;').replace('"','&quot;')

EXCL=[]
for k,offs in grp.items():
    if any(o['fuente']=='M Automoción' for o in offs):
        EXCL.append(k)

FUEL_TXT={'Híbrido':'híbrido','Híbrido enchufable':'híbrido enchufable','Eléctrico':'eléctrico',
          'Diésel':'diésel','Gasolina':'de gasolina'}
CAT_TXT={'SUV':'SUV','Urbano':'urbano','Berlina':'berlina','Compacto':'compacto',
         'Furgoneta':'furgoneta','Todoterreno':'todoterreno','Familiar':'familiar'}

TIPO={'particular':'Particular','autonomo':'Autónomo','empresa':'Empresa'}
generated=[]
for make,model in sorted(EXCL):
    offs=grp[(make,model)]
    ficha=find_ficha(make,model)
    if not ficha: continue
    modelo=title_case(f"{make} {model}")
    mn=int(min(o['precio_desde'] for o in offs))
    cheap=min(offs,key=lambda o:o['precio_desde'])
    DISP={'m automoción':'M Automoción','m automocion':'M Automoción'}
    cheap_g=DISP.get(cheap['fuente'].lower(),cheap['fuente'])
    cat=offs[0].get('category',''); fu=offs[0].get('fuel','')
    ct=CAT_TXT.get(cat,cat.lower() if cat else 'coche'); ft=FUEL_TXT.get(fu,'')
    model_line=(f"El {modelo} es un {ct}{(' '+ft) if ft else ''} que en MyRenting puedes tener en renting "
                f"desde {mn}€/mes con todo incluido y sin entrada.")
    plazo=offs[0]['duracion']; km=f"{offs[0]['km']:,}".replace(',','.')
    # una fila por tipo (cuota más barata de cada tipo)
    by_t={}
    for o in offs:
        t=o['tipo']
        if t not in by_t or o['precio_desde']<by_t[t]['precio_desde']: by_t[t]=o
    rows=''
    for t in ['particular','autonomo','empresa']:
        if t in by_t:
            o=by_t[t]
            rows+=f'<tr><td>{TIPO[t]}</td><td>{esc(o.get("version",modelo))}</td><td class="p">{int(o["precio_desde"])}€</td></tr>'
    for cslug,c in CIUDADES.items():
        fname=f"renting-{slug(model if make in ('OMODA','JAECOO','EBRO','BYD') else make+' '+model)}-{cslug}.html"
        # asegurar unicidad de slug usando make+model
        fname=f"renting-{slug(make+' '+model)}-{cslug}.html"
        ciudad=c['n']
        title=f"Renting {modelo} en {ciudad} Sin Entrada — desde {mn}€/mes | MyRenting"
        desc=f"Renting del {modelo} en {ciudad} desde {mn}€/mes, todo incluido y sin entrada. Precios reales para particulares, autónomos y empresas. Entrega en {c['prov']}."
        import os
        if os.path.exists(fname):   # no sobrescribir páginas existentes (ricas o ya creadas)
            continue
        watext=urllib.parse.quote(f"Hola, me interesa el renting del {modelo} en {ciudad}")
        otras=' '.join(f'<a href="/renting-{slug(make+" "+model)}-{o}.html">{CIUDADES[o]["n"]}</a>' for o in CIUDADES if o!=cslug)
        otras+=f' <a href="/{ficha}">Ver todas las ofertas →</a>'
        jsonld=json.dumps({"@context":"https://schema.org","@type":"Product","name":f"Renting {modelo} en {ciudad}",
            "description":desc,"brand":{"@type":"Brand","name":title_case(make)},"category":offs[0].get('category','').lower(),
            "offers":{"@type":"AggregateOffer","lowPrice":str(mn),"priceCurrency":"EUR","offerCount":str(len(offs)),
                "availability":"https://schema.org/InStock","areaServed":ciudad,
                "seller":{"@type":"Organization","name":cheap_g}}}, ensure_ascii=False)
        html=TPL.format(title=esc(title),desc=esc(desc),fname=fname,jsonld=jsonld,ficha=ficha,
            modelo=modelo,ciudad=ciudad,intro=esc(model_line+' '+c['intro']),precio=mn,plazo=plazo,km=km,rows=rows,
            prov=c['prov'],zbe=c['zbe'],wa=WA,watext=watext,mail=MAIL,otras=otras)
        if not DRY: open(fname,'w').write(html)
        generated.append(fname)

print(f"páginas generadas: {len(generated)} (DRY={DRY})")
for g in generated[:6]: print('  ',g)
if generated: print('  ...')
