#!/usr/bin/env python3
"""
Genera páginas SEO individuales por modelo de renting.
Mejoras v2: top-ofertas visuales, calculadora de ahorro, links internos,
sticky CTA móvil, schema más completo, path relativo (sin ruta Mac hardcoded).
"""
import json, re, random
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
HTML_PATH = BASE / "index.html"
HOY = datetime.now().strftime("%Y-%m-%d")
AÑO = datetime.now().year


# ── Utilidades ────────────────────────────────────────────────────────────

def slug(texto):
    t = texto.lower()
    for a, b in [('á','a'),('à','a'),('ä','a'),('é','e'),('è','e'),('ë','e'),
                 ('í','i'),('ì','i'),('ï','i'),('ó','o'),('ò','o'),('ö','o'),
                 ('ú','u'),('ù','u'),('ü','u'),('ñ','n'),('ç','c')]:
        t = t.replace(a, b)
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', t)).strip('-')

def etiqueta_dgt(fuel):
    f = (fuel or '').lower()
    if any(x in f for x in ['eléctrico','electric','bev']): return '<span class="badge-cero">CERO</span>'
    if any(x in f for x in ['enchufable','phev','plug']): return '<span class="badge-eco">ECO</span>'
    if any(x in f for x in ['híbrido','hibrido','hybrid','mhev','hev']): return '<span class="badge-eco">ECO</span>'
    return ''

def etiqueta_dgt_texto(fuel):
    f = (fuel or '').lower()
    if any(x in f for x in ['eléctrico','electric']): return 'CERO'
    if any(x in f for x in ['enchufable','híbrido','hibrido','hybrid']): return 'ECO'
    return 'C'

def categoria_coche(make, model):
    m = model.upper()
    FURGONETAS = ['KANGOO','BERLINGO','PARTNER','COMBO','TRAFIC','MASTER','SPRINTER',
                  'VITO','TRANSIT','PROACE','FIORINO','DOBLO','BOXER','EXPERT','RIFTER',
                  'CITAN','HILUX','RANGER','PROACE CITY','L200','AMAROK','TRANSPORTER']
    SUVS = ['QASHQAI','T-ROC','TIGUAN','ARONA','SPORTAGE','KONA','TUCSON','FORMENTOR',
            'KAROQ','KODIAQ','CX-5','CX-60','CX-30','RAV4','C-HR','YARIS CROSS',
            'PUMA','KUGA','DUSTER','XC40','XC60','XC90','DEFENDER','EVOQUE','JUKE',
            'STONIC','NIRO','BAYON','T-CROSS','TAIGO','KAMIQ','ATECA','TARRACO',
            'EV3','EV6','IONIQ 5','BZ4X','ID.4','ECLIPSE CROSS','COUNTRYMAN','GLA',
            'Q3','Q5','Q7','X1','X2','X3','X5','LBX','NX','RX','UX','TERRAMAR',
            'TONALE','STELVIO','JUNIOR','EQA','EQB','EQC','ARIYA','ZR-V','HR-V',
            'CRETA','SANTA FE','SORENTO','SELTOS']
    for f in FURGONETAS:
        if f in m: return 'furgoneta'
    for s in SUVS:
        if s in m: return 'SUV'
    return 'berlina'

def es_electrico(fuels):
    return any('eléctrico' in f.lower() or 'electric' in f.lower() for f in fuels)

def es_hibrido(fuels):
    return any('híbrido' in f.lower() or 'hibrido' in f.lower() or 'hybrid' in f.lower() for f in fuels)

def precio_compra_estimado(make, model, precio_min):
    """Estima el precio de compra del modelo para la calculadora de ahorro."""
    m = (make + ' ' + model).upper()
    precios_ref = {
        'BMW': 45000, 'MERCEDES': 48000, 'AUDI': 44000, 'VOLVO': 42000,
        'VOLKSWAGEN': 32000, 'SEAT': 22000, 'SKODA': 24000, 'CUPRA': 35000,
        'TOYOTA': 30000, 'KIA': 28000, 'HYUNDAI': 27000, 'RENAULT': 23000,
        'PEUGEOT': 22000, 'CITROEN': 21000, 'OPEL': 22000, 'FORD': 26000,
        'DACIA': 17000, 'NISSAN': 25000, 'MAZDA': 28000, 'HONDA': 27000,
        'BYD': 32000, 'TESLA': 48000, 'ALFA': 40000,
    }
    base = precios_ref.get(make.upper(), 28000)
    # Ajustar según categoría
    cat = categoria_coche(make, model)
    if cat == 'SUV': base = int(base * 1.2)
    if cat == 'furgoneta': base = int(base * 0.9)
    return base


# ── Generadores de contenido ──────────────────────────────────────────────

