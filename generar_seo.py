"""
Genera páginas HTML individuales por modelo para SEO.
Ejecutar: python3 generar_seo.py
"""

import json, re
from pathlib import Path

BASE = Path("/Users/matthiasthomassen/Documents/Myrenting")
HTML_PATH = BASE / "index.html"

def slug(texto):
    t = texto.lower()
    t = t.replace(" ", "-")
    t = re.sub(r'[áàä]', 'a', t)
    t = re.sub(r'[éèë]', 'e', t)
    t = re.sub(r'[íìï]', 'i', t)
    t = re.sub(r'[óòö]', 'o', t)
    t = re.sub(r'[úùü]', 'u', t)
    t = re.sub(r'[^a-z0-9-]', '-', t)
    t = re.sub(r'-+', '-', t).strip('-')
    return t

def etiqueta_dgt(fuel):
    f = fuel.lower()
    if 'eléctrico' in f: return '🟢 CERO'
    if 'enchufable' in f: return '🔵 ECO'
    if 'híbrido' in f or 'hibrido' in f: return '🔵 ECO'
    if 'gasolina' in f: return '🟡 C'
    if 'diésel' in f or 'diesel' in f: return '🟡 C'
    return ''

def generar_pagina(make, model, ofertas_modelo):
    nombre = f"{make.title()} {model.title()}"
    slug_name = slug(f"renting-{make}-{model}")
    
    precio_min = min(o.get('precio_desde', 9999) for o in ofertas_modelo)
    gestoras = sorted(set(o.get('fuente','') for o in ofertas_modelo))
    fuels = sorted(set(o.get('fuel','') for o in ofertas_modelo))
    
    # Imagen — coger la primera disponible
    imagen = next((o.get('image','') for o in ofertas_modelo if o.get('image')), '')
    
    # Ordenar ofertas por precio
    ofertas_sorted = sorted(ofertas_modelo, key=lambda x: x.get('precio_desde', 9999))
    
    # Generar filas de la tabla
    filas = ""
    for i, o in enumerate(ofertas_sorted):
        precio = o.get('precio_desde', 0)
        fuente = o.get('fuente', '—')
        tipo = o.get('tipo', '—')
        fuel = o.get('fuel', '—')
        version = o.get('version', '—')
        link = o.get('link_oferta', '#')
        
        duracion = '—'
        km = '—'
        if o.get('precios') and len(o['precios']) > 0:
            duracion = f"{o['precios'][0][0]} meses"
            km = f"{int(o['precios'][0][1]):,} km/año".replace(',', '.')

        es_mejor = i == 0
        clase_fila = 'best-row' if es_mejor else ''
        badge = '<span class="best-badge">✓ Mejor precio</span><br>' if es_mejor else ''
        dgt = etiqueta_dgt(fuel)
        
        filas += f"""
        <tr class="{clase_fila}">
          <td>{'<span class="rank-star">★</span>' if es_mejor else f'<span class="rank-num">{i+1}</span>'}</td>
          <td><strong>{fuente}</strong></td>
          <td><span class="tipo-badge">{tipo}</span></td>
          <td>{fuel} {dgt}</td>
          <td>{duracion}</td>
          <td>{km}</td>
          <td class="version-cell">{version[:60]}{'...' if len(version)>60 else ''}</td>
          <td>{badge}<span class="price-strong">{precio} €/mes</span></td>
          <td><a href="{link}" target="_blank" rel="noopener" class="btn-ver">Ver oferta →</a></td>
        </tr>"""

    # Texto SEO
    gestoras_texto = ', '.join(gestoras[:-1]) + (' y ' + gestoras[-1] if len(gestoras) > 1 else gestoras[0])
    fuels_texto = ', '.join(fuels)
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <!-- Google Tag Manager -->
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
  new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
  }})(window,document,'script','dataLayer','GTM-NHXGQF97');</script>
  <!-- End Google Tag Manager -->

  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Renting {nombre} desde {precio_min}€/mes | Comparar {gestoras_texto} | MiRenting</title>
  <meta name="description" content="Compara el renting del {nombre} en {gestoras_texto}. Precio desde {precio_min}€/mes. {len(ofertas_modelo)} ofertas con diferentes plazos y kilómetros. Sin letra pequeña.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://www.myrenting.es/{slug_name}.html">
  <meta property="og:title" content="Renting {nombre} — Comparativa de precios | MiRenting">
  <meta property="og:description" content="Compara el renting del {nombre} desde {precio_min}€/mes en {gestoras_texto}.">
  <meta property="og:url" content="https://www.myrenting.es/{slug_name}.html">
  <meta property="og:type" content="website">
  {'<meta property="og:image" content="' + imagen + '">' if imagen else ''}
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">

  <!-- Schema.org -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "Renting {nombre}",
    "description": "Comparativa de renting del {nombre} en {gestoras_texto}",
    "offers": {{
      "@type": "AggregateOffer",
      "lowPrice": "{precio_min}",
      "priceCurrency": "EUR",
      "offerCount": "{len(ofertas_modelo)}"
    }}
  }}
  </script>

  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --accent: #e8380d; --accent-2: #c42e0a;
      --ink: #111318; --ink-2: #2d2d3a; --ink-3: #6b6b80; --ink-4: #a0a0b0;
      --green: #00c47a; --green-lt: #e0faf1;
      --surface: #ffffff; --surface-2: #f7f8fa; --surface-3: #eeeff4;
      --border: #e4e4ec; --border-2: #d0d0dc;
      --radius: 14px; --radius-sm: 8px;
      --shadow-lg: 0 12px 48px rgba(0,0,0,.12);
    }}
    body {{ font-family: 'Plus Jakarta Sans', sans-serif; background: var(--surface-2); color: var(--ink); line-height: 1.6; -webkit-font-smoothing: antialiased; }}
    
    nav {{ background: rgba(255,255,255,.95); backdrop-filter: blur(16px); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 200; }}
    .nav-inner {{ max-width: 1280px; margin: 0 auto; padding: 0 28px; height: 62px; display: flex; align-items: center; justify-content: space-between; }}
    .logo {{ font-size: 1.25rem; font-weight: 800; color: var(--ink); text-decoration: none; }}
    .logo-dot {{ width: 8px; height: 8px; background: var(--accent); border-radius: 50%; display: inline-block; margin-left: 3px; margin-bottom: 10px; }}
    .nav-back {{ color: var(--ink-3); text-decoration: none; font-size: .875rem; font-weight: 500; }}
    .nav-back:hover {{ color: var(--ink); }}

    .hero-model {{ background: #111318; color: #fff; padding: 48px 28px; }}
    .hero-model-inner {{ max-width: 1280px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 40px; align-items: center; }}
    .breadcrumb {{ font-size: .78rem; color: rgba(255,255,255,.4); margin-bottom: 12px; }}
    .breadcrumb a {{ color: rgba(255,255,255,.4); text-decoration: none; }}
    .breadcrumb a:hover {{ color: #fff; }}
    .hero-model h1 {{ font-size: clamp(1.8rem, 4vw, 2.8rem); font-weight: 800; letter-spacing: -1px; margin-bottom: 12px; }}
    .hero-model h1 em {{ font-style: normal; color: var(--accent); }}
    .hero-stats {{ display: flex; gap: 24px; margin-top: 20px; flex-wrap: wrap; }}
    .hero-stat {{ background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.12); border-radius: var(--radius-sm); padding: 12px 16px; }}
    .hero-stat-label {{ font-size: .7rem; font-weight: 700; color: rgba(255,255,255,.4); text-transform: uppercase; letter-spacing: .5px; }}
    .hero-stat-value {{ font-size: 1.2rem; font-weight: 800; color: #fff; margin-top: 2px; }}
    .hero-model-img {{ border-radius: var(--radius); overflow: hidden; max-height: 280px; }}
    .hero-model-img img {{ width: 100%; height: 100%; object-fit: cover; }}

    main {{ max-width: 1280px; margin: 40px auto; padding: 0 28px; }}
    
    .section-title {{ font-size: 1.3rem; font-weight: 800; margin-bottom: 20px; letter-spacing: -0.3px; }}

    .comp-panel {{ background: var(--surface); border-radius: var(--radius); border: 1px solid var(--border); overflow: hidden; margin-bottom: 40px; }}
    .comp-table-wrap {{ overflow-x: auto; }}
    .comp-table {{ width: 100%; border-collapse: collapse; }}
    .comp-table thead th {{ background: var(--surface-2); padding: 10px 16px; text-align: left; font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .6px; color: var(--ink-4); border-bottom: 2px solid var(--border); white-space: nowrap; }}
    .comp-table tbody tr {{ border-bottom: 1px solid var(--border); transition: background .1s; }}
    .comp-table tbody tr:hover {{ background: var(--surface-2); }}
    .comp-table tbody tr.best-row {{ background: var(--green-lt); }}
    .comp-table tbody td {{ padding: 12px 16px; font-size: .875rem; color: var(--ink-2); vertical-align: middle; }}
    .rank-num {{ width: 28px; height: 28px; background: var(--surface-3); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: .78rem; font-weight: 700; color: var(--ink-3); }}
    .rank-star {{ width: 28px; height: 28px; background: var(--green); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: .82rem; color: #fff; }}
    .best-badge {{ display: inline-flex; align-items: center; background: var(--green); color: #fff; font-size: .65rem; font-weight: 700; padding: 2px 8px; border-radius: 99px; margin-bottom: 4px; }}
    .price-strong {{ font-size: 1rem; font-weight: 800; color: var(--ink); }}
    .best-row .price-strong {{ color: #00875a; }}
    .version-cell {{ max-width: 200px; font-size: .78rem; color: var(--ink-3); }}
    .tipo-badge {{ font-size: .68rem; font-weight: 600; padding: 2px 7px; border-radius: 99px; background: var(--surface-3); color: var(--ink-3); border: 1px solid var(--border); text-transform: uppercase; }}
    .btn-ver {{ background: var(--ink); color: #fff; text-decoration: none; padding: 7px 14px; border-radius: var(--radius-sm); font-size: .78rem; font-weight: 700; white-space: nowrap; transition: background .15s; }}
    .btn-ver:hover {{ background: var(--accent); }}

    .seo-section {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 32px; margin-bottom: 40px; }}
    .seo-section h2 {{ font-size: 1.2rem; font-weight: 800; margin-bottom: 12px; }}
    .seo-section h3 {{ font-size: 1rem; font-weight: 700; margin: 20px 0 8px; }}
    .seo-section p {{ color: var(--ink-3); margin-bottom: 12px; line-height: 1.7; }}

    .cta-section {{ background: #111318; color: #fff; border-radius: var(--radius); padding: 40px; text-align: center; margin-bottom: 40px; }}
    .cta-section h2 {{ font-size: 1.4rem; font-weight: 800; margin-bottom: 8px; }}
    .cta-section p {{ color: rgba(255,255,255,.5); margin-bottom: 24px; }}
    .btn-cta {{ background: var(--accent); color: #fff; text-decoration: none; padding: 14px 28px; border-radius: var(--radius-sm); font-size: .95rem; font-weight: 700; transition: background .15s; display: inline-block; }}
    .btn-cta:hover {{ background: var(--accent-2); }}

    footer {{ background: #111318; color: rgba(255,255,255,.4); padding: 32px 28px; text-align: center; font-size: .8rem; }}
    footer a {{ color: rgba(255,255,255,.4); text-decoration: none; }}
    footer a:hover {{ color: #fff; }}

    @media (max-width: 768px) {{
      .hero-model-inner {{ grid-template-columns: 1fr; }}
      .hero-model-img {{ display: none; }}
    }}
  </style>
</head>
<body>

<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-NHXGQF97" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>

<nav>
  <div class="nav-inner">
    <a href="/" class="logo">MiRenting<span class="logo-dot"></span></a>
    <a href="/" class="nav-back">← Ver todas las ofertas</a>
  </div>
</nav>

<section class="hero-model">
  <div class="hero-model-inner">
    <div>
      <div class="breadcrumb">
        <a href="/">MiRenting</a> › <a href="/">Ofertas</a> › {nombre}
      </div>
      <h1>Renting <em>{nombre}</em><br>Comparativa de precios</h1>
      <p style="color:rgba(255,255,255,.55); margin-top:8px;">Compara {len(ofertas_modelo)} ofertas de {gestoras_texto}. Mismas condiciones, precios reales.</p>
      <div class="hero-stats">
        <div class="hero-stat">
          <div class="hero-stat-label">Desde</div>
          <div class="hero-stat-value">{precio_min} €/mes</div>
        </div>
        <div class="hero-stat">
          <div class="hero-stat-label">Ofertas</div>
          <div class="hero-stat-value">{len(ofertas_modelo)}</div>
        </div>
        <div class="hero-stat">
          <div class="hero-stat-label">Gestoras</div>
          <div class="hero-stat-value">{len(gestoras)}</div>
        </div>
      </div>
    </div>
    {'<div class="hero-model-img"><img src="' + imagen + '" alt="Renting ' + nombre + '" loading="lazy"></div>' if imagen else '<div></div>'}
  </div>
</section>

<main>
  <h2 class="section-title">Comparativa de precios — {nombre}</h2>
  
  <div class="comp-panel">
    <div class="comp-table-wrap">
      <table class="comp-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Gestora</th>
            <th>Cliente</th>
            <th>Combustible</th>
            <th>Plazo</th>
            <th>Km/año</th>
            <th>Versión</th>
            <th>Precio/mes</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {filas}
        </tbody>
      </table>
    </div>
  </div>

  <div class="seo-section">
    <h2>Renting {nombre}: todo lo que necesitas saber</h2>
    <p>El <strong>renting del {nombre}</strong> es una de las opciones más demandadas en España. Con un precio desde <strong>{precio_min}€/mes</strong>, puedes disfrutar de este vehículo sin entrada y con todos los gastos incluidos: seguro, mantenimiento y asistencia en carretera.</p>
    
    <h3>¿Qué gestoras ofrecen el {nombre} en renting?</h3>
    <p>Actualmente puedes contratar el renting del {nombre} con {gestoras_texto}. En MiRenting comparamos todas las ofertas disponibles con las mismas condiciones para que puedas elegir la más barata.</p>

    <h3>Combustibles disponibles</h3>
    <p>El {nombre} está disponible en las siguientes motorizaciones: {fuels_texto}. {'La versión eléctrica o híbrida tiene etiqueta ECO o CERO, lo que te permite circular por zonas de bajas emisiones.' if any('híbrido' in f.lower() or 'eléctrico' in f.lower() for f in fuels) else ''}</p>

    <h3>¿Cuánto cuesta el renting del {nombre}?</h3>
    <p>El precio del renting del {nombre} varía según el plazo y los kilómetros contratados. El precio más bajo que hemos encontrado es de <strong>{precio_min}€/mes</strong>. Para contratos más cortos o con más kilómetros, el precio sube proporcionalmente.</p>

    <h3>¿Qué incluye el renting del {nombre}?</h3>
    <p>El renting del {nombre} incluye normalmente: seguro a todo riesgo, mantenimiento preventivo y correctivo, asistencia en carretera 24h, gestión de multas e ITV. Consulta las condiciones exactas de cada gestora antes de contratar.</p>
  </div>

  <div class="cta-section">
    <h2>¿Buscas más opciones?</h2>
    <p>Compara más de 900 ofertas de renting de todas las gestoras</p>
    <a href="/" class="btn-cta">Ver todas las ofertas →</a>
  </div>
</main>

<footer>
  <p>© 2025 MiRenting · <a href="/">Comparador de renting</a> · Las ofertas son responsabilidad de cada gestora.</p>
</footer>

</body>
</html>"""
    return slug_name, html

def main():
    # Leer ofertas del HTML
    html = HTML_PATH.read_text(encoding="utf-8")
    start = html.find("const _OFERTAS = [") + len("const _OFERTAS = ")
    end = html.find("];", start) + 1
    ofertas = json.loads(html[start:end])
    print(f"Ofertas leídas: {len(ofertas)}")

    # Agrupar por make+model
    modelos = {}
    for o in ofertas:
        make = (o.get("make") or "").strip().upper()
        model = (o.get("model") or "").strip().upper()
        key = f"{make}||{model}"
        if key not in modelos:
            modelos[key] = []
        modelos[key].append(o)

    # Filtrar modelos con suficientes ofertas (mínimo 3)
    modelos_validos = {k: v for k, v in modelos.items() if len(v) >= 3}
    print(f"Modelos con 3+ ofertas: {len(modelos_validos)}")

    # Generar páginas
    paginas_generadas = []
    for key, ofertas_modelo in modelos_validos.items():
        make, model = key.split("||")
        if not make or not model:
            continue
        slug_name, html_pagina = generar_pagina(make, model, ofertas_modelo)
        path = BASE / f"{slug_name}.html"
        path.write_text(html_pagina, encoding="utf-8")
        paginas_generadas.append((slug_name, make, model, len(ofertas_modelo)))

    paginas_generadas.sort(key=lambda x: x[3], reverse=True)
    print(f"\n✓ {len(paginas_generadas)} páginas generadas:")
    for slug_name, make, model, n in paginas_generadas[:20]:
        print(f"  {slug_name}.html ({n} ofertas)")

    # Generar sitemap
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += '  <url><loc>https://www.myrenting.es/</loc><priority>1.0</priority></url>\n'
    for slug_name, _, _, _ in paginas_generadas:
        sitemap += f'  <url><loc>https://www.myrenting.es/{slug_name}.html</loc><priority>0.8</priority></url>\n'
    sitemap += '</urlset>'
    (BASE / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print(f"\n✓ sitemap.xml generado con {len(paginas_generadas)+1} URLs")

    # Generar lista de enlaces para añadir al index
    print("\nEnlaces para añadir al footer del index.html:")
    for slug_name, make, model, n in paginas_generadas[:10]:
        nombre = f"{make.title()} {model.title()}"
        print(f'  <a href="/{slug_name}.html">Renting {nombre}</a>')

if __name__ == "__main__":
    main()
