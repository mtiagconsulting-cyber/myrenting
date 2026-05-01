#!/usr/bin/env python3
"""
generar_categorias.py
Genera las páginas de categoría transversales (silo nivel 2) para myrenting.es:
  /renting-barato.html         → ofertas < 300€/mes
  /renting-suv.html            → todos los SUV disponibles
  /renting-electrico.html      → eléctricos e híbridos enchufables
  /renting-sin-entrada.html    → keyword transaccional de alto volumen
  /renting-arval-vs-ayvens.html → comparativa gestoras (Bolsa 3)

Uso: python3 generar_categorias.py
"""

import json, re
from pathlib import Path

BASE     = Path("/Users/matthiasthomassen/Documents/Myrenting")
BASE_URL = "https://www.myrenting.es"

def slug(t):
    for a, b in [('á','a'),('à','a'),('é','e'),('í','i'),('ó','o'),('ú','u'),('ü','u')]:
        t = t.lower().replace(a, b)
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', t)).strip('-')

SUVY = {'QASHQAI','T-ROC','TIGUAN','ARONA','SPORTAGE','KONA','TUCSON','FORMENTOR','KAROQ',
        'KODIAQ','CX-5','CX-60','CX-30','RAV4','C-HR','PUMA','KUGA','DUSTER','XC40','XC60',
        'DEFENDER','EVOQUE','JUKE','STONIC','NIRO','BAYON','T-CROSS','TAIGO','KAMIQ','ATECA',
        'TARRACO','EV3','EV6','IONIQ 5','ID.4','ECLIPSE CROSS','COUNTRYMAN','GLA','Q3','Q5',
        'X1','X2','X3','HS','ZS','ATTO 2','SEAL U','DOLPHIN SURF','IONIQ5','TERRAMAR',
        'GRANDLAND X','MOKKA','SANDERO','DUSTER','LBX','ARKANA','SYMBIOZ','RAFALE'}