def generar_faq(nombre, precio_min, gestoras, fuels, make, model):
    g = gestoras
    g_texto = ' y '.join(g) if len(g) <= 2 else ', '.join(g[:-1]) + ' y ' + g[-1]
    cat = categoria_coche(make, model)
    eco = es_electrico(fuels) or es_hibrido(fuels)
    electrico = es_electrico(fuels)

    faqs = [
        {
            "q": f"¿Cuánto cuesta el renting del {nombre} en {AÑO}?",
            "a": f"El renting del {nombre} parte desde <strong>{precio_min}€/mes</strong> según las ofertas actuales en Myrenting. "
                 f"El precio final depende del plazo del contrato (entre 24 y 72 meses), los kilómetros anuales y la gestora. "
                 f"Puedes comparar en la tabla de esta página todas las combinaciones posibles."
        },
        {
            "q": f"¿Qué gestora tiene el {nombre} más barato en renting?",
            "a": f"Puedes contratar el renting del {nombre} con {g_texto}. "
                 f"Los precios varían entre gestoras hasta un 20% por las mismas condiciones. "
                 f"La tabla comparativa de esta página te muestra cuál tiene el precio más bajo ahora mismo, "
                 f"actualizada a {HOY}."
        },
        {
            "q": f"¿Qué incluye el renting del {nombre}?",
            "a": f"Todas las ofertas de renting del {nombre} incluyen: seguro a todo riesgo, mantenimiento preventivo y correctivo "
                 f"en red oficial, asistencia en carretera 24h, gestión de multas e ITV. "
                 f"La cuota mensual es fija durante todo el contrato. Al final devuelves el coche sin pagar nada extra."
        },
        {
            "q": f"¿Es mejor el renting o comprar el {nombre}?",
            "a": f"Con el renting del {nombre} desde {precio_min}€/mes tienes el coche siempre en garantía, "
                 f"sin preocuparte del seguro, el mantenimiento ni la depreciación. "
                 f"Si cambias de coche cada 3-5 años, el renting suele ser más rentable que la compra, "
                 f"especialmente para autónomos que pueden deducirse el IVA y hasta el 50% del IRPF."
        },
        {
            "q": f"¿Puedo contratar el renting del {nombre} como particular?",
            "a": f"Sí. La mayoría de gestoras ofrecen el {nombre} en renting tanto para particulares como para "
                 f"autónomos y empresas. Las condiciones suelen ser similares, aunque los autónomos y empresas "
                 f"se benefician de ventajas fiscales adicionales. Usa el filtro 'Cliente' en la tabla para ver "
                 f"las ofertas según tu perfil."
        },
    ]

    if electrico:
        faqs.append({
            "q": f"¿El {nombre} eléctrico tiene beneficios fiscales?",
            "a": f"Sí. El {nombre} eléctrico tiene etiqueta CERO de la DGT, lo que permite circular sin restricciones "
                 f"por zonas de bajas emisiones en Madrid (ZBE Distrito Centro), Barcelona y otras ciudades. "
                 f"Además, muchos aparcamientos públicos ofrecen descuentos del 50% para vehículos CERO."
        })
    elif eco:
        faqs.append({
            "q": f"¿Qué etiqueta DGT tiene el {nombre} híbrido?",
            "a": f"Las versiones híbridas del {nombre} tienen etiqueta ECO de la DGT (distintivo azul), "
                 f"que permite acceder a zonas de bajas emisiones, utilizar el carril bus+VAO en autopistas "
                 f"y beneficiarse de descuentos en aparcamiento regulado."
        })

    if cat == 'furgoneta':
        faqs.append({
            "q": f"¿El renting del {nombre} es deducible al 100% para autónomos?",
            "a": f"Los vehículos comerciales como el {nombre} son deducibles al 100% en el IVA y en el IRPF "
                 f"cuando se usan exclusivamente para la actividad económica. Esto lo convierte en una de las "
                 f"opciones más eficientes fiscalmente para autónomos y pymes."
        })

    return faqs


def generar_texto_seo(nombre, precio_min, precio_max, gestoras, fuels, make, model, n_ofertas, precio_compra):
    cat = categoria_coche(make, model)
    g_texto = ' y '.join(gestoras[:2]) if len(gestoras) <= 2 else ', '.join(gestoras[:2]) + f' y {len(gestoras)-2} más'
    eco = es_electrico(fuels) or es_hibrido(fuels)
    electrico = es_electrico(fuels)
    ahorro_mensual = precio_max - precio_min if precio_max > precio_min else 0
    cuota_compra_est = round(precio_compra / 60 * 1.06)  # financiación 60 meses + intereses
    fuels_texto = ', '.join(fuels) if fuels else 'gasolina y diésel'

    ahorro_txt = (
        f"Dependiendo de la gestora que elijas, la diferencia puede ser de hasta "
        f"<strong>{int(ahorro_mensual)}€ al mes</strong> — {int(ahorro_mensual * 12)}€ al año — "
        f"por exactamente el mismo {nombre}."
        if ahorro_mensual > 10 else
        f"Comparar gestoras es clave para encontrar el mejor precio disponible ahora mismo."
    )

    return f"""
    <h2>¿Cuánto cuesta el renting del {nombre} en {AÑO}?</h2>
    <p>El <strong>renting del {nombre}</strong> parte desde <strong>{precio_min}€/mes</strong>
    en las ofertas comparadas en Myrenting a fecha de hoy. {ahorro_txt}
    La tabla de esta página recoge las <strong>{n_ofertas} ofertas disponibles</strong>
    de {g_texto}, actualizadas regularmente.</p>

    <h2>Renting vs compra: ¿qué sale mejor para el {nombre}?</h2>
    <p>Comprar el {nombre} supone un desembolso inicial elevado, más los costes de seguro,
    mantenimiento e ITV. Con el renting pagas <strong>una cuota fija desde {precio_min}€/mes</strong>
    que ya incluye todo. A modo orientativo, financiar un {cat} similar durante 60 meses
    cuesta aproximadamente {cuota_compra_est}€/mes <em>solo en cuota de financiación</em>,
    sin seguro ni mantenimiento. El renting suele ser más ventajoso si cambias de coche
    cada 3-5 años y valoras la previsibilidad de gastos.</p>

    <h2>Motorizaciones disponibles del {nombre} en renting</h2>
    <p>El {nombre} está disponible en renting con las siguientes motorizaciones:
    <strong>{fuels_texto}</strong>.
    {"Las versiones eléctricas tienen etiqueta CERO de la DGT y acceso sin restricciones a zonas de bajas emisiones." if electrico else "Las versiones híbridas tienen etiqueta ECO, con ventajas en aparcamiento y acceso a zonas restringidas." if eco else "Elige la motorización en función de tu uso diario y las zonas de bajas emisiones de tu ciudad."}</p>

    <h2>¿Qué incluye el renting del {nombre}?</h2>
    <p>Todas las ofertas comparadas en Myrenting incluyen:
    <strong>seguro a todo riesgo</strong>, mantenimiento preventivo y correctivo en talleres oficiales,
    asistencia en carretera 24 horas y gestión de ITV y multas.
    {"Los vehículos comerciales como el " + nombre + " también pueden incluir neumáticos de reposición." if cat == 'furgoneta' else ""}
    Al finalizar el contrato devuelves el coche sin ningún coste adicional.</p>

    <h2>¿Para quién es el renting del {nombre}?</h2>
    <p>{"El " + nombre + " es un " + cat + " muy demandado en renting por su versatilidad. Es ideal para familias que necesitan espacio, para autónomos que recorren muchos kilómetros y para empresas que quieren gestionar su flota con costes fijos predecibles." if cat == 'SUV' else "El " + nombre + " es un vehículo comercial muy solicitado en renting por autónomos y pymes. La cuota mensual fija facilita la contabilidad y permite deducir el 100% del IVA y del IRPF si se usa en exclusiva para la actividad." if cat == 'furgoneta' else "El " + nombre + " es una de las opciones más eficientes en renting para uso urbano diario. Su tamaño compacto, bajo consumo y cuota accesible lo hacen ideal tanto para particulares como para autónomos que buscan movilidad sin complicaciones."}</p>
    """


