"""
Genera páginas HTML SEO individuales por modelo con:
- Title/meta optimizados con precio real y gestoras
- H1 orientado a intención de compra
- FAQ con schema JSON-LD
- Texto personalizado por modelo con precio, ahorro, combustible
- Schema Product con precios reales

Ejecutar: python3 generar_seo.py
"""

import json, re
from pathlib import Path

BASE = Path("/Users/matthiasthomassen/Documents/Myrenting")
HTML_PATH = BASE / "index.html"

def slug(texto):
    t = texto.lower()
    for a, b in [('á','a'),('à','a'),('é','e'),('è','e'),('í','i'),('ì','i'),
                 ('ó','o'),('ò','o'),('ú','u'),('ù','u'),('ü','u')]:
        t = t.replace(a, b)
    t = re.sub(r'[^a-z0-9]+', '-', t)
    return re.sub(r'-+', '-', t).strip('-')

def etiqueta_dgt(fuel):
    f = (fuel or "").lower()
    if 'eléctrico' in f or 'electric' in f: return '🟢 CERO'
    if 'enchufable' in f or 'phev' in f: return '🔵 ECO'
    if 'híbrido' in f or 'hybrid' in f: return '🔵 ECO'
    if 'gasolina' in f: return '🟡 C'
    if 'diésel' in f or 'diesel' in f: return '🟡 C'
    return ''

def es_electrico_o_hibrido(fuels):
    for f in fuels:
        f = f.lower()
        if 'eléctrico' in f or 'híbrido' in f or 'enchufable' in f:
            return True
    return False

def categoria_coche(make, model):
    suv = ['QASHQAI','T-ROC','TIGUAN','ARONA','SPORTAGE','KONA','TUCSON','FORMENTOR',
           'KAROQ','KODIAQ','CX-5','CX-60','CX-30','RAV4','C-HR','YARIS CROSS',
           'PUMA','KUGA','DUSTER','XC40','XC60','DEFENDER','EVOQUE','JUKE',
           'STONIC','NIRO','BAYON','T-CROSS','TAIGO','KAMIQ','ATECA','TARRACO',
           'EV3','EV6','IONIQ 5','BZ4X','ID.4','ECLIPSE CROSS','COUNTRYMAN','GLA','Q3',
           'Q5','X1','X2','X3','LBX','NX','RX','UX','TERRAMAR','SANDERO','DUSTER']
    furgoneta = ['KANGOO','BERLINGO','PARTNER','COMBO','TRAFIC','MASTER','SPRINTER',
                 'VITO','TRANSIT','PROACE','FIORINO','DOBLO','BOXER','EXPERT','RIFTER',
                 'CITAN','HILUX','RANGER','PROACE CITY']
    m = model.upper()
    for f in furgoneta:
        if f in m: return 'furgoneta'
    for s in suv:
        if s in m: return 'SUV'
    return 'berlina'

def generar_faq(nombre, precio_min, gestoras, fuels, make, model):
    g_texto = ' y '.join(gestoras) if len(gestoras) <= 2 else ', '.join(gestoras[:-1]) + ' y ' + gestoras[-1]
    cat = categoria_coche(make, model)
    eco = es_electrico_o_hibrido(fuels)
    faqs = [
        {
            "q": f"¿Cuánto cuesta el renting del {nombre}?",
            "a": f"El renting del {nombre} tiene un precio desde {precio_min}€/mes. Este precio varía según la duración del contrato, los kilómetros anuales y la gestora que elijas. En MiRenting comparamos todas las ofertas disponibles para que encuentres el precio más barato sin tener que llamar a nadie."
        },
        {
            "q": f"¿Qué gestora ofrece el {nombre} más barato?",
            "a": f"Puedes contratar el renting del {nombre} con {g_texto}. Los precios varían entre gestoras — en la tabla de esta página puedes comparar todas las ofertas con las mismas condiciones para encontrar la más barata."
        },
        {
            "q": f"¿Qué incluye el renting del {nombre}?",
            "a": f"El renting del {nombre} incluye seguro a todo riesgo, mantenimiento preventivo y correctivo, asistencia en carretera 24h, gestión de multas e ITV. Todo en una cuota mensual fija sin entrada ni sorpresas al final."
        },
        {
            "q": f"¿Es mejor renting o compra para el {nombre}?",
            "a": f"El renting del {nombre} desde {precio_min}€/mes te permite conducir un {cat} nuevo sin entrada y sin preocuparte de mantenimiento ni seguro. Si cambias de coche cada 3-4 años y no quieres asumir la depreciación, el renting suele ser más rentable que la compra."
        },
        {
            "q": f"¿Se puede contratar el renting del {nombre} como particular?",
            "a": f"Sí, el renting del {nombre} está disponible tanto para particulares como para autónomos y empresas. Las condiciones y precios pueden variar según el perfil — en la tabla puedes filtrar por tipo de cliente."
        },
    ]
    if eco:
        faqs.append({
            "q": f"¿El {nombre} tiene etiqueta ECO o CERO?",
            "a": f"Sí, el {nombre} está disponible en versiones con etiqueta ECO o CERO de la DGT, lo que te permite circular por zonas de bajas emisiones en Madrid, Barcelona y otras ciudades, y beneficiarte de descuentos en aparcamiento y peajes."
        })
    return faqs