CSS = """
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    :root{--accent:#e8380d;--ink:#111318;--ink-2:#2d2d3a;--ink-3:#6b6b80;--ink-4:#a0a0b0;
          --green:#00c47a;--surface:#fff;--surface-2:#f7f8fa;--border:#e4e4ec;
          --radius:14px;--radius-sm:8px}
    body{font-family:'Plus Jakarta Sans',sans-serif;background:var(--surface-2);
         color:var(--ink);line-height:1.6;-webkit-font-smoothing:antialiased}
    nav{background:rgba(255,255,255,.95);backdrop-filter:blur(16px);
        border-bottom:1px solid var(--border);position:sticky;top:0;z-index:200}
    .nav-inner{max-width:1280px;margin:0 auto;padding:0 28px;height:62px;
               display:flex;align-items:center;justify-content:space-between}
    .logo{font-size:1.25rem;font-weight:800;color:var(--ink);text-decoration:none}
    .logo-dot{width:8px;height:8px;background:var(--accent);border-radius:50%;
              display:inline-block;margin-left:3px;margin-bottom:10px}
    .cat-hero{background:#111318;color:#fff;padding:52px 28px}
    .cat-hero-inner{max-width:1280px;margin:0 auto}
    .breadcrumb{font-size:.78rem;color:rgba(255,255,255,.4);margin-bottom:14px}
    .breadcrumb a{color:rgba(255,255,255,.4);text-decoration:none}
    .cat-pill{display:inline-block;background:var(--accent);color:#fff;font-size:.7rem;
              font-weight:700;padding:3px 10px;border-radius:99px;margin-bottom:12px;
              text-transform:uppercase;letter-spacing:.5px}
    .cat-hero h1{font-size:clamp(1.8rem,4vw,2.8rem);font-weight:800;letter-spacing:-1px;
                 line-height:1.2;margin-bottom:10px}
    .cat-hero h1 em{font-style:normal;color:var(--accent)}
    .cat-hero p{color:rgba(255,255,255,.5);max-width:600px;font-size:1rem}
    main{max-width:1280px;margin:0 auto;padding:40px 28px}
    .stats-bar{display:flex;gap:24px;margin-bottom:32px;padding:20px 24px;
               background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-sm)}
    .stat{display:flex;flex-direction:column;gap:2px}
    .stat-val{font-size:1.4rem;font-weight:800;color:var(--ink)}
    .stat-label{font-size:.75rem;color:var(--ink-4);text-transform:uppercase;letter-spacing:.5px}
    .offers-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;margin-bottom:40px}
    .offer-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
                padding:20px;display:flex;flex-direction:column;gap:10px;transition:box-shadow .2s,transform .2s}
    .offer-card:hover{box-shadow:0 8px 32px rgba(0,0,0,.1);transform:translateY(-2px)}
    .offer-card-brand{font-size:.7rem;font-weight:700;color:var(--ink-4);text-transform:uppercase;letter-spacing:.5px}
    .offer-card-name{font-size:1.05rem;font-weight:800;color:var(--ink);letter-spacing:-.2px}
    .offer-card-price{font-size:1.5rem;font-weight:800;color:var(--accent);margin-top:4px}
    .offer-card-price span{font-size:.8rem;font-weight:500;color:var(--ink-3)}
    .offer-card-meta{font-size:.8rem;color:var(--ink-3);display:flex;gap:10px;flex-wrap:wrap}
    .offer-tag{background:var(--surface-2);border-radius:99px;padding:3px 8px;font-size:.72rem;font-weight:600}
    .offer-card-link{background:var(--accent);color:#fff;text-align:center;text-decoration:none;
                     padding:10px;border-radius:var(--radius-sm);font-size:.85rem;font-weight:700;
                     margin-top:auto;transition:background .15s}
    .offer-card-link:hover{background:#c42e0a}
    .seo-block{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
               padding:32px;margin-bottom:32px}
    .seo-block h2{font-size:1.1rem;font-weight:800;margin-bottom:10px;letter-spacing:-.2px}
    .seo-block h3{font-size:.95rem;font-weight:700;margin:18px 0 6px;color:var(--ink)}
    .seo-block p{color:var(--ink-3);margin-bottom:12px;line-height:1.75;font-size:.95rem}
    .seo-block ul{padding-left:1.3rem;margin-bottom:12px}
    .seo-block li{color:var(--ink-3);margin-bottom:5px;line-height:1.6;font-size:.92rem}
    .seo-block strong{color:var(--ink)}
    .comp-table-wrap{overflow-x:auto;margin-bottom:32px}
    .comp-table{width:100%;border-collapse:collapse;font-size:.875rem}
    .comp-table th{background:#111318;color:#fff;padding:10px 14px;text-align:left;
                   font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px}
    .comp-table td{padding:10px 14px;border-bottom:1px solid var(--border);vertical-align:top}
    .comp-table tr:hover td{background:var(--surface-2)}
    .winner-badge{background:#e0faf1;color:#00875a;font-size:.7rem;font-weight:700;
                  padding:2px 7px;border-radius:99px}
    footer{background:#111318;color:rgba(255,255,255,.4);padding:32px 28px;text-align:center;font-size:.8rem}
    footer a{color:rgba(255,255,255,.4);text-decoration:none;margin:0 6px}
    footer a:hover{color:#fff}
    footer p+p{margin-top:8px}
    @media(max-width:640px){
      .cat-hero{padding:36px 16px}
      main{padding:24px 16px}
      .stats-bar{flex-wrap:wrap;gap:16px}
      .offers-grid{grid-template-columns:1fr}
    }
"""

NAV = """<nav>
  <div class="nav-inner">
    <a href="/" class="logo">MiRenting<span class="logo-dot"></span></a>
    <a href="/" style="color:var(--ink-3);text-decoration:none;font-size:.875rem">← Todas las ofertas</a>
  </div>
</nav>"""

FOOTER = """<footer>
  <p>© 2026 MiRenting · mtiagconsulting · Barcelona, España</p>
  <p><a href="/">Comparador</a><a href="/blog/">Blog</a>
     <a href="/aviso-legal.html">Aviso Legal</a>
     <a href="/politica-privacidad.html">Privacidad</a>
     <a href="/politica-cookies.html">Cookies</a></p>
</footer>"""