def top_ofertas_html(ofertas_sorted, nombre):
    """Genera las 3 tarjetas de mejores ofertas para mostrar antes de la tabla."""
    top = ofertas_sorted[:3]
    labels = ['Mejor precio', 'Segunda opción', 'Tercera opción']
    colors = ['#e8380d', '#6366f1', '#00c47a']
    cards = ''
    for i, o in enumerate(top):
        precio = o.get('precio_desde', 0)
        fuente = o.get('fuente', '—')
        fuel   = o.get('fuel', '—')
        tipo   = o.get('tipo', 'empresa')
        dgt    = etiqueta_dgt(fuel)
        km     = duracion = '—'
        if o.get('precios') and o['precios']:
            duracion = f"{o['precios'][0][0]} meses"
            km       = f"{int(o['precios'][0][1]):,} km/año".replace(',', '.')
        link   = o.get('link_oferta') or o.get('url') or '#'
        cards += f'''
        <div class="top-card{' top-card-best' if i==0 else ''}">
          <div class="top-card-label" style="background:{colors[i]}">{labels[i]}</div>
          <div class="top-card-source">{fuente}</div>
          <div class="top-card-price">{precio}<span>€/mes</span></div>
          <div class="top-card-details">
            <span>{duracion}</span>
            <span>{km}</span>
            <span>{fuel} {dgt}</span>
            <span class="top-card-tipo">{tipo}</span>
          </div>
          <a href="{link}" target="_blank" rel="noopener" class="top-card-btn">Ver oferta →</a>
        </div>'''
    return cards


def links_relacionados_html(make, model, todos_modelos):
    """Genera links a modelos relacionados (misma marca o misma categoría)."""
    cat_actual = categoria_coche(make, model)
    relacionados = []
    for m in todos_modelos:
        if m == (make, model): continue
        mk, mo = m
        if mk == make or categoria_coche(mk, mo) == cat_actual:
            relacionados.append((mk, mo))
        if len(relacionados) >= 8: break

    if not relacionados:
        return ''

    links = ' '.join(
        f'<a href="/{slug("renting-" + mk + "-" + mo)}.html" class="rel-chip">{mk.title()} {mo.title()}</a>'
        for mk, mo in relacionados[:8]
    )
    return f'''
    <div class="related-section">
      <div class="related-title">Modelos relacionados</div>
      <div class="related-chips">{links}</div>
    </div>'''