def generar_eat_block(nombre, precio_min, make, model, fuels, gestoras):
    """Bloque E-A-T con H2/H3 semánticos para señales de autoridad en Google."""
    cat   = categoria_coche(make, model)
    eco   = es_electrico_o_hibrido(fuels)
    marca = make.title()
    g_txt = ' y '.join(gestoras[:2]) if gestoras else 'las principales gestoras'

    # Características específicas por categoría
    if cat == 'SUV':
        ventajas_cat = (f"El <strong>{nombre}</strong> destaca por su posición de conducción elevada, "
                        f"maletero de gran capacidad y tracción en todo tipo de terrenos. "
                        f"Su consumo optimizado y los sistemas de asistencia al conductor lo convierten en "
                        f"una de las opciones más demandadas en renting de SUV en España.")
    elif cat == 'furgoneta':
        ventajas_cat = (f"El <strong>{nombre}</strong> es la solución preferida por autónomos y pymes para "
                        f"gestionar su actividad profesional. Su capacidad de carga, versatilidad y "
                        f"bajo coste por kilómetro lo hacen ideal para distribución, servicios técnicos o logística.")
    else:
        ventajas_cat = (f"El <strong>{nombre}</strong> combina eficiencia de combustible, maletero funcional "
                        f"y tecnología de conectividad de última generación. Su diseño compacto lo hace "
                        f"especialmente apto para uso urbano e interurbano con bajos costes de mantenimiento.")

    etiqueta_txt = ""
    if eco:
        etiqueta_txt = (f"<p>Además, las versiones híbridas y eléctricas del {nombre} disponen de "
                        f"<strong>etiqueta ECO o CERO de la DGT</strong>, lo que permite circular sin "
                        f"restricciones por las Zonas de Bajas Emisiones de Madrid, Barcelona y otras "
                        f"ciudades, y acceder a ventajas en aparcamiento regulado.</p>")

    return f"""
    <div class="eat-section">

      <h2>¿Por qué elegir el {nombre} en modalidad de renting?</h2>
      <p>{ventajas_cat}</p>
      {etiqueta_txt}
      <p>Con el renting del {nombre} desde <strong>{precio_min}€/mes</strong> con {g_txt}, 
      conduces un vehículo nuevo sin entrada inicial, sin asumir la depreciación y sin 
      preocuparte por imprevistos mecánicos. Todo en una cuota mensual fija.</p>

      <h2>Condiciones del renting para el {nombre}</h2>
      <p>Todas las ofertas de renting del {nombre} incluyen:</p>
      <ul>
        <li><strong>Seguro a todo riesgo</strong> sin franquicia y sin distinción de conductor.</li>
        <li><strong>Mantenimiento preventivo y correctivo</strong> en talleres oficiales {marca}.</li>
        <li><strong>Asistencia en carretera 24 horas</strong> en toda España y Europa.</li>
        <li><strong>Gestión de ITV</strong> cuando corresponda por normativa.</li>
        <li><strong>Gestión administrativa de multas</strong> de tráfico.</li>
      </ul>
      <p>Al finalizar el contrato, simplemente devuelves el vehículo. Sin cuotas finales 
      ni obligación de compra.</p>

      <h3>Ventajas para particulares</h3>
      <p>El renting del {nombre} para particulares permite estrenar un coche nuevo sin 
      desembolso inicial, con cuota fija mensual que facilita la planificación del presupuesto 
      familiar. Ideal si cambias de coche cada 3-4 años o no quieres asumir la depreciación.</p>

      <h3>Ventajas para autónomos</h3>
      <p>Los autónomos pueden <strong>deducirse hasta el 50% del IVA</strong> de cada cuota 
      en uso mixto, y hasta el 100% si el uso es exclusivamente profesional. La cuota mensual 
      es gasto deducible en IRPF, lo que reduce la carga fiscal de forma directa.</p>

      <h3>Ventajas para empresas y pymes</h3>
      <p>Para empresas, el renting del {nombre} es un <strong>gasto operativo 100% deducible</strong> 
      en el Impuesto de Sociedades. No aparece en el balance como activo, mejora el ratio de 
      endeudamiento y permite renovar la flota con tecnología actual sin inmovilizar capital.</p>

    </div>"""