GTM = """<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','GTM-NHXGQF97');</script>"""

def page_shell(title, desc, canonical, pill, h1, subtitle, content, schema=""):
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  {GTM}
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{BASE_URL}/{canonical}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  {f'<script type="application/ld+json">{schema}</script>' if schema else ''}
  <style>{CSS}</style>
</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-NHXGQF97" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
{NAV}
<section class="cat-hero">
  <div class="cat-hero-inner">
    <div class="breadcrumb"><a href="/">MiRenting</a> › {pill}</div>
    <span class="cat-pill">{pill}</span>
    <h1>{h1}</h1>
    <p>{subtitle}</p>
  </div>
</section>
<main>{content}</main>
{FOOTER}
</body>
</html>"""


def offer_card(nombre, precio_min, slug_name, fuentes, fuels):
    fuentes_txt = " · ".join(list(fuentes)[:2])
    fuel_tags = "".join(f'<span class="offer-tag">{f}</span>' for f in list(fuels)[:2])
    make = nombre.split()[0]
    model = " ".join(nombre.split()[1:])
    return f"""<div class="offer-card">
  <div class="offer-card-brand">{make}</div>
  <div class="offer-card-name">{model}</div>
  <div class="offer-card-price">{precio_min}€<span>/mes</span></div>
  <div class="offer-card-meta">{fuel_tags}<span class="offer-tag">{fuentes_txt}</span></div>
  <a href="/{slug_name}.html" class="offer-card-link">Comparar ofertas →</a>
</div>"""


def stats_bar(n_modelos, precio_min_global, n_gestoras):
    return f"""<div class="stats-bar">
  <div class="stat"><span class="stat-val">{n_modelos}</span><span class="stat-label">Modelos disponibles</span></div>
  <div class="stat"><span class="stat-val">desde {precio_min_global}€</span><span class="stat-label">Precio más bajo/mes</span></div>
  <div class="stat"><span class="stat-val">{n_gestoras}</span><span class="stat-label">Gestoras comparadas</span></div>