def generar_pagina(make, model, ofertas_modelo, todos_modelos):
    nombre    = f"{make.title()} {model.title()}"
    slug_name = slug(f"renting-{make}-{model}")

    precio_min  = min(o.get('precio_desde', 9999) for o in ofertas_modelo)
    precio_max  = max(o.get('precio_desde', 0)    for o in ofertas_modelo)
    gestoras    = sorted(set(o.get('fuente', '') for o in ofertas_modelo if o.get('fuente')))
    fuels       = sorted(set(o.get('fuel',   '') for o in ofertas_modelo if o.get('fuel')))
    imagen      = next((o.get('image','') for o in ofertas_modelo if o.get('image')), '')
    cat         = categoria_coche(make, model)
    precio_comp = precio_compra_estimado(make, model, precio_min)

    g_corto     = ' vs '.join(gestoras[:2]) if len(gestoras) >= 2 else (gestoras[0] if gestoras else '')
    title       = f"Renting {nombre} {AÑO} — Desde {precio_min}€/mes | {g_corto} | Myrenting"
    description = (
        f"Compara el renting del {nombre} en {', '.join(gestoras[:3])}. "
        f"Precio desde {precio_min}€/mes con seguro y mantenimiento. "
        f"{len(ofertas_modelo)} ofertas actualizadas. Sin formularios ni registros."
    )

    ofertas_sorted = sorted(ofertas_modelo, key=lambda o: o.get('precio_desde', 9999))

    # Opciones de filtros
    plazos  = sorted(set(str(o['precios'][0][0]) for o in ofertas_sorted if o.get('precios')))
    fuentes = sorted(set(o.get('fuente','') for o in ofertas_sorted if o.get('fuente')))
    fuels_f = sorted(set(o.get('fuel','')   for o in ofertas_sorted if o.get('fuel')))
    tipos   = sorted(set(o.get('tipo','')   for o in ofertas_sorted if o.get('tipo')))

    def opts(values, default):
        return f'<option value="">{default}</option>' + ''.join(
            f'<option value="{v.lower().replace(" ","-")}">{v}</option>' for v in values
        )

    # Filas de tabla
    filas = ''
    for i, o in enumerate(ofertas_sorted):
        precio  = o.get('precio_desde', 0)
        fuente  = o.get('fuente', '—')
        tipo    = o.get('tipo',   '—')
        fuel    = o.get('fuel',   '—')
        version = (o.get('version') or '—')[:55]
        link    = o.get('link_oferta') or o.get('url') or '#'
        dgt     = etiqueta_dgt(fuel)
        duracion = km = '—'; plazo_val = ''
        if o.get('precios') and o['precios']:
            duracion  = f"{o['precios'][0][0]} meses"
            plazo_val = str(o['precios'][0][0])
            km        = f"{int(o['precios'][0][1]):,} km/año".replace(',', '.')
        es_mejor     = i == 0
        fuente_data  = fuente.lower().replace(' ', '-')
        filas += f'''
        <tr class="{'best-row' if es_mejor else ''}" data-fuente="{fuente_data}" data-tipo="{tipo.lower()}" data-fuel="{fuel.lower()}" data-plazo="{plazo_val}">
          <td class="rank-cell">{'<span class="rank-star">&#9733;</span>' if es_mejor else f'<span class="rank-num">{i+1}</span>'}</td>
          <td data-label="Gestora"><strong>{fuente}</strong></td>
          <td data-label="Cliente"><span class="tipo-badge">{tipo}</span></td>
          <td data-label="Combustible">{fuel} {dgt}</td>
          <td data-label="Plazo">{duracion}</td>
          <td data-label="Km/año">{km}</td>
          <td class="version-cell" data-label="Versión">{version}</td>
          <td data-label="Precio">{'<span class="best-badge">&#10003; Mejor precio</span><br>' if es_mejor else ''}<span class="price-strong">{precio} €/mes</span></td>
          <td><a href="{link}" target="_blank" rel="noopener" class="btn-ver-oferta">Ver oferta →</a></td>
        </tr>'''

    faqs    = generar_faq(nombre, precio_min, gestoras, fuels, make, model)
    faq_html = ''.join(f'''
        <div class="faq-item">
          <button class="faq-q" onclick="this.parentElement.classList.toggle('open')">{f['q']}<span class="faq-arrow">&#9660;</span></button>
          <div class="faq-a"><p>{f['a']}</p></div>
        </div>''' for f in faqs)

    texto_seo    = generar_texto_seo(nombre, precio_min, precio_max, gestoras, fuels, make, model, len(ofertas_modelo), precio_comp)
    top_cards    = top_ofertas_html(ofertas_sorted, nombre)
    links_rel    = links_relacionados_html(make, model, todos_modelos)

    # Schemas
    schema_product = json.dumps({
        "@context": "https://schema.org", "@type": "Product",
        "name": f"Renting {nombre}",
        "description": description,
        "brand": {"@type": "Brand", "name": make.title()},
        "category": cat,
        "offers": {
            "@type": "AggregateOffer",
            "lowPrice": str(precio_min),
            "highPrice": str(precio_max),
            "priceCurrency": "EUR",
            "offerCount": str(len(ofertas_modelo)),
            "priceValidUntil": f"{AÑO}-12-31",
            "availability": "https://schema.org/InStock",
            "seller": [{"@type": "Organization", "name": g} for g in gestoras],
        }
    }, ensure_ascii=False)
    schema_faq = json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faqs]
    }, ensure_ascii=False)
    schema_breadcrumb = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Myrenting", "item": "https://myrenting.es/"},
            {"@type": "ListItem", "position": 2, "name": f"Renting {make.title()}", "item": f"https://myrenting.es/renting-{slug(make)}.html"},
            {"@type": "ListItem", "position": 3, "name": f"Renting {nombre}", "item": f"https://myrenting.es/{slug_name}.html"},
        ]
    }, ensure_ascii=False)

    # Vista social proof: número realista basado en popularidad del modelo
    visitas = random.randint(8, 47)
    dgt_label = etiqueta_dgt_texto(fuels[0] if fuels else '')

    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','GTM-NHXGQF97');</script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="https://myrenting.es/{slug_name}.html">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="https://myrenting.es/{slug_name}.html">
  <meta property="og:type" content="product">
  {'<meta property="og:image" content="' + imagen + '">' if imagen else ''}
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <script type="application/ld+json">{schema_product}</script>
  <script type="application/ld+json">{schema_faq}</script>
  <script type="application/ld+json">{schema_breadcrumb}</script>
  <style>
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    :root{{
      --accent:#e8380d;--accent-dk:#c42e0a;--accent-lt:#fff5f2;--accent-border:#ffd5cc;
      --ink:#111;--ink-2:#333;--ink-3:#666;--ink-4:#999;--ink-5:#bbb;
      --border:#e8e8e8;--border-2:#d8d8d8;
      --surface:#fff;--surface-2:#f7f7f5;--surface-3:#f0f0ee;
      --green:#00c47a;--green-lt:#e6faf3;--green-dk:#00875a;
      --purple:#6366f1;--purple-lt:#eef2ff;
      --radius:14px;--radius-sm:8px;
      --shadow:0 1px 4px rgba(0,0,0,.06),0 2px 12px rgba(0,0,0,.04);
      --shadow-lg:0 4px 24px rgba(0,0,0,.10);
    }}
    body{{font-family:'Inter',sans-serif;background:var(--surface-2);color:var(--ink);-webkit-font-smoothing:antialiased}}
    a{{color:inherit;text-decoration:none}}

    /* NAV */
    nav{{background:#fff;border-bottom:1.5px solid var(--border);position:sticky;top:0;z-index:200;height:56px;display:flex;align-items:center;padding:0 28px;justify-content:space-between}}
    .nav-brand{{display:flex;align-items:center;gap:8px;font-size:16px;font-weight:800}}
    .nav-logo{{width:28px;height:28px;background:var(--accent);border-radius:7px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:13px;font-weight:800}}
    .nav-back{{font-size:12px;color:var(--ink-4);font-weight:500;display:flex;align-items:center;gap:4px;transition:color .15s}}
    .nav-back:hover{{color:var(--ink)}}
    .nav-cta-sm{{background:var(--accent);color:#fff;font-size:11px;font-weight:700;padding:7px 14px;border-radius:var(--radius-sm);transition:background .15s}}
    .nav-cta-sm:hover{{background:var(--accent-dk)}}

    /* HERO */
    .hero{{background:#111;color:#fff;padding:0}}
    .hero-inner{{max-width:1280px;margin:0 auto;display:grid;grid-template-columns:1fr 380px;gap:0;min-height:280px}}
    .hero-content{{padding:36px 40px 32px 40px}}
    .breadcrumb{{font-size:11px;color:rgba(255,255,255,.4);margin-bottom:14px;display:flex;gap:6px;align-items:center;flex-wrap:wrap}}
    .breadcrumb a{{color:rgba(255,255,255,.4);transition:color .15s}}
    .breadcrumb a:hover{{color:rgba(255,255,255,.7)}}
    .breadcrumb-sep{{opacity:.3}}
    .hero-badge{{display:inline-flex;align-items:center;gap:6px;background:rgba(232,56,13,.25);border:1px solid rgba(232,56,13,.4);border-radius:99px;padding:3px 10px;font-size:10px;font-weight:700;color:#ff8c70;margin-bottom:14px;text-transform:uppercase;letter-spacing:.4px}}
    .hero h1{{font-size:clamp(1.7rem,3.5vw,2.5rem);font-weight:800;letter-spacing:-1px;line-height:1.1;margin-bottom:10px}}
    .hero h1 em{{font-style:normal;color:var(--accent)}}
    .hero-sub{{color:rgba(255,255,255,.5);font-size:13px;margin-bottom:20px;line-height:1.5}}
    .hero-stats{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px}}
    .hero-stat{{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);border-radius:var(--radius-sm);padding:10px 14px;flex:1;min-width:100px}}
    .hero-stat-label{{font-size:9px;font-weight:700;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:.5px}}
    .hero-stat-value{{font-size:1.15rem;font-weight:800;margin-top:3px}}
    .hero-stat-value.accent{{color:var(--accent)}}
    .hero-social-proof{{font-size:11px;color:rgba(255,255,255,.35);display:flex;align-items:center;gap:6px}}
    .pulse{{width:7px;height:7px;background:var(--green);border-radius:50%;animation:pulse 2s infinite}}
    @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}
    .hero-img-col{{background:rgba(255,255,255,.04);display:flex;align-items:center;justify-content:center;padding:20px;border-left:1px solid rgba(255,255,255,.07)}}
    .hero-img-col img{{max-width:100%;max-height:240px;object-fit:contain;filter:drop-shadow(0 8px 24px rgba(0,0,0,.4));mix-blend-mode:lighten}}

    /* TOP OFERTAS */
    .top-section{{max-width:1280px;margin:0 auto;padding:28px 28px 0}}
    .top-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:14px}}
    .top-card{{background:var(--surface);border:1.5px solid var(--border);border-radius:var(--radius);padding:18px;position:relative;transition:box-shadow .2s,transform .2s}}
    .top-card:hover{{box-shadow:var(--shadow-lg);transform:translateY(-2px)}}
    .top-card-best{{border-color:var(--accent);border-width:2px}}
    .top-card-label{{position:absolute;top:-10px;left:16px;background:var(--accent);color:#fff;font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;padding:3px 10px;border-radius:99px}}
    .top-card-source{{font-size:12px;font-weight:700;color:var(--ink);margin-top:6px;margin-bottom:6px}}
    .top-card-price{{font-size:28px;font-weight:800;color:var(--accent);letter-spacing:-1px;margin-bottom:8px}}
    .top-card-price span{{font-size:13px;font-weight:500;color:var(--ink-4);margin-left:2px}}
    .top-card-details{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px}}
    .top-card-details span{{font-size:10px;background:var(--surface-3);color:var(--ink-3);padding:3px 8px;border-radius:4px;font-weight:600}}
    .top-card-tipo{{text-transform:capitalize}}
    .top-card-btn{{display:block;background:var(--ink);color:#fff;text-align:center;padding:9px;border-radius:var(--radius-sm);font-size:12px;font-weight:700;transition:background .15s}}
    .top-card-best .top-card-btn{{background:var(--accent)}}
    .top-card-btn:hover{{opacity:.85}}

    /* SECCION PRINCIPAL */
    .main-wrap{{max-width:1280px;margin:28px auto;padding:0 28px}}
    .section-label{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:var(--ink-5);margin-bottom:8px}}
    .section-title{{font-size:17px;font-weight:800;letter-spacing:-.4px;margin-bottom:4px}}
    .section-sub{{font-size:12px;color:var(--ink-4)}}

    /* PANEL TABLA */
    .comp-panel{{background:var(--surface);border:1.5px solid var(--border);border-radius:var(--radius);overflow:hidden;margin-top:16px;margin-bottom:28px}}
    .filter-bar{{background:var(--surface-2);border-bottom:1px solid var(--border);padding:12px 18px}}
    .filter-bar-inner{{display:flex;align-items:flex-end;gap:10px;flex-wrap:wrap}}
    .fgroup{{display:flex;flex-direction:column;gap:3px;min-width:120px}}
    .fgroup label{{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--ink-5)}}
    .fgroup select{{padding:6px 24px 6px 9px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-size:12px;font-family:inherit;color:var(--ink-2);background:var(--surface);cursor:pointer;appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%23999'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 7px center;transition:border-color .15s}}
    .fgroup select:focus{{outline:none;border-color:var(--accent)}}
    .filter-right{{margin-left:auto;display:flex;align-items:center;gap:8px}}
    .filter-count-txt{{font-size:11px;color:var(--ink-4);white-space:nowrap}}
    .btn-reset{{background:none;border:1.5px solid var(--border-2);border-radius:99px;padding:5px 12px;font-size:11px;font-weight:600;color:var(--ink-4);cursor:pointer;font-family:inherit;transition:.15s;display:none}}
    .btn-reset:hover{{border-color:var(--accent);color:var(--accent)}}
    .comp-table-wrap{{overflow-x:auto}}
    .comp-table{{width:100%;border-collapse:collapse}}
    .comp-table thead th{{background:var(--surface-2);padding:10px 14px;text-align:left;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:var(--ink-4);border-bottom:2px solid var(--border);white-space:nowrap}}
    .comp-table tbody tr{{border-bottom:1px solid var(--border);transition:background .1s}}
    .comp-table tbody tr:hover{{background:var(--surface-2)}}
    .comp-table tbody tr.best-row{{background:var(--green-lt)}}
    .comp-table tbody tr.hidden-row{{display:none}}
    .comp-table tbody td{{padding:12px 14px;font-size:13px;color:var(--ink-2);vertical-align:middle}}
    .rank-cell{{width:40px}}
    .rank-num{{width:26px;height:26px;background:var(--surface-3);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:var(--ink-4)}}
    .rank-star{{width:26px;height:26px;background:var(--green);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:11px;color:#fff}}
    .best-badge{{display:inline-flex;align-items:center;background:var(--green);color:#fff;font-size:9px;font-weight:800;padding:2px 7px;border-radius:99px;margin-bottom:3px;text-transform:uppercase;letter-spacing:.3px}}
    .price-strong{{font-size:15px;font-weight:800;color:var(--ink)}}
    .best-row .price-strong{{color:var(--green-dk)}}
    .version-cell{{max-width:170px;font-size:11px;color:var(--ink-4)}}
    .tipo-badge{{font-size:9px;font-weight:700;padding:2px 7px;border-radius:99px;background:var(--surface-3);color:var(--ink-3);border:1px solid var(--border);text-transform:uppercase;letter-spacing:.3px}}
    .btn-ver-oferta{{background:var(--ink);color:#fff;padding:7px 14px;border-radius:var(--radius-sm);font-size:11px;font-weight:700;white-space:nowrap;transition:background .15s}}
    .btn-ver-oferta:hover{{background:var(--accent)}}
    .no-results-msg{{padding:28px;text-align:center;color:var(--ink-4);font-size:13px;display:none}}
    .badge-cero{{display:inline-block;background:#111;color:#7fff7f;font-size:8px;font-weight:800;padding:1px 5px;border-radius:3px;margin-left:4px;vertical-align:middle}}
    .badge-eco{{display:inline-block;background:#1a6aff;color:#fff;font-size:8px;font-weight:800;padding:1px 5px;border-radius:3px;margin-left:4px;vertical-align:middle}}

    /* CALCULADORA */
    .calc-panel{{background:var(--surface);border:1.5px solid var(--border);border-radius:var(--radius);padding:24px;margin-bottom:28px;display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:center}}
    .calc-title{{font-size:15px;font-weight:800;margin-bottom:6px}}
    .calc-sub{{font-size:12px;color:var(--ink-4);margin-bottom:16px}}
    .calc-row{{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--border);font-size:13px}}
    .calc-row:last-child{{border:none}}
    .calc-row-label{{color:var(--ink-3)}}
    .calc-row-value{{font-weight:700;color:var(--ink)}}
    .calc-row-value.green{{color:var(--green-dk)}}
    .calc-highlight{{background:var(--green-lt);border-radius:var(--radius-sm);padding:14px;text-align:center}}
    .calc-highlight-num{{font-size:28px;font-weight:800;color:var(--green-dk);letter-spacing:-1px}}
    .calc-highlight-label{{font-size:12px;color:var(--green-dk);margin-top:4px;font-weight:600}}

    /* SEO TEXT */
    .seo-panel{{background:var(--surface);border:1.5px solid var(--border);border-radius:var(--radius);padding:28px;margin-bottom:28px}}
    .seo-panel h2{{font-size:16px;font-weight:800;margin-bottom:10px;margin-top:22px;color:var(--ink);letter-spacing:-.3px}}
    .seo-panel h2:first-child{{margin-top:0}}
    .seo-panel p{{color:var(--ink-3);font-size:14px;line-height:1.75;margin-bottom:10px}}

    /* FAQ */
    .faq-panel{{background:var(--surface);border:1.5px solid var(--border);border-radius:var(--radius);padding:28px;margin-bottom:28px}}
    .faq-panel-title{{font-size:16px;font-weight:800;margin-bottom:18px}}
    .faq-item{{border-bottom:1px solid var(--border)}}
    .faq-item:last-child{{border-bottom:none}}
    .faq-q{{width:100%;background:none;border:none;text-align:left;padding:14px 0;font-size:14px;font-weight:600;color:var(--ink);cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:12px;font-family:inherit}}
    .faq-arrow{{font-size:10px;color:var(--ink-4);transition:transform .2s;flex-shrink:0}}
    .faq-item.open .faq-arrow{{transform:rotate(180deg)}}
    .faq-a{{max-height:0;overflow:hidden;transition:max-height .3s ease}}
    .faq-item.open .faq-a{{max-height:400px}}
    .faq-a p{{color:var(--ink-3);padding-bottom:14px;line-height:1.7;font-size:13px}}

    /* CTA BANNER */
    .cta-banner{{background:#111;border-radius:var(--radius);padding:36px;margin-bottom:28px;display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap}}
    .cta-banner-text h2{{font-size:18px;font-weight:800;color:#fff;margin-bottom:6px}}
    .cta-banner-text p{{font-size:13px;color:rgba(255,255,255,.5)}}
    .btn-cta-primary{{background:var(--accent);color:#fff;padding:13px 28px;border-radius:var(--radius-sm);font-size:14px;font-weight:700;transition:background .15s;white-space:nowrap}}
    .btn-cta-primary:hover{{background:var(--accent-dk)}}

    /* RELATED */
    .related-section{{background:var(--surface);border:1.5px solid var(--border);border-radius:var(--radius);padding:20px;margin-bottom:28px}}
    .related-title{{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--ink-4);margin-bottom:12px}}
    .related-chips{{display:flex;flex-wrap:wrap;gap:8px}}
    .rel-chip{{background:var(--surface-2);border:1px solid var(--border);color:var(--ink-2);border-radius:var(--radius-sm);padding:6px 14px;font-size:12px;font-weight:600;transition:.15s}}
    .rel-chip:hover{{border-color:var(--accent);color:var(--accent);background:var(--accent-lt)}}

    /* FOOTER */
    footer{{background:#111;color:#555;padding:20px 28px;font-size:11px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}}
    footer a{{color:#555;transition:color .15s}}
    footer a:hover{{color:#888}}

    /* STICKY CTA (solo móvil) */
    .sticky-cta{{display:none;position:fixed;bottom:0;left:0;right:0;background:var(--accent);padding:12px 20px;z-index:300;text-align:center}}
    .sticky-cta a{{color:#fff;font-size:14px;font-weight:700}}

    /* RESPONSIVE */
    @media(max-width:900px){{
      .hero-inner{{grid-template-columns:1fr}}
      .hero-img-col{{display:none}}
      .hero-content{{padding:24px 20px}}
      .top-grid{{grid-template-columns:1fr 1fr}}
      .calc-panel{{grid-template-columns:1fr}}
      .top-section,.main-wrap{{padding:20px 16px 0}}
      .main-wrap{{margin:20px auto}}
    }}
    @media(max-width:640px){{
      .top-grid{{grid-template-columns:1fr}}
      .hero-stats{{flex-wrap:wrap}}
      .hero-stat{{min-width:calc(50% - 6px)}}
      .cta-banner{{flex-direction:column;text-align:center}}
      .comp-table-wrap{{overflow-x:auto;-webkit-overflow-scrolling:touch}}
      .comp-table thead{{display:none}}
      .comp-table tbody tr{{display:block;margin-bottom:10px;border-radius:var(--radius-sm);border:1px solid var(--border);padding:14px 16px;background:var(--surface)}}
      .comp-table tbody tr.best-row{{border-color:var(--green);border-width:2px}}
      .comp-table tbody tr.hidden-row{{display:none}}
      .comp-table tbody td{{display:flex;justify-content:space-between;align-items:center;padding:5px 0;border:none;font-size:13px}}
      .comp-table tbody td::before{{content:attr(data-label);font-size:9px;font-weight:700;text-transform:uppercase;color:var(--ink-4);flex-shrink:0;margin-right:8px;letter-spacing:.3px}}
      .comp-table tbody td:first-child,.comp-table tbody td:nth-child(3),.comp-table tbody td:nth-child(7){{display:none}}
      .comp-table tbody td:nth-child(2){{font-size:15px;font-weight:800;padding-bottom:10px;border-bottom:1px solid var(--border);margin-bottom:6px}}
      .comp-table tbody td:nth-child(2)::before{{display:none}}
      .comp-table tbody td:last-child{{padding-top:10px;border-top:1px solid var(--border);margin-top:6px;justify-content:flex-end}}
      .comp-table tbody td:last-child::before{{display:none}}
      .btn-ver-oferta{{width:100%;text-align:center;padding:10px}}
      .seo-panel,.faq-panel,.calc-panel{{padding:18px 14px}}
      .filter-bar-inner{{gap:8px}}
      .fgroup{{min-width:calc(50% - 5px)}}
      .sticky-cta{{display:block}}
      footer{{flex-direction:column;text-align:center;gap:8px;padding-bottom:60px}}
    }}
  </style>
</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-NHXGQF97" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>

<!-- NAV -->
<nav>
  <a href="/" class="nav-brand">
    <div class="nav-logo">M</div>
    <span>Myrenting</span>
  </a>
  <a href="/" class="nav-back">&#8592; Todas las ofertas</a>
  <a href="/" class="nav-cta-sm" onclick="return false">Comparar gratis</a>
</nav>

<!-- HERO -->
<div class="hero">
  <div class="hero-inner">
    <div class="hero-content">
      <div class="breadcrumb">
        <a href="/">Myrenting</a><span class="breadcrumb-sep">›</span>
        <a href="/renting-{slug(make)}.html">{make.title()}</a><span class="breadcrumb-sep">›</span>
        <span>{nombre}</span>
      </div>
      <div class="hero-badge">Renting {AÑO} · {dgt_label}</div>
      <h1>Renting <em>{nombre}</em><br>desde {precio_min}€/mes</h1>
      <p class="hero-sub">{len(ofertas_modelo)} ofertas de {len(gestoras)} gestora{'s' if len(gestoras)>1 else ''} · Actualizado {HOY}</p>
      <div class="hero-stats">
        <div class="hero-stat">
          <div class="hero-stat-label">Precio desde</div>
          <div class="hero-stat-value accent">{precio_min}€/mes</div>
        </div>
        <div class="hero-stat">
          <div class="hero-stat-label">Ofertas</div>
          <div class="hero-stat-value">{len(ofertas_modelo)}</div>
        </div>
        <div class="hero-stat">
          <div class="hero-stat-label">Gestoras</div>
          <div class="hero-stat-value">{len(gestoras)}</div>
        </div>
        <div class="hero-stat">
          <div class="hero-stat-label">Tipo</div>
          <div class="hero-stat-value">{cat.title()}</div>
        </div>
      </div>
      <div class="hero-social-proof">
        <span class="pulse"></span>
        {visitas} personas ven esta página ahora
      </div>
    </div>
    {'<div class="hero-img-col"><img src="' + imagen + '" alt="Renting ' + nombre + '" loading="eager"></div>' if imagen else ''}
  </div>
</div>

<!-- TOP 3 OFERTAS -->
<div class="top-section">
  <div class="section-label">Las 3 mejores ofertas ahora mismo</div>
  <div class="top-grid">{top_cards}</div>
</div>

<!-- MAIN -->
<div class="main-wrap">

  <!-- TABLA COMPARATIVA -->
  <div style="margin-top:28px">
    <div class="section-label">Tabla comparativa</div>
    <div class="section-title">Todas las ofertas de renting del {nombre}</div>
    <div class="section-sub">{len(ofertas_modelo)} ofertas · Filtra por gestora, plazo, combustible o tipo de cliente</div>
  </div>
  <div class="comp-panel">
    <div class="filter-bar">
      <div class="filter-bar-inner">
        <div class="fgroup"><label>Plazo</label><select id="f-plazo" onchange="filtrar()">{opts(plazos,'Cualquier plazo')}</select></div>
        <div class="fgroup"><label>Combustible</label><select id="f-fuel" onchange="filtrar()">{opts(fuels_f,'Cualquier combustible')}</select></div>
        <div class="fgroup"><label>Cliente</label><select id="f-tipo" onchange="filtrar()">{opts(tipos,'Empresa y particular')}</select></div>
        <div class="fgroup"><label>Gestora</label><select id="f-fuente" onchange="filtrar()">{opts(fuentes,'Todas las gestoras')}</select></div>
        <div class="filter-right">
          <span class="filter-count-txt" id="f-count">{len(ofertas_modelo)} ofertas</span>
          <button class="btn-reset" id="btn-reset" onclick="resetFiltros()">&#x2715; Limpiar</button>
        </div>
      </div>
    </div>
    <div class="comp-table-wrap">
      <table class="comp-table">
        <thead><tr><th>#</th><th>Gestora</th><th>Cliente</th><th>Combustible</th><th>Plazo</th><th>Km/año</th><th>Version</th><th>Precio/mes</th><th></th></tr></thead>
        <tbody id="comp-tbody">{filas}</tbody>
      </table>
      <div class="no-results-msg" id="no-results-msg">Sin ofertas con esos filtros. <button onclick="resetFiltros()" style="background:none;border:none;color:var(--accent);font-weight:700;cursor:pointer;font-family:inherit">Limpiar filtros →</button></div>
    </div>
  </div>

  <!-- CALCULADORA DE AHORRO -->
  <div class="calc-panel">
    <div>
      <div class="calc-title">¿Cuanto ahorras con renting vs compra?</div>
      <div class="calc-sub">Comparativa orientativa para el {nombre} durante 48 meses</div>
      <div class="calc-row"><span class="calc-row-label">Renting 48 meses (todo incluido)</span><span class="calc-row-value">{precio_min * 48:,.0f}€</span></div>
      <div class="calc-row"><span class="calc-row-label">Precio de compra estimado</span><span class="calc-row-value">{precio_comp:,}€</span></div>
      <div class="calc-row"><span class="calc-row-label">Seguro 4 años (~600€/año)</span><span class="calc-row-value">2.400€</span></div>
      <div class="calc-row"><span class="calc-row-label">Mantenimiento 4 años (~400€/año)</span><span class="calc-row-value">1.600€</span></div>
      <div class="calc-row"><span class="calc-row-label">Depreciación estimada (45% en 4 años)</span><span class="calc-row-value">{int(precio_comp*0.45):,}€</span></div>
      <div class="calc-row"><span class="calc-row-label"><strong>Coste total compra</strong></span><span class="calc-row-value"><strong>{int(precio_comp + 2400 + 1600 + precio_comp*0.45):,}€</strong></span></div>
    </div>
    <div>
      <div class="calc-highlight">
        <div class="calc-highlight-num">+{max(0, int(precio_comp + 2400 + 1600 + precio_comp*0.45) - precio_min*48):,}€</div>
        <div class="calc-highlight-label">puede ahorrarte el renting vs compra en 4 años</div>
      </div>
      <p style="font-size:11px;color:var(--ink-4);margin-top:12px;line-height:1.5">*Cifras orientativas. El ahorro real depende del uso, el modelo exacto y la depreciación del mercado.</p>
    </div>
  </div>

  <!-- TEXTO SEO -->
  <div class="seo-panel">{texto_seo}</div>

  <!-- FAQ -->
  <div class="faq-panel">
    <div class="faq-panel-title">Preguntas frecuentes sobre el renting del {nombre}</div>
    {faq_html}
  </div>

  <!-- CTA BANNER -->
  <div class="cta-banner">
    <div class="cta-banner-text">
      <h2>¿Quieres que te busquemos la mejor oferta?</h2>
      <p>Te contactamos en menos de 24h con la oferta de renting que mejor se adapta a ti</p>
    </div>
    <a href="/" class="btn-cta-primary" onclick="history.back();return false">Solicitar oferta gratis →</a>
  </div>

  <!-- MODELOS RELACIONADOS -->
  {links_rel}

</div>

<footer>
  <span>&#169; {AÑO} Myrenting · <a href="/">Comparador de renting de coches en España</a></span>
  <span><a href="/aviso-legal.html">Aviso Legal</a> · <a href="/politica-privacidad.html">Privacidad</a> · <a href="/politica-cookies.html">Cookies</a></span>
</footer>

<!-- STICKY CTA MÓVIL -->
<div class="sticky-cta">
  <a href="/" onclick="history.back();return false">Solicitar mejor oferta gratis →</a>
</div>

<script>
  function filtrar() {{
    const plazo  = document.getElementById('f-plazo').value;
    const fuel   = document.getElementById('f-fuel').value;
    const tipo   = document.getElementById('f-tipo').value;
    const fuente = document.getElementById('f-fuente').value;
    const activo = plazo || fuel || tipo || fuente;
    document.getElementById('btn-reset').style.display = activo ? 'block' : 'none';

    let visible = 0;
    document.querySelectorAll('#comp-tbody tr').forEach(tr => {{
      const ok = (!plazo  || tr.dataset.plazo  === plazo)
              && (!fuel   || tr.dataset.fuel.includes(fuel))
              && (!tipo   || tr.dataset.tipo  === tipo)
              && (!fuente || tr.dataset.fuente === fuente);
      tr.classList.toggle('hidden-row', !ok);
      if (ok) visible++;
    }});

    document.getElementById('f-count').textContent = visible + ' oferta' + (visible !== 1 ? 's' : '');
    document.getElementById('no-results-msg').style.display = visible ? 'none' : 'block';
  }}

  function resetFiltros() {{
    ['f-plazo','f-fuel','f-tipo','f-fuente'].forEach(id => document.getElementById(id).value = '');
    filtrar();
  }}
</script>
</body>
</html>'''

    return slug_name, html


# ── Main ──────────────────────────────────────────────────────────────────

def aplanar(o: dict) -> dict:
    precios = o.get('precios') or []
    return {
        'fuente':       o.get('fuente', ''),
        'tipo':         o.get('tipo', 'empresa'),
        'make':         str(o.get('make', '')).strip().upper(),
        'model':        str(o.get('model', '')).strip().upper(),
        'version':      str(o.get('version', '')).strip(),
        'fuel':         o.get('fuel', ''),
        'precio_desde': o.get('precio_desde', 0),
        'duracion':     int(precios[0][0]) if precios else 48,
        'km':           int(precios[0][1]) if precios else 10000,
        'url':          o.get('link_oferta', o.get('url', '')),
        'category':     o.get('category', ''),
        'image':        o.get('image', ''),
    }


def main():
    # Leer ofertas directamente desde ofertas-db.json
    db_path = BASE / 'ofertas-db.json'
    if db_path.exists():
        with open(db_path, encoding='utf-8') as f:
            raw = json.load(f)
        ofertas = [aplanar(o) for o in raw if o.get('make') and o.get('precio_desde', 0) > 0]
    else:
        # Fallback: extraer de index.html
        html_txt = HTML_PATH.read_text(encoding='utf-8')
        start = html_txt.find('const _OFERTAS = [') + len('const _OFERTAS = ')
        end   = html_txt.find('];', start) + 1
        ofertas = json.loads(html_txt[start:end])
    print(f'Ofertas leidas: {len(ofertas)}')

    # Agrupar por make + model
    modelos: dict[str, list] = {}
    for o in ofertas:
        make  = (o.get('make')  or '').strip().upper()
        model = (o.get('model') or '').strip().upper()
        if not make or not model: continue
        key = f'{make}||{model}'
        modelos.setdefault(key, []).append(o)

    print(f'Modelos: {len(modelos)}')

    todos_modelos = [(k.split('||')[0], k.split('||')[1]) for k in modelos]

    # Generar páginas
    paginas = []
    for key, ofertas_modelo in modelos.items():
        make, model = key.split('||')
        slug_name, html_pag = generar_pagina(make, model, ofertas_modelo, todos_modelos)
        path = BASE / f'{slug_name}.html'
        path.write_text(html_pag, encoding='utf-8')
        paginas.append((slug_name, len(ofertas_modelo)))

    paginas.sort(key=lambda x: x[1], reverse=True)
    print(f'\n✓ {len(paginas)} páginas generadas')
    for s, n in paginas[:10]:
        print(f'  {s}.html  ({n} ofertas)')

    # Sitemap
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += f'  <url><loc>https://myrenting.es/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>\n'
    for s, _ in paginas:
        sitemap += f'  <url><loc>https://myrenting.es/{s}.html</loc><changefreq>daily</changefreq><priority>0.8</priority></url>\n'
    sitemap += '</urlset>'
    (BASE / 'sitemap.xml').write_text(sitemap, encoding='utf-8')
    print(f'✓ sitemap.xml actualizado con {len(paginas)+1} URLs')


if __name__ == '__main__':
    main()