def generar_texto_seo(nombre, precio_min, precio_max, gestoras, fuels, make, model, n_ofertas):
    cat = categoria_coche(make, model)
    g_texto = ' y '.join(gestoras) if len(gestoras) <= 2 else ', '.join(gestoras[:-1]) + ' y ' + gestoras[-1]
    eco = es_electrico_o_hibrido(fuels)
    ahorro = precio_max - precio_min if precio_max > precio_min else 0
    fuels_texto = ', '.join(fuels)

    texto = f"""
    <h2>¿Cuánto cuesta el renting del {nombre} en 2026?</h2>
    <p>El <strong>renting del {nombre}</strong> parte desde <strong>{precio_min}€/mes</strong> según las ofertas actuales de {g_texto}. {'Dependiendo de la gestora, puedes ahorrarte hasta <strong>' + str(int(ahorro)) + '€ al mes</strong> — es decir, ' + str(int(ahorro * 12)) + '€ al año — por exactamente el mismo coche.' if ahorro > 5 else 'El precio varía según el plazo y los kilómetros anuales que elijas.'}</p>

    <h2>Comparativa: {g_texto}</h2>
    <p>En MiRenting hemos recopilado <strong>{n_ofertas} ofertas del {nombre}</strong> de {g_texto}. A diferencia de otros comparadores, aquí ves el precio real de cada gestora sin tener que rellenar formularios ni esperar llamadas. La tabla de arriba te muestra qué gestora tiene el {nombre} más barato ahora mismo.</p>

    <h2>Motorizaciones disponibles del {nombre}</h2>
    <p>El {nombre} está disponible en renting con las siguientes motorizaciones: <strong>{fuels_texto}</strong>. {'Las versiones híbridas y eléctricas tienen etiqueta ECO o CERO de la DGT, lo que te permite circular sin restricciones por las zonas de bajas emisiones.' if eco else 'Elige la motorización según tu uso diario y la normativa de emisiones de tu ciudad.'}</p>

    <h2>¿Qué incluye el renting del {nombre}?</h2>
    <p>Todas las ofertas de renting del {nombre} incluyen: <strong>seguro a todo riesgo</strong>, mantenimiento preventivo y correctivo en talleres oficiales, asistencia en carretera 24 horas, gestión de multas e ITV. Al final del contrato devuelves el coche sin pagar nada extra — sin cuota de compra ni sorpresas.</p>

    <h2>¿Para quién es el renting del {nombre}?</h2>
    <p>{'El ' + nombre + ' es un ' + cat + ' muy demandado en renting por autónomos y empresas que quieren deducir la cuota del IRPF y el IVA, y también por particulares que quieren conducir un coche nuevo sin asumir la depreciación. Con el renting cambias de coche al terminar el contrato sin pagar nada más.' if cat != 'furgoneta' else 'El ' + nombre + ' es uno de los vehículos comerciales más solicitados en renting por autónomos y empresas que necesitan controlar sus gastos de movilidad. La cuota mensual fija facilita la gestión contable y permite deducir el 100% del IVA.'}</p>
    """
    return texto