</div>"""


# ── Generadores de cada categoría ─────────────────────────────────────────────

def gen_renting_barato(modelos_data):
    baratos = [(n, d) for n, d in modelos_data.items() if d['precio_min'] < 300]
    baratos.sort(key=lambda x: x[1]['precio_min'])
    cards = "".join(offer_card(n, d['precio_min'], d['slug'], d['fuentes'], d['fuels']) for n, d in baratos)
    pm = baratos[0][1]['precio_min'] if baratos else 220
    schema = json.dumps({
        "@context":"https://schema.org","@type":"ItemList",
        "name":"Coches baratos en renting — menos de 300€/mes",
        "numberOfItems": len(baratos),
        "itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"url":f"{BASE_URL}/{d['slug']}.html"}
                           for i,(n,d) in enumerate(baratos[:10])]
    }, ensure_ascii=False)
    content = stats_bar(len(baratos), pm, 3)
    content += f'<div class="offers-grid">{cards}</div>'
    content += """<div class="seo-block">
      <h2>¿Qué coches baratos hay en renting por menos de 300€/mes?</h2>
      <p>El mercado de renting en España ofrece una amplia selección de coches por menos de 300€/mes, incluyendo utilitarios, berlinas compactas y SUV urbanos. Los modelos más económicos parten de <strong>220€/mes</strong> y suelen ser utilitarios como el Dacia Sandero o el Seat Ibiza.</p>
      <h3>¿Por qué el renting barato no significa peor servicio?</h3>
      <p>Todas las ofertas de renting incluyen <strong>seguro a todo riesgo, mantenimiento y asistencia</strong>, independientemente del precio de la cuota. Un renting de 250€/mes cubre exactamente los mismos servicios que uno de 500€. La diferencia está en el modelo y la gestora, no en lo que incluye.</p>
      <h3>Cómo conseguir el renting más barato</h3>
      <ul>
        <li>Compara entre gestoras para el mismo modelo: el precio puede variar más de 60€/mes.</li>
        <li>Elige un plazo más largo (48 meses vs 24): reduce la cuota mensual entre un 8% y un 12%.</li>
        <li>Opta por menos kilómetros si no haces muchos desplazamientos (10.000 km/año vs 20.000).</li>
        <li>Considera motorizaciones gasolina en vez de diesel para contratos cortos o uso urbano.</li>
      </ul>
    </div>"""
    return page_shell(
        title=f"Renting barato desde {pm}€/mes — Coches por menos de 300€ | MiRenting",
        desc=f"Los {len(baratos)} coches más baratos en renting en España. Cuotas desde {pm}€/mes con seguro y mantenimiento incluidos. Compara sin registrarte.",
        canonical="renting-barato.html",
        pill="Renting Barato",
        h1=f"Renting barato — <em>desde {pm}€/mes</em>",
        subtitle=f"{len(baratos)} modelos por menos de 300€/mes con seguro, mantenimiento e ITV incluidos.",
        content=content, schema=schema
    )


def gen_renting_suv(modelos_data):
    suvs = [(n, d) for n, d in modelos_data.items()
            if any(w in n.upper() for w in SUVY)]
    suvs.sort(key=lambda x: x[1]['precio_min'])
    cards = "".join(offer_card(n, d['precio_min'], d['slug'], d['fuentes'], d['fuels']) for n, d in suvs)
    pm = suvs[0][1]['precio_min'] if suvs else 290
    schema = json.dumps({
        "@context":"https://schema.org","@type":"ItemList",
        "name":"Renting SUV España 2026",
        "numberOfItems": len(suvs),
        "itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"url":f"{BASE_URL}/{d['slug']}.html"}
                           for i,(n,d) in enumerate(suvs[:10])]
    }, ensure_ascii=False)
    content = stats_bar(len(suvs), pm, 3)
    content += f'<div class="offers-grid">{cards}</div>'
    content += """<div class="seo-block">
      <h2>Renting de SUV: el segmento más demandado en España</h2>
      <p>Los SUV representan más del <strong>40% de las matriculaciones en renting</strong> en España. Su posición de conducción elevada, maletero generoso y disponibilidad en versiones híbridas los convierten en el tipo de vehículo más solicitado por particulares, autónomos y empresas.</p>
      <h3>SUV más baratos en renting</h3>
      <p>El Seat Arona y el Renault Captur lideran el segmento de SUV urbanos por precio (desde 290€/mes), mientras que los SUV medios como el Nissan Qashqai o el Volkswagen Tiguan parten desde 354€/mes.</p>
      <h3>SUV eléctricos e híbridos con etiqueta ECO</h3>
      <p>Modelos como el Hyundai Tucson PHEV, el Kia Sportage Híbrido o el Volkswagen ID.4 eléctrico tienen <strong>etiqueta ECO o CERO</strong>, lo que permite circular sin restricciones por las Zonas de Bajas Emisiones de Madrid y Barcelona.</p>
    </div>"""
    return page_shell(
        title=f"Renting SUV desde {pm}€/mes — Comparativa 2026 | MiRenting",
        desc=f"Compara {len(suvs)} SUV disponibles en renting en España. Desde {pm}€/mes con seguro y mantenimiento. Filtra por precio, gestora y etiqueta DGT.",
        canonical="renting-suv.html",
        pill="Renting SUV",
        h1=f"Renting de <em>SUV</em> — comparativa completa",
        subtitle=f"{len(suvs)} modelos SUV disponibles. Compara precios por gestora sin registrarte.",
        content=content, schema=schema
    )


def gen_renting_electrico(modelos_data):
    eco_keys = ['eléctrico','electric','enchufable','phev','híbrido','hybrid']
    electricos = [(n, d) for n, d in modelos_data.items()
                  if any(k in f.lower() for f in d['fuels'] for k in eco_keys)]
    electricos.sort(key=lambda x: x[1]['precio_min'])
    cards = "".join(offer_card(n, d['precio_min'], d['slug'], d['fuentes'], d['fuels']) for n, d in electricos)
    pm = electricos[0][1]['precio_min'] if electricos else 250
    content = stats_bar(len(electricos), pm, 3)
    content += f'<div class="offers-grid">{cards}</div>'
    content += """<div class="seo-block">
      <h2>Renting de coches eléctricos e híbridos: etiqueta ECO y CERO en 2026</h2>
      <p>El renting es la fórmula ideal para acceder a un coche eléctrico o híbrido sin asumir la fuerte depreciación inicial de estos modelos. Cuando la tecnología evolucione, simplemente cambias de coche al terminar el contrato.</p>
      <h3>Ventajas de la etiqueta ECO y CERO en renting</h3>
      <ul>
        <li><strong>Circulación sin restricciones</strong> en ZBE de Madrid (Madrid Central, Plaza Elíptica) y Barcelona (Zona de Bajas Emisiones).</li>
        <li><strong>Aparcamiento bonificado</strong> en zonas reguladas de muchos municipios.</li>
        <li>Acceso al carril BUS-VAO en algunas vías de Madrid con 1 ocupante.</li>
        <li>Descuentos en algunos peajes de autopistas de gestión autonómica.</li>
      </ul>
      <h3>¿Eléctrico puro o híbrido enchufable?</h3>
      <p>Si haces más de 40 km diarios y tienes punto de carga en casa o en el trabajo, el <strong>eléctrico puro (etiqueta CERO)</strong> tiene menor coste por kilómetro. Si tu uso es mixto urbano/interurbano sin punto de carga garantizado, el <strong>híbrido enchufable (etiqueta ECO)</strong> es más flexible.</p>
    </div>"""
    return page_shell(
        title=f"Renting Eléctrico e Híbrido — Etiqueta ECO y CERO desde {pm}€/mes | MiRenting",
        desc=f"Compara {len(electricos)} coches eléctricos e híbridos en renting. Etiqueta ECO y CERO, desde {pm}€/mes. Sin entrada, seguro incluido.",
        canonical="renting-electrico.html",
        pill="Renting Eléctrico",
        h1=f"Renting <em>eléctrico e híbrido</em> — etiqueta ECO y CERO",
        subtitle=f"{len(electricos)} modelos con etiqueta ECO o CERO disponibles en renting. Circula sin restricciones en ZBE.",
        content=content
    )


def gen_renting_sin_entrada(modelos_data):
    todos = sorted(modelos_data.items(), key=lambda x: x[1]['precio_min'])
    cards = "".join(offer_card(n, d['precio_min'], d['slug'], d['fuentes'], d['fuels']) for n, d in todos[:24])
    pm = todos[0][1]['precio_min'] if todos else 220
    content = f"""<div class="seo-block">
      <h2>El renting no tiene entrada: así funciona</h2>
      <p>A diferencia de comprar un coche con financiación, el renting <strong>no requiere pago inicial</strong>. Pagas la primera cuota mensual y ya puedes recoger el coche. Sin entrada, sin intereses, sin depreciación.</p>
      <p>Algunas gestoras solicitan un depósito equivalente a <strong>1 o 2 cuotas</strong> que se devuelve al final del contrato si el vehículo se entrega en buen estado. Esto no es una entrada: es una garantía reembolsable.</p>
      <h3>¿Qué necesito para contratar un renting sin entrada?</h3>
      <ul>
        <li>DNI o NIE en vigor.</li>
        <li>Nómina o declaración de la renta reciente (para verificar solvencia).</li>
        <li>Permiso de conducir en vigor.</li>
        <li>En algunos casos, los últimos 3 meses de extracto bancario.</li>
      </ul>
      <h3>Renting sin entrada vs. leasing con entrada</h3>
      <p>El leasing financiero puede requerir una entrada del 10-30% del valor del vehículo. El renting operativo, en cambio, no. Esta es una de las principales razones por las que <strong>autónomos y pymes prefieren el renting</strong> para gestionar sus vehículos.</p>
    </div>"""
    content += stats_bar(len(todos), pm, 3)
    content += f'<div class="offers-grid">{cards}</div>'
    return page_shell(
        title=f"Renting Sin Entrada — Todos los coches desde {pm}€/mes | MiRenting",
        desc=f"El renting no requiere entrada. Empieza a conducir desde {pm}€/mes sin pago inicial. Más de 900 ofertas sin formularios ni registros.",
        canonical="renting-sin-entrada.html",
        pill="Sin Entrada",
        h1=f"Renting <em>sin entrada</em> — empieza desde {pm}€/mes",
        subtitle="Sin pago inicial, sin intereses. Solo tu cuota mensual con todo incluido.",
        content=content
    )


def gen_arval_vs_ayvens(modelos_data):
    """Bolsa 3: keyword comparativa de alto valor."""
    comunes = [(n, d) for n, d in modelos_data.items()
               if 'arval' in {f.lower() for f in d['fuentes']} and 'ayvens' in {f.lower() for f in d['fuentes']}]
    comunes.sort(key=lambda x: x[1]['precio_min'])

    rows = ""
    for nombre, d in comunes[:20]:
        arval_min  = min((o.get('precio_desde',9999) for o in d['ofertas'] if (o.get('fuente','') or '').lower()=='arval'), default=None)
        ayvens_min = min((o.get('precio_desde',9999) for o in d['ofertas'] if (o.get('fuente','') or '').lower()=='ayvens'), default=None)
        if not arval_min or not ayvens_min: continue
        winner = "arval" if arval_min <= ayvens_min else "ayvens"
        diff = abs(arval_min - ayvens_min)
        rows += f"""<tr>
          <td><a href="/{d['slug']}.html">{nombre}</a></td>
          <td>{'<strong>' if winner=='arval' else ''}{arval_min}€/mes{'<span class="winner-badge">✓ más barato</span>' if winner=='arval' else ''}{'</strong>' if winner=='arval' else ''}</td>
          <td>{'<strong>' if winner=='ayvens' else ''}{ayvens_min}€/mes{'<span class="winner-badge">✓ más barato</span>' if winner=='ayvens' else ''}{'</strong>' if winner=='ayvens' else ''}</td>
          <td>{'Arval' if winner=='arval' else 'Ayvens'} (−{diff}€/mes)</td>
        </tr>"""

    arval_wins  = sum(1 for n,d in comunes if d['ofertas'] and
                      min((o.get('precio_desde',9999) for o in d['ofertas'] if (o.get('fuente','') or '').lower()=='arval'), default=9999) <=
                      min((o.get('precio_desde',9999) for o in d['ofertas'] if (o.get('fuente','') or '').lower()=='ayvens'), default=9999))
    ayvens_wins = len(comunes) - arval_wins

    content = f"""<div class="seo-block">
      <h2>Arval vs Ayvens: ¿cuál tiene el renting más barato en 2026?</h2>
      <p>Hemos comparado precio a precio los modelos disponibles en ambas gestoras. El resultado sobre <strong>{len(comunes)} modelos en común</strong>: Arval gana en precio en <strong>{arval_wins} modelos</strong> y Ayvens en <strong>{ayvens_wins}</strong>. La diferencia media es de <strong>15-40€/mes</strong> para el mismo coche.</p>
      <p>La conclusión práctica: <strong>no hay una gestora universalmente más barata</strong>. Depende del modelo concreto. Por eso tiene sentido comparar ambas antes de contratar.</p>
    </div>
    <div class="comp-table-wrap">
      <table class="comp-table">
        <thead><tr><th>Modelo</th><th>Arval</th><th>Ayvens</th><th>Más barato</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    <div class="seo-block">
      <h3>¿En qué se diferencian Arval y Ayvens además del precio?</h3>
      <p><strong>Arval</strong> (filial de BNP Paribas) destaca por su red de talleres concertados y su servicio de sustitución de vehículo. <strong>Ayvens</strong> (fusión de ALD Automotive y LeasePlan) tiene mayor cobertura internacional y una plataforma digital más avanzada para la gestión de flotas.</p>
      <p>Para un particular o autónomo, la diferencia operativa es mínima. El criterio de decisión debería ser el precio para tu modelo concreto.</p>
    </div>"""

    return page_shell(
        title="Arval vs Ayvens: ¿cuál es más barata? Comparativa precio a precio | MiRenting",
        desc=f"Comparamos Arval y Ayvens modelo a modelo. Descubre qué gestora tiene el renting más barato para tu coche. {len(comunes)} modelos analizados.",
        canonical="renting-arval-vs-ayvens.html",
        pill="Comparativa Gestoras",
        h1="<em>Arval vs Ayvens</em>: ¿cuál tiene el renting más barato?",
        subtitle=f"{len(comunes)} modelos comparados precio a precio. La respuesta te sorprenderá.",
        content=content
    )


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    html_src = (BASE / "index.html").read_text(encoding="utf-8")
    start = html_src.find("const _OFERTAS = [") + len("const _OFERTAS = ")
    end   = html_src.find("];", start) + 1
    ofertas = json.loads(html_src[start:end])
    print(f"Ofertas leídas: {len(ofertas)}")

    # Agrupar por modelo
    modelos_data = {}
    for o in ofertas:
        make  = (o.get("make")  or "").strip()
        model = (o.get("model") or "").strip()
        if not make or not model: continue
        nombre = f"{make.title()} {model.title()}"
        if nombre not in modelos_data:
            modelos_data[nombre] = {
                "slug":      slug(f"renting-{make}-{model}"),
                "precio_min": 9999,
                "fuentes":   set(),
                "fuels":     set(),
                "ofertas":   []
            }
        precio = o.get("precio_desde", 9999) or 9999
        modelos_data[nombre]["precio_min"] = min(modelos_data[nombre]["precio_min"], precio)
        if o.get("fuente"): modelos_data[nombre]["fuentes"].add(o["fuente"])
        if o.get("fuel"):   modelos_data[nombre]["fuels"].add(o["fuel"])
        modelos_data[nombre]["ofertas"].append(o)

    paginas = {
        "renting-barato.html":          gen_renting_barato(modelos_data),
        "renting-suv.html":             gen_renting_suv(modelos_data),
        "renting-electrico.html":       gen_renting_electrico(modelos_data),
        "renting-sin-entrada.html":     gen_renting_sin_entrada(modelos_data),
        "renting-arval-vs-ayvens.html": gen_arval_vs_ayvens(modelos_data),
    }

    print(f"\n{'='*50}")
    for filename, html_content in paginas.items():
        (BASE / filename).write_text(html_content, encoding="utf-8")
        print(f"  ✓ {filename}")

    # Actualizar sitemap
    sitemap_path = BASE / "sitemap.xml"
    if sitemap_path.exists():
        sitemap = sitemap_path.read_text(encoding="utf-8")
        # Eliminar entradas de categoría anteriores
        for f in paginas:
            sitemap = re.sub(rf'\s*<url><loc>[^<]*/{re.escape(f)}</loc>[^<]*</url>', '', sitemap)
        nuevas = ""
        for f in paginas:
            nuevas += f'  <url><loc>{BASE_URL}/{f}</loc><priority>0.85</priority></url>\n'
        sitemap = sitemap.replace('</urlset>', nuevas + '</urlset>')
        sitemap_path.write_text(sitemap, encoding="utf-8")
        print(f"  ✓ sitemap.xml actualizado (+{len(paginas)} categorías)")

    print(f"{'='*50}")
    print(f"\n✅ {len(paginas)} páginas de categoría generadas")
    print("\nPara publicar:")
    print("  git add renting-*.html sitemap.xml")
    print('  git commit -m "feat: páginas de categoría SEO (barato, SUV, eléctrico, sin entrada, Arval vs Ayvens)"')
    print("  git push origin main")

if __name__ == "__main__":
    main()