def generar_pagina(make, model, ofertas_modelo):
    nombre = f"{make.title()} {model.title()}"
    slug_name = slug(f"renting-{make}-{model}")

    precio_min = min((o.get('precio_desde') or 9999) for o in ofertas_modelo)
    precio_max = max((o.get('precio_desde') or 0) for o in ofertas_modelo)
    gestoras = sorted(set(o.get('fuente', '') for o in ofertas_modelo if o.get('fuente')))
    fuels = sorted(set(o.get('fuel', '') for o in ofertas_modelo if o.get('fuel')))
    imagen = next((o.get('image', '') for o in ofertas_modelo if o.get('image')), '')
    img_local = f"/img/modelos/{slug(make + '-' + model)}.png"

    g_corto = ' vs '.join(gestoras[:2]) if len(gestoras) >= 2 else gestoras[0] if gestoras else ''
    # ── Title optimizado para CTR ──────────────────────────────────────────
    title = f"Renting {nombre} desde {precio_min}€/mes | Ofertas 2026 — MiRenting"
    # ── Meta-description con call-to-action ───────────────────────────────
    description = (
        f"Compara {len(ofertas_modelo)} ofertas de renting para el {nombre}. "
        f"Precio desde {precio_min}€/mes con seguro, mantenimiento e ITV incluidos. "
        f"Sin entrada. Arval, Ayvens y más. ¡Calcula tu cuota ahora!"
    )

    ofertas_sorted = sorted(ofertas_modelo, key=lambda x: x.get('precio_desde', 9999))

    # Recopilar valores únicos para los selects de filtros
    plazos_unicos  = sorted(set(str(o['precios'][0][0]) for o in ofertas_sorted if o.get('precios') and len(o['precios']) > 0))
    fuels_unicos   = sorted(set(o.get('fuel','') for o in ofertas_sorted if o.get('fuel') and o.get('fuel') != '—'))
    tipos_unicos   = sorted(set(o.get('tipo','') for o in ofertas_sorted if o.get('tipo') and o.get('tipo') != '—'))
    fuentes_unicas = sorted(set(o.get('fuente','') for o in ofertas_sorted if o.get('fuente') and o.get('fuente') != '—'))

    opts_plazo   = '<option value="">Cualquier plazo</option>'  + ''.join(f'<option value="{p}">{p} meses</option>' for p in plazos_unicos)
    opts_fuel    = '<option value="">Cualquier combustible</option>' + ''.join(f'<option value="{f.lower()}">{f}</option>' for f in fuels_unicos)
    opts_tipo    = '<option value="">Empresa y particular</option>' + ''.join(f'<option value="{t.lower()}">{t.title()}</option>' for t in tipos_unicos)
    opts_fuente  = '<option value="">Todas las gestoras</option>' + ''.join(f'<option value="{f.lower().replace(" ","-")}">{f}</option>' for f in fuentes_unicas)

    filas = ""
    for i, o in enumerate(ofertas_sorted):
        precio = o.get('precio_desde', 0)
        fuente = o.get('fuente', '—')
        tipo = o.get('tipo', '—')
        fuel = o.get('fuel', '—')
        version = (o.get('version') or '—')[:55]
        link = o.get('link_oferta', '#')
        dgt = etiqueta_dgt(fuel)
        duracion = km = '—'
        plazo_val = ''
        if o.get('precios') and len(o['precios']) > 0:
            duracion = f"{o['precios'][0][0]} meses"
            plazo_val = str(o['precios'][0][0])
            km = f"{int(o['precios'][0][1]):,} km/año".replace(',', '.')
        es_mejor = i == 0
        fuente_data = fuente.lower().replace(' ', '-')
        tipo_data   = tipo.lower()
        fuel_data   = fuel.lower()
        filas += f"""
        <tr class="{'best-row' if es_mejor else ''}" data-fuente="{fuente_data}" data-tipo="{tipo_data}" data-fuel="{fuel_data}" data-plazo="{plazo_val}">
          <td class="rank-cell">{'<span class="rank-star">★</span>' if es_mejor else f'<span class="rank-num">{i+1}</span>'}</td>
          <td data-label="Gestora"><strong>{fuente}</strong></td>
          <td data-label="Cliente"><span class="tipo-badge">{tipo}</span></td>
          <td data-label="Combustible">{fuel} {dgt}</td>
          <td data-label="Plazo">{duracion}</td>
          <td data-label="Km/año">{km}</td>
          <td class="version-cell" data-label="Versión">{version}</td>
          <td data-label="Precio">{'<span class="best-badge">✓ Mejor precio</span><br>' if es_mejor else ''}<span class="price-strong">{precio} €/mes</span></td>
          <td><a href="{link}" target="_blank" rel="noopener" class="btn-ver">Ver oferta →</a></td>
        </tr>"""

    faqs = generar_faq(nombre, precio_min, gestoras, fuels, make, model)
    faq_html = ""
    for faq in faqs:
        faq_html += f"""
        <div class="faq-item">
          <button class="faq-q" onclick="this.parentElement.classList.toggle('open')">{faq['q']} <span class="faq-arrow">▾</span></button>
          <div class="faq-a"><p>{faq['a']}</p></div>
        </div>"""

    faq_schema = json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":f["q"],"acceptedAnswer":{"@type":"Answer","text":f["a"]}} for f in faqs]}, ensure_ascii=False)
    breadcrumb_schema = json.dumps({
        "@context":"https://schema.org","@type":"BreadcrumbList",
        "itemListElement":[
            {"@type":"ListItem","position":1,"name":"MiRenting","item":"https://www.myrenting.es/"},
            {"@type":"ListItem","position":2,"name":"Comparador de renting","item":"https://www.myrenting.es/"},
            {"@type":"ListItem","position":3,"name":f"Renting {nombre}","item":f"https://www.myrenting.es/{slug_name}.html"}
        ]
    }, ensure_ascii=False)
    product_schema = json.dumps({
        "@context":"https://schema.org",
        "@type":"Product",
        "name": f"Renting {nombre}",
        "description": description,
        "brand": {"@type":"Brand","name": make.title()},
        "model": model.title(),
        "offers": {
            "@type":"AggregateOffer",
            "lowPrice": str(precio_min),
            "highPrice": str(precio_max),
            "priceCurrency": "EUR",
            "offerCount": str(len(ofertas_modelo)),
            "availability": "https://schema.org/InStock",
            "seller": {"@type":"Organization","name":"MiRenting","url":"https://www.myrenting.es"}
        }
    }, ensure_ascii=False)

    texto_seo = generar_texto_seo(nombre, precio_min, precio_max, gestoras, fuels, make, model, len(ofertas_modelo))
    eat_block = generar_eat_block(nombre, precio_min, make, model, fuels, gestoras)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','GTM-NHXGQF97');</script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://www.myrenting.es/{slug_name}.html">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="https://www.myrenting.es/{slug_name}.html">
  <meta property="og:type" content="website">
  {'<meta property="og:image" content="' + imagen + '">' if imagen else ''}
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <script type="application/ld+json">{product_schema}</script>
  <script type="application/ld+json">{faq_schema}</script>
  <script type="application/ld+json">{breadcrumb_schema}</script>
  <style>
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    :root{{--accent:#e8380d;--ink:#111318;--ink-2:#2d2d3a;--ink-3:#6b6b80;--ink-4:#a0a0b0;--green:#00c47a;--green-lt:#e0faf1;--surface:#fff;--surface-2:#f7f8fa;--surface-3:#eeeff4;--border:#e4e4ec;--radius:14px;--radius-sm:8px}}
    body{{font-family:'Plus Jakarta Sans',sans-serif;background:var(--surface-2);color:var(--ink);line-height:1.6;-webkit-font-smoothing:antialiased}}
    nav{{background:rgba(255,255,255,.95);backdrop-filter:blur(16px);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:200}}
    .nav-inner{{max-width:1280px;margin:0 auto;padding:0 28px;height:62px;display:flex;align-items:center;justify-content:space-between}}
    .logo{{font-size:1.25rem;font-weight:800;color:var(--ink);text-decoration:none}}
    .logo-dot{{width:8px;height:8px;background:var(--accent);border-radius:50%;display:inline-block;margin-left:3px;margin-bottom:10px}}
    .nav-back{{color:var(--ink-3);text-decoration:none;font-size:.875rem;font-weight:500}}
    .nav-back:hover{{color:var(--ink)}}
    .hero-model{{background:#111318;color:#fff;padding:48px 28px}}
    .hero-inner{{max-width:1280px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:center}}
    .breadcrumb{{font-size:.78rem;color:rgba(255,255,255,.4);margin-bottom:12px}}
    .breadcrumb a{{color:rgba(255,255,255,.4);text-decoration:none}}
    .hero-model h1{{font-size:clamp(1.8rem,4vw,2.6rem);font-weight:800;letter-spacing:-1px;line-height:1.15;margin-bottom:8px}}
    .hero-model h1 em{{font-style:normal;color:var(--accent)}}
    .hero-sub{{color:rgba(255,255,255,.55);margin-top:8px;font-size:.95rem}}
    .hero-stats{{display:flex;gap:16px;margin-top:20px;flex-wrap:wrap}}
    .hero-stat{{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);border-radius:var(--radius-sm);padding:12px 16px}}
    .hero-stat-label{{font-size:.68rem;font-weight:700;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:.5px}}
    .hero-stat-value{{font-size:1.2rem;font-weight:800;color:#fff;margin-top:2px}}
    .hero-img{{border-radius:var(--radius);overflow:hidden;max-height:260px;background:rgba(255,255,255,.05)}}
    .hero-img img{{width:100%;height:100%;object-fit:cover}}
    main{{max-width:1280px;margin:40px auto;padding:0 28px}}
    .section-title{{font-size:1.2rem;font-weight:800;margin-bottom:16px;letter-spacing:-.3px}}
    .comp-panel{{background:var(--surface);border-radius:var(--radius);border:1px solid var(--border);overflow:hidden;margin-bottom:32px}}
    .comp-table-wrap{{overflow-x:auto}}
    .comp-table{{width:100%;border-collapse:collapse}}
    .comp-table thead th{{background:var(--surface-2);padding:10px 16px;text-align:left;font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:var(--ink-4);border-bottom:2px solid var(--border);white-space:nowrap}}
    .comp-table tbody tr{{border-bottom:1px solid var(--border);transition:background .1s}}
    .comp-table tbody tr:hover{{background:var(--surface-2)}}
    .comp-table tbody tr.best-row{{background:var(--green-lt)}}
    .comp-table tbody td{{padding:12px 16px;font-size:.875rem;color:var(--ink-2);vertical-align:middle}}
    .rank-num{{width:28px;height:28px;background:var(--surface-3);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:.78rem;font-weight:700;color:var(--ink-3)}}
    .rank-star{{width:28px;height:28px;background:var(--green);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:.82rem;color:#fff}}
    .best-badge{{display:inline-flex;align-items:center;background:var(--green);color:#fff;font-size:.65rem;font-weight:700;padding:2px 8px;border-radius:99px;margin-bottom:4px}}
    .price-strong{{font-size:1rem;font-weight:800;color:var(--ink)}}
    .best-row .price-strong{{color:#00875a}}
    .version-cell{{max-width:180px;font-size:.78rem;color:var(--ink-3)}}
    .tipo-badge{{font-size:.68rem;font-weight:600;padding:2px 7px;border-radius:99px;background:var(--surface-3);color:var(--ink-3);border:1px solid var(--border);text-transform:uppercase}}
    .btn-ver{{background:var(--ink);color:#fff;text-decoration:none;padding:7px 14px;border-radius:var(--radius-sm);font-size:.78rem;font-weight:700;white-space:nowrap;transition:background .15s}}
    .btn-ver:hover{{background:var(--accent)}}
    .seo-section{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:32px;margin-bottom:32px}}
    .seo-section h2{{font-size:1.1rem;font-weight:800;margin-bottom:10px;margin-top:24px;color:var(--ink)}}
    .seo-section h2:first-child{{margin-top:0}}
    .seo-section p{{color:var(--ink-3);margin-bottom:12px;line-height:1.75;font-size:.95rem}}
    .faq-section{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:32px;margin-bottom:32px}}
    .faq-section h2{{font-size:1.1rem;font-weight:800;margin-bottom:20px}}
    .faq-item{{border-bottom:1px solid var(--border);overflow:hidden}}
    .faq-item:last-child{{border-bottom:none}}
    .faq-q{{width:100%;background:none;border:none;text-align:left;padding:16px 0;font-size:.95rem;font-weight:600;color:var(--ink);cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:12px;font-family:inherit}}
    .faq-arrow{{transition:transform .2s;font-size:.8rem;color:var(--ink-4);flex-shrink:0}}
    .faq-item.open .faq-arrow{{transform:rotate(180deg)}}
    .faq-a{{max-height:0;overflow:hidden;transition:max-height .3s ease}}
    .faq-item.open .faq-a{{max-height:300px}}
    .faq-a p{{color:var(--ink-3);padding-bottom:16px;line-height:1.7;font-size:.9rem}}
    .cta-section{{background:#111318;color:#fff;border-radius:var(--radius);padding:40px;text-align:center;margin-bottom:40px}}
    .cta-section h2{{font-size:1.3rem;font-weight:800;margin-bottom:8px}}
    .cta-section p{{color:rgba(255,255,255,.5);margin-bottom:20px}}
    .btn-cta{{background:var(--accent);color:#fff;text-decoration:none;padding:14px 28px;border-radius:var(--radius-sm);font-size:.95rem;font-weight:700;display:inline-block;transition:background .15s}}
    .btn-cta:hover{{background:#c42e0a}}
    /* ── E-A-T section ── */
    .eat-section{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:32px;margin-bottom:32px}}
    .eat-section h2{{font-size:1.15rem;font-weight:800;margin:28px 0 10px;color:var(--ink);letter-spacing:-.2px}}
    .eat-section h2:first-child{{margin-top:0}}
    .eat-section h3{{font-size:1rem;font-weight:700;margin:20px 0 7px;color:var(--ink);padding-left:12px;border-left:3px solid var(--accent)}}
    .eat-section p{{color:var(--ink-3);margin-bottom:12px;line-height:1.75;font-size:.95rem}}
    .eat-section ul{{padding-left:1.3rem;margin-bottom:12px}}
    .eat-section li{{color:var(--ink-3);margin-bottom:5px;line-height:1.6;font-size:.92rem}}
    .eat-section strong{{color:var(--ink)}}
    /* ── Precio destacado en tabla ── */
    .price-strong{{font-size:1.05rem;font-weight:800;color:var(--ink)}}
    .best-row .price-strong{{color:#00875a;font-size:1.15rem}}
    .price-pill{{display:inline-block;background:var(--accent-lt,#fdecea);color:var(--accent);
                 font-size:.72rem;font-weight:700;padding:2px 7px;border-radius:99px;margin-left:4px;vertical-align:middle}}
    /* ── Botón flotante móvil ── */
    .mobile-float{{
      display:none;position:fixed;bottom:20px;left:50%;transform:translateX(-50%);
      background:var(--accent);color:#fff;border:none;border-radius:99px;
      padding:14px 28px;font-size:.95rem;font-weight:700;font-family:inherit;
      box-shadow:0 4px 20px rgba(232,56,13,.4);cursor:pointer;z-index:300;
      white-space:nowrap;transition:background .15s,transform .15s;
    }}
    .mobile-float:hover{{background:var(--accent-2);transform:translateX(-50%) scale(1.03)}}
    @media(max-width:768px){{.mobile-float{{display:block}}}}
    .filter-bar{{background:var(--surface-2);border-bottom:1px solid var(--border);padding:14px 20px}}
    .filter-bar-inner{{display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
    .filter-group-inline{{display:flex;flex-direction:column;gap:3px;min-width:130px}}
    .filter-group-inline label{{font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--ink-4)}}
    .filter-group-inline select{{padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-size:.8rem;font-family:inherit;color:var(--ink);background:var(--surface);cursor:pointer;transition:border-color .15s;appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%23a0a0b0'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 8px center;padding-right:24px}}
    .filter-group-inline select:focus{{outline:none;border-color:var(--accent)}}
    .filter-group-inline select.active{{border-color:var(--accent);background-color:var(--accent-lt,#fdecea)}}
    .filter-results-wrap{{display:flex;align-items:center;gap:8px;margin-left:auto}}
    .filter-count{{font-size:.78rem;color:var(--ink-4);white-space:nowrap}}
    .filter-reset{{background:none;border:1.5px solid var(--border-2,#d0d0dc);border-radius:99px;padding:5px 12px;font-size:.75rem;font-weight:600;color:var(--ink-3);cursor:pointer;transition:all .15s;font-family:inherit}}
    .filter-reset:hover{{border-color:var(--accent);color:var(--accent)}}
    .no-results-filter{{padding:32px;text-align:center;color:var(--ink-4);font-size:.9rem}}
    .link-btn{{background:none;border:none;color:var(--accent);cursor:pointer;font-size:.9rem;font-weight:600;font-family:inherit;text-decoration:underline}}
    .comp-table tbody tr.hidden-row{{display:none}}
    @media(max-width:768px){{
      .hero-model{{padding:32px 16px}}
      .hero-inner{{grid-template-columns:1fr;gap:20px}}
      .hero-img{{display:none}}
      .hero-stats{{gap:8px}}
      .hero-stat{{padding:10px 12px;flex:1;min-width:calc(50% - 4px)}}
      main{{padding:0 16px;margin:20px auto}}
      .section-title{{font-size:1rem}}
      .seo-section,.faq-section{{padding:20px 16px}}
      .cta-section{{padding:28px 16px}}
      .filter-bar-inner{{gap:8px}}
      .filter-group-inline{{min-width:calc(50% - 4px)}}
      .filter-results-wrap{{width:100%;margin-left:0}}
    }}
    @media(max-width:640px){{
      .comp-table-wrap{{overflow-x:unset}}
      .comp-table thead{{display:none}}
      .comp-table tbody tr{{
        display:block;
        border-bottom:none;
        margin-bottom:10px;
        border-radius:var(--radius-sm);
        border:1px solid var(--border);
        padding:14px 16px;
        background:var(--surface);
        position:relative;
      }}
      .comp-table tbody tr.best-row{{border-color:var(--green);border-width:2px}}
      .comp-table tbody tr.hidden-row{{display:none}}
      .comp-table tbody td{{
        display:flex;
        justify-content:space-between;
        align-items:center;
        padding:5px 0;
        font-size:.85rem;
        border:none;
      }}
      .comp-table tbody td::before{{
        content:attr(data-label);
        font-size:.68rem;
        font-weight:700;
        text-transform:uppercase;
        letter-spacing:.4px;
        color:var(--ink-4);
        flex-shrink:0;
        margin-right:8px;
      }}
      .comp-table tbody td:first-child{{
        position:absolute;top:14px;left:16px;padding:0;width:auto;
      }}
      .comp-table tbody td:first-child::before{{display:none}}
      .comp-table tbody td:nth-child(2){{
        font-size:1rem;font-weight:800;padding-top:0;
        padding-left:36px;padding-bottom:10px;
        border-bottom:1px solid var(--border);margin-bottom:6px;
      }}
      .comp-table tbody td:nth-child(2)::before{{display:none}}
      .comp-table tbody td:nth-child(3){{display:none}}
      .comp-table tbody td:nth-child(7){{display:none}}
      .comp-table tbody td:last-child{{
        padding-top:10px;border-top:1px solid var(--border);
        margin-top:6px;justify-content:flex-end;
      }}
      .comp-table tbody td:last-child::before{{display:none}}
      .btn-ver{{width:100%;text-align:center;padding:10px;font-size:.85rem}}
      .price-strong{{font-size:1.1rem}}
      .best-badge{{font-size:.68rem}}
      .version-cell{{max-width:none;font-size:.8rem}}
    }}
    </style>
<script>
  function filtrarTabla() {{
    const plazo  = document.getElementById('f-plazo').value;
    const fuel   = document.getElementById('f-fuel').value;
    const tipo   = document.getElementById('f-tipo').value;
    const fuente = document.getElementById('f-fuente').value;

    const hayFiltro = plazo || fuel || tipo || fuente;
    document.getElementById('btn-reset').style.display = hayFiltro ? 'inline-block' : 'none';

    ['f-plazo','f-fuel','f-tipo','f-fuente'].forEach(id => {{
      const el = document.getElementById(id);
      el.classList.toggle('active', el.value !== '');
    }});

    const filas = document.querySelectorAll('#comp-tbody tr');
    let visibles = 0;

    filas.forEach(tr => {{
      const match =
        (!plazo  || tr.dataset.plazo  === plazo)  &&
        (!fuel   || tr.dataset.fuel.includes(fuel)) &&
        (!tipo   || tr.dataset.tipo   === tipo)   &&
        (!fuente || tr.dataset.fuente === fuente);

      tr.classList.toggle('hidden-row', !match);
      if (match) visibles++;
    }});

    // Renumerar filas visibles
    let num = 1;
    filas.forEach(tr => {{
      if (!tr.classList.contains('hidden-row')) {{
        const cell = tr.querySelector('.rank-cell');
        if (cell && !tr.classList.contains('best-row')) {{
          cell.innerHTML = `<span class="rank-num">${{num}}</span>`;
        }}
        num++;
      }}
    }});

    const total = filas.length;
    const countEl = document.getElementById('filter-count');
    countEl.textContent = hayFiltro ? `${{visibles}} de ${{total}} ofertas` : `${{total}} ofertas`;

    document.getElementById('no-results-msg').style.display = visibles === 0 ? 'block' : 'none';
  }}

  function resetFiltros() {{
    ['f-plazo','f-fuel','f-tipo','f-fuente'].forEach(id => {{
      document.getElementById(id).value = '';
      document.getElementById(id).classList.remove('active');
    }});
    filtrarTabla();
  }}

  // Inicializar contador al cargar
  window.addEventListener('DOMContentLoaded', () => {{
    const total = document.querySelectorAll('#comp-tbody tr').length;
    document.getElementById('filter-count').textContent = `${{total}} ofertas`;
  }});
</script>
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
  <div class="hero-inner">
    <div>
      <div class="breadcrumb"><a href="/">MiRenting</a> › <a href="/">Ofertas</a> › {nombre}</div>
      <h1>Renting <em>{nombre}</em> — ¿Cuál es el más barato?</h1>
      <p class="hero-sub">Comparamos {len(ofertas_modelo)} ofertas de {', '.join(gestoras)}. Precio real, sin formularios ni registros.</p>
      <div class="hero-stats">
        <div class="hero-stat"><div class="hero-stat-label">Precio desde</div><div class="hero-stat-value">{precio_min} €/mes</div></div>
        <div class="hero-stat"><div class="hero-stat-label">Ofertas</div><div class="hero-stat-value">{len(ofertas_modelo)}</div></div>
        <div class="hero-stat"><div class="hero-stat-label">Gestoras</div><div class="hero-stat-value">{len(gestoras)}</div></div>
        {f'<div class="hero-stat"><div class="hero-stat-label">Ahorro máximo</div><div class="hero-stat-value">{int(precio_max - precio_min)} €/mes</div></div>' if precio_max - precio_min > 5 else ''}
      </div>
    </div>
    <div class="hero-img">
      <img src="{img_local}" alt="Renting {nombre}" loading="eager" onerror="this.src='{imagen}';this.onerror=null;">
    </div>
  </div>
</section>
<main>
  <h2 class="section-title">Comparativa de precios — Renting {nombre} 2026</h2>
  <div class="comp-panel">
    <div class="filter-bar">
      <div class="filter-bar-inner">
        <div class="filter-group-inline">
          <label>Plazo</label>
          <select id="f-plazo" onchange="filtrarTabla()">{opts_plazo}</select>
        </div>
        <div class="filter-group-inline">
          <label>Combustible</label>
          <select id="f-fuel" onchange="filtrarTabla()">{opts_fuel}</select>
        </div>
        <div class="filter-group-inline">
          <label>Cliente</label>
          <select id="f-tipo" onchange="filtrarTabla()">{opts_tipo}</select>
        </div>
        <div class="filter-group-inline">
          <label>Gestora</label>
          <select id="f-fuente" onchange="filtrarTabla()">{opts_fuente}</select>
        </div>
        <div class="filter-results-wrap">
          <span id="filter-count" class="filter-count"></span>
          <button class="filter-reset" onclick="resetFiltros()" id="btn-reset" style="display:none">✕ Limpiar</button>
        </div>
      </div>
    </div>
    <div class="comp-table-wrap">
      <table class="comp-table" id="comp-table">
        <thead><tr><th>#</th><th>Gestora</th><th>Cliente</th><th>Combustible</th><th>Plazo</th><th>Km/año</th><th>Versión</th><th>Precio/mes</th><th></th></tr></thead>
        <tbody id="comp-tbody">{filas}</tbody>
      </table>
      <div id="no-results-msg" class="no-results-filter" style="display:none">
        <p>No hay ofertas con esos filtros. <button onclick="resetFiltros()" class="link-btn">Limpiar filtros →</button></p>
      </div>
    </div>
  </div>
  <div class="seo-section">{texto_seo}</div>
  {eat_block}
  <div class="faq-section">
    <h2>Preguntas frecuentes sobre el renting del {nombre}</h2>
    {faq_html}
  </div>
  <div class="cta-section">
    <h2>¿Buscas más modelos?</h2>
    <p>Compara más de 900 ofertas de renting de todas las gestoras sin registrarte</p>
    <a href="/" class="btn-cta">Ver todas las ofertas →</a>
  </div>
</main>
<footer>
  <p>© 2026 MiRenting · <a href="/">Comparador de renting de coches en España</a> · Precios orientativos sujetos a disponibilidad de cada gestora.</p>
  <p style="margin-top:8px"><a href="/aviso-legal.html">Aviso Legal</a> · <a href="/politica-privacidad.html">Privacidad</a> · <a href="/politica-cookies.html">Cookies</a></p>
</footer>

<button class="mobile-float" onclick="document.getElementById('comp-table').scrollIntoView({{behavior:'smooth'}})">
  📋 Ver todas las ofertas
</button>
</body>
</html>"""
    return slug_name, html

def main():
    html = HTML_PATH.read_text(encoding="utf-8")
    start = html.find("const _OFERTAS = [") + len("const _OFERTAS = ")
    end = html.find("];", start) + 1
    ofertas = json.loads(html[start:end])
    print(f"Ofertas leídas: {len(ofertas)}")

    modelos = {}
    for o in ofertas:
        make  = (o.get("make") or "").strip().upper()
        model = (o.get("model") or "").strip().upper()
        if not make or not model: continue
        key = f"{make}||{model}"
        if key not in modelos: modelos[key] = []
        modelos[key].append(o)

    print(f"Modelos: {len(modelos)}")

    paginas = []
    for key, ofertas_modelo in modelos.items():
        make, model = key.split("||")
        slug_name, html_pagina = generar_pagina(make, model, ofertas_modelo)
        path = BASE / f"{slug_name}.html"
        path.write_text(html_pagina, encoding="utf-8")
        paginas.append((slug_name, len(ofertas_modelo)))

    paginas.sort(key=lambda x: x[1], reverse=True)
    print(f"\n✓ {len(paginas)} páginas generadas")
    for s, n in paginas[:10]:
        print(f"  {s}.html ({n} ofertas)")

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += '  <url><loc>https://www.myrenting.es/</loc><priority>1.0</priority></url>\n'
    for s, _ in paginas:
        sitemap += f'  <url><loc>https://www.myrenting.es/{s}.html</loc><priority>0.8</priority></url>\n'
    sitemap += '</urlset>'
    (BASE / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print(f"✓ sitemap.xml con {len(paginas)+1} URLs")

if __name__ == "__main__":
    main()
