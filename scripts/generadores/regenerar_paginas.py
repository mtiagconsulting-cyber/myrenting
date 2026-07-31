import os, re, glob

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Leer todas las páginas de modelo
pages = glob.glob(os.path.join(BASE_DIR, 'renting-*.html'))
print(f"Encontradas {len(pages)} páginas")

def extract_data(content):
    """Extrae datos clave de la página existente"""
    data = {}
    
    # Título
    t = re.search(r'<title>(.*?)</title>', content)
    data['title'] = t.group(1) if t else ''
    
    # Meta description
    m = re.search(r'<meta name="description" content="(.*?)"', content)
    data['desc'] = m.group(1) if m else ''
    
    # Canonical
    c = re.search(r'<link rel="canonical" href="(.*?)"', content)
    data['canonical'] = c.group(1) if c else ''
    
    # OG image
    og = re.search(r'<meta property="og:image" content="(.*?)"', content)
    data['og_image'] = og.group(1) if og else ''
    
    # GTM
    gtm = re.search(r'(<script>\(function\(w,d.*?</script>)', content, re.DOTALL)
    data['gtm'] = gtm.group(1) if gtm else ''
    
    # JSON-LD blocks
    jld = re.findall(r'<script type="application/ld\+json">.*?</script>', content, re.DOTALL)
    data['jsonld'] = '\n'.join(jld)
    
    # H1 nombre del modelo
    h1 = re.search(r'<h1[^>]*>Renting <em>(.*?)</em>', content)
    data['model_name'] = h1.group(1) if h1 else ''
    
    # Hero sub (gestoras y num ofertas)
    hs = re.search(r'<p class="hero-sub">(.*?)</p>', content, re.DOTALL)
    data['hero_sub'] = hs.group(1).strip() if hs else ''
    
    # Hero stats
    stats = re.findall(r'<div class="hero-stat-label">(.*?)</div>\s*<div class="hero-stat-value">(.*?)</div>', content)
    data['stats'] = stats  # [(label, value), ...]
    
    # Imagen del modelo
    img_src = re.search(r'<img src="(/img/modelos/[^"]+)"', content)
    if not img_src:
        img_src = re.search(r'<source srcset="(/img/modelos/[^"]+)"', content)
    data['img'] = img_src.group(1) if img_src else ''
    
    # OG image como fallback
    if not data['img'] and data['og_image']:
        data['img'] = data['og_image']
    
    # Filter bar HTML completo
    fb = re.search(r'<div class="filter-bar">(.*?)</div>\s*</div>\s*<div class="comp-table-wrap">', content, re.DOTALL)
    data['filter_bar'] = fb.group(1).strip() if fb else ''
    
    # Tabla tbody completo
    tb = re.search(r'<tbody id="comp-tbody">(.*?)</tbody>', content, re.DOTALL)
    data['tbody'] = tb.group(1).strip() if tb else ''
    
    # Thead
    th = re.search(r'<thead>(.*?)</thead>', content, re.DOTALL)
    data['thead'] = th.group(1).strip() if th else ''
    
    # SEO / EAT / FAQ sections
    seo = re.search(r'<section class="seo-section">(.*?)</section>', content, re.DOTALL)
    data['seo_section'] = seo.group(0) if seo else ''
    
    eat = re.search(r'<section class="eat-section">(.*?)</section>', content, re.DOTALL)
    data['eat_section'] = eat.group(0) if eat else ''
    
    faq = re.search(r'<section class="faq-section">(.*?)</section>', content, re.DOTALL)
    data['faq_section'] = faq.group(0) if faq else ''
    
    # Silo links
    silo = re.search(r'<section class="silo-section">(.*?)</section>', content, re.DOTALL)
    data['silo_section'] = silo.group(0) if silo else ''
    
    # Filtros JS (filtrarTabla, resetFiltros)
    js_filter = re.search(r'<script>\s*function filtrarTabla.*?</script>', content, re.DOTALL)
    data['js_filter'] = js_filter.group(0) if js_filter else ''
    
    # FAQ JS
    js_faq = re.search(r'function toggleFaq.*?(?=</script>)', content, re.DOTALL)
    data['js_faq'] = js_faq.group(0).strip() if js_faq else ''
    
    # Breadcrumb
    bc = re.search(r'<div class="breadcrumb">(.*?)</div>', content, re.DOTALL)
    data['breadcrumb'] = bc.group(1).strip() if bc else ''
    
    return data


def build_page(data):
    model_name = data.get('model_name', '')
    img = data.get('img', '')
    stats = data.get('stats', [])

    # Extraer stats
    precio = next((v for l,v in stats if 'precio' in l.lower()), '—')
    num_ofertas = next((v for l,v in stats if 'oferta' in l.lower()), '—')
    gestoras = next((v for l,v in stats if 'gestora' in l.lower()), '—')
    ahorro = next((v for l,v in stats if 'ahorro' in l.lower()), '—')

    hero_sub = data.get('hero_sub', '')
    # Limpiar HTML del hero_sub
    hero_sub_clean = re.sub(r'<[^>]+>', '', hero_sub)

    # Precompute img HTML (avoids backslash in f-string, not allowed in Python < 3.12)
    onerror_attr = "this.parentElement.innerHTML='<div style=\"color:#ccc;font-size:12px;\">" + model_name + "</div>'"
    if img:
        img_html = '<img src="' + img + '" alt="Renting ' + model_name + '" loading="eager" decoding="async" onerror="' + onerror_attr + '">'
    else:
        img_html = '<div style="color:#ccc;font-size:13px;text-align:center;">' + model_name + '</div>'

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
  {data.get('gtm', '')}
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{data.get('title', '')}</title>
  <meta name="description" content="{data.get('desc', '')}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{data.get('canonical', '')}">
  <meta property="og:title" content="{data.get('title', '')}">
  <meta property="og:description" content="{data.get('desc', '')}">
  <meta property="og:url" content="{data.get('canonical', '')}">
  <meta property="og:type" content="website">
  <meta property="og:image" content="{data.get('og_image', '')}">
  {data.get('jsonld', '')}
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    :root{{
      --accent:#F04E00;--accent-dk:#E54E00;--accent-lt:#FFF4EE;--accent-border:#FFD4BD;
      --brand:#FF5C00;
      --ink:#111;--ink-2:#3D3D3D;--ink-3:#666;--ink-4:#999;--ink-5:#C8C8C8;
      --border:#ECECEC;--border-2:#DEDEDE;
      --surface:#fff;--surface-2:#F7F7F5;--surface-3:#FBFBF9;
      --green:#00A86B;--green-lt:#E6F7F0;--green-dk:#047a51;
      --radius:12px;--radius-sm:8px;
      --shadow:0 1px 4px rgba(0,0,0,.06),0 2px 12px rgba(0,0,0,.04);
      --shadow-lg:0 4px 24px rgba(0,0,0,.10);
    }}
    html{{scroll-behavior:smooth}}
    body{{font-family:'Inter',-apple-system,sans-serif;background:var(--surface-2);color:var(--ink);}}
    a{{color:inherit;text-decoration:none;}}

    /* NAV */
    .nav{{background:var(--surface);border-bottom:1.5px solid var(--border);height:58px;display:flex;align-items:center;justify-content:space-between;padding:0 32px;position:sticky;top:0;z-index:100;}}
    .nav-brand{{display:flex;align-items:center;gap:8px;}}
    .nav-logo{{width:28px;height:28px;background:var(--accent);border-radius:7px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:13px;font-weight:800;}}
    .nav-name{{font-size:17px;font-weight:800;letter-spacing:-.5px;}}
    .nav-back{{font-size:12px;color:var(--ink-4);font-weight:500;display:flex;align-items:center;gap:4px;}}
    .nav-back:hover{{color:var(--ink);}}

    /* BREADCRUMB */
    .breadcrumb-bar{{background:var(--surface);padding:10px 32px;border-bottom:1px solid var(--border);font-size:11px;color:var(--ink-5);}}
    .breadcrumb-bar a{{color:var(--ink-5);}}
    .breadcrumb-bar a:hover{{color:var(--ink);}}

    /* HERO */
    .hero{{background:var(--surface);padding:32px 32px 0;display:grid;grid-template-columns:1fr 420px;gap:40px;align-items:start;}}
    .hero-badges{{display:flex;gap:7px;margin-bottom:14px;flex-wrap:wrap;align-items:center;}}
    .badge{{font-size:10px;font-weight:700;padding:3px 10px;border-radius:99px;}}
    .badge-type{{background:var(--accent);color:#fff;text-transform:uppercase;letter-spacing:.5px;}}
    .badge-eco{{background:var(--green-lt);color:var(--green-dk);}}
    .badge-count{{font-size:10px;color:var(--ink-5);}}
    .hero-title{{font-size:32px;font-weight:800;letter-spacing:-1.5px;margin-bottom:6px;}}
    .hero-title em{{color:var(--accent);font-style:normal;}}
    .hero-sub{{font-size:13px;color:var(--ink-4);margin-bottom:20px;line-height:1.6;}}

    /* PRECIO DESTACADO */
    .precio-box{{background:var(--accent-lt);border:1.5px solid var(--accent-border);border-radius:var(--radius);padding:16px 20px;display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;}}
    .precio-label{{font-size:10px;color:var(--accent);font-weight:700;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px;}}
    .precio-val{{display:flex;align-items:baseline;gap:4px;}}
    .precio-desde{{font-size:13px;color:var(--ink-5);}}
    .precio-num{{font-size:36px;font-weight:800;color:var(--accent);letter-spacing:-2px;}}
    .precio-unit{{font-size:14px;color:var(--ink-5);font-weight:500;}}
    .precio-sub{{font-size:11px;color:var(--ink-5);margin-top:2px;}}
    .btn-solicitar{{background:var(--accent);color:#fff;border:none;padding:12px 20px;border-radius:var(--radius-sm);font-size:12px;font-weight:700;cursor:pointer;font-family:inherit;transition:background .15s;white-space:nowrap;}}
    .btn-solicitar:hover{{background:var(--accent-dk);}}

    /* STATS */
    .hero-stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:18px;}}
    .stat-box{{background:var(--surface-2);border-radius:var(--radius-sm);padding:12px;}}
    .stat-label{{font-size:9px;color:var(--ink-5);font-weight:700;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px;}}
    .stat-val{{font-size:14px;font-weight:800;color:var(--ink);}}

    /* TAGS */
    .hero-tags{{display:flex;gap:6px;flex-wrap:wrap;}}
    .tag{{font-size:10px;font-weight:600;padding:4px 10px;border-radius:6px;background:var(--surface-2);color:var(--ink-3);border:1px solid var(--border);}}
    .tag-eco{{background:var(--green-lt);color:var(--green-dk);border-color:var(--green-dk);}}

    /* FOTO VEHICULO */
    .hero-img{{background:var(--accent-lt);border-radius:16px;overflow:hidden;border:1px solid var(--accent-border);height:260px;display:flex;align-items:center;justify-content:center;position:relative;}}
    .hero-img img{{width:100%;height:100%;object-fit:contain;padding:16px;mix-blend-mode:multiply;}}
    .hero-img-badge{{position:absolute;top:12px;left:12px;background:rgba(0,0,0,.55);color:#fff;font-size:9px;font-weight:700;padding:3px 8px;border-radius:5px;}}

    /* SECTION */
    .section{{padding:0 32px;margin-bottom:32px;}}
    .section-title{{font-size:16px;font-weight:800;letter-spacing:-.5px;margin-bottom:4px;}}
    .section-sub{{font-size:11px;color:var(--ink-5);margin-bottom:16px;}}

    /* FILTROS DESPLEGABLES */
    .ofertas-header{{display:flex;align-items:center;justify-content:space-between;padding:16px 20px;cursor:pointer;user-select:none;background:var(--surface);border-radius:var(--radius) var(--radius) 0 0;border:1px solid var(--border);border-bottom:none;}}
    .ofertas-header-left{{display:flex;align-items:center;gap:10px;}}
    .ofertas-count{{font-size:12px;font-weight:700;color:var(--ink);}}
    .ofertas-count-badge{{background:var(--accent);color:#fff;font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;}}
    .ofertas-toggle-icon{{font-size:14px;color:var(--ink-5);transition:transform .25s;}}
    .ofertas-toggle-icon.open{{transform:rotate(180deg);}}
    .ofertas-body{{background:var(--surface);border:1px solid var(--border);border-radius:0 0 var(--radius) var(--radius);overflow:hidden;}}
    .ofertas-body.collapsed{{display:none;}}

    /* FILTROS */
    .filter-bar{{background:var(--surface-2);border-bottom:1px solid var(--border);padding:12px 16px;}}
    .filter-bar-inner{{display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end;}}
    .filter-group{{display:flex;flex-direction:column;gap:3px;min-width:120px;}}
    .filter-group label{{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--ink-5);}}
    .filter-group select{{padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-size:11px;font-family:inherit;color:var(--ink-3);background:var(--surface);cursor:pointer;outline:none;transition:border-color .15s;}}
    .filter-group select:focus,.filter-group select.active{{border-color:var(--accent);color:var(--ink);}}
    .filter-actions{{display:flex;align-items:flex-end;gap:8px;margin-left:auto;}}
    .filter-count{{font-size:11px;color:var(--ink-5);white-space:nowrap;padding-bottom:4px;}}
    .btn-reset{{background:none;border:1.5px solid var(--border-2);border-radius:99px;padding:5px 12px;font-size:11px;font-weight:600;color:var(--ink-4);cursor:pointer;font-family:inherit;transition:all .15s;}}
    .btn-reset:hover{{border-color:var(--accent);color:var(--accent);}}

    /* TABLA */
    .comp-table-wrap{{overflow-x:auto;}}
    .comp-table{{width:100%;border-collapse:collapse;}}
    .comp-table thead th{{background:var(--surface-2);padding:10px 16px;text-align:left;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:var(--ink-5);border-bottom:2px solid var(--border);white-space:nowrap;}}
    .comp-table tbody tr{{border-bottom:1px solid var(--border);transition:background .1s;}}
    .comp-table tbody tr:hover{{background:var(--surface-2);}}
    .comp-table tbody tr.best-row{{background:#fff8f5;border-left:3px solid var(--accent);}}
    .comp-table tbody tr.hidden-row{{display:none;}}
    .comp-table tbody td{{padding:12px 16px;font-size:13px;color:var(--ink-2);vertical-align:middle;}}
    .rank-num{{width:24px;height:24px;background:var(--surface-2);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:var(--ink-5);}}
    .rank-star{{width:24px;height:24px;background:var(--accent);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:11px;color:#fff;}}
    .best-badge{{display:inline-block;background:var(--accent);color:#fff;font-size:8px;font-weight:700;padding:2px 7px;border-radius:3px;margin-bottom:3px;text-transform:uppercase;}}
    .price-strong{{font-size:18px;font-weight:800;color:var(--accent);letter-spacing:-.5px;}}
    .best-row .price-strong{{color:var(--accent);font-size:20px;}}
    .version-cell{{max-width:160px;font-size:11px;color:var(--ink-4);}}
    .tipo-badge{{font-size:9px;font-weight:600;padding:2px 7px;border-radius:4px;background:var(--surface-2);color:var(--ink-4);border:1px solid var(--border);}}
    .btn-ver{{background:var(--accent);color:#fff;text-decoration:none;padding:8px 14px;border-radius:var(--radius-sm);font-size:11px;font-weight:700;white-space:nowrap;transition:background .15s;display:inline-block;}}
    .btn-ver:hover{{background:var(--accent-dk);}}
    .best-row .btn-ver{{background:var(--accent);}}
    .no-results-filter{{padding:28px;text-align:center;color:var(--ink-5);font-size:13px;}}

    /* QUE INCLUYE */
    .incluye-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;}}
    .incluye-card{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px;}}
    .incluye-title{{font-size:12px;font-weight:700;color:var(--ink);margin-bottom:4px;}}
    .incluye-sub{{font-size:11px;color:var(--ink-5);line-height:1.5;}}

    /* SEO / FAQ / SILO */
    .seo-section,.eat-section,.faq-section,.silo-section{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:28px;margin-bottom:24px;}}
    .seo-section h2,.eat-section h2,.faq-section h2,.silo-section h2{{font-size:15px;font-weight:800;margin-bottom:10px;margin-top:20px;}}
    .seo-section h2:first-child,.eat-section h2:first-child{{margin-top:0;}}
    .seo-section p,.eat-section p{{color:var(--ink-4);font-size:13px;line-height:1.75;margin-bottom:10px;}}
    .eat-section h3{{font-size:13px;font-weight:700;margin:16px 0 6px;padding-left:10px;border-left:3px solid var(--accent);}}
    .eat-section ul{{padding-left:1.2rem;margin-bottom:10px;}}
    .eat-section li{{color:var(--ink-4);font-size:12px;line-height:1.6;margin-bottom:4px;}}
    .faq-item{{border-bottom:1px solid var(--border);}}
    .faq-item:last-child{{border-bottom:none;}}
    .faq-q{{width:100%;background:none;border:none;text-align:left;padding:14px 0;font-size:13px;font-weight:600;color:var(--ink);cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:12px;font-family:inherit;}}
    .faq-arrow{{transition:transform .2s;font-size:12px;color:var(--ink-5);flex-shrink:0;}}
    .faq-item.open .faq-arrow{{transform:rotate(180deg);}}
    .faq-a{{max-height:0;overflow:hidden;transition:max-height .3s ease;}}
    .faq-item.open .faq-a{{max-height:300px;}}
    .faq-a p{{color:var(--ink-4);padding-bottom:14px;line-height:1.7;font-size:12px;}}
    .silo-grid{{display:flex;flex-wrap:wrap;gap:8px;}}
    .silo-link{{background:var(--surface-2);border:1.5px solid var(--border);border-radius:99px;padding:6px 14px;font-size:12px;font-weight:600;color:var(--ink);transition:all .15s;}}
    .silo-link:hover{{border-color:var(--accent);color:var(--accent);}}

    /* FOOTER */
    .footer{{background:#111;padding:18px 32px;display:flex;justify-content:space-between;align-items:center;margin-top:40px;}}
    .footer-brand{{display:flex;align-items:center;gap:8px;}}
    .footer-logo{{width:24px;height:24px;background:var(--accent);border-radius:6px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:11px;font-weight:800;}}
    .footer-name{{font-size:14px;font-weight:800;color:#fff;}}
    .footer-links{{display:flex;gap:20px;}}
    .footer-links a{{font-size:11px;color:#444;}}
    .footer-links a:hover{{color:#888;}}
    .footer-copy{{font-size:11px;color:#444;}}

    /* MOBILE */
    .mobile-cta{{display:none;position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:var(--accent);color:#fff;border:none;border-radius:99px;padding:14px 28px;font-size:14px;font-weight:700;font-family:inherit;box-shadow:0 4px 20px rgba(232,56,13,.4);cursor:pointer;z-index:300;white-space:nowrap;}}
    @media(max-width:768px){{
      .mobile-cta{{display:block;}}
      .nav{{padding:0 16px;}}
      .breadcrumb-bar{{padding:8px 16px;}}
      .hero{{grid-template-columns:1fr;padding:20px 16px 0;gap:20px;}}
      .hero-img{{height:180px;}}
      .hero-title{{font-size:24px;}}
      .hero-stats{{grid-template-columns:1fr 1fr;}}
      .section{{padding:0 16px;}}
      .incluye-grid{{grid-template-columns:1fr 1fr;}}
      .filter-bar-inner{{gap:8px;}}
      .filter-group{{min-width:calc(50% - 4px);}}
      .footer{{flex-direction:column;gap:12px;text-align:center;padding:16px;}}
      .footer-links{{flex-wrap:wrap;justify-content:center;}}
    }}
    @media(max-width:640px){{
      .comp-table-wrap{{overflow-x:unset;}}
      .comp-table thead{{display:none;}}
      .comp-table tbody tr{{display:block;border-bottom:none;margin-bottom:10px;border-radius:var(--radius-sm);border:1px solid var(--border);padding:14px 16px;background:var(--surface);position:relative;}}
      .comp-table tbody tr.best-row{{border-color:var(--accent);border-width:2px;border-left-width:2px;}}
      .comp-table tbody tr.hidden-row{{display:none;}}
      .comp-table tbody td{{display:flex;justify-content:space-between;align-items:center;padding:5px 0;font-size:13px;border:none;}}
      .comp-table tbody td::before{{content:attr(data-label);font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--ink-5);flex-shrink:0;margin-right:8px;}}
      .comp-table tbody td:first-child{{position:absolute;top:14px;left:16px;padding:0;width:auto;}}
      .comp-table tbody td:first-child::before{{display:none;}}
      .comp-table tbody td:nth-child(2){{font-size:15px;font-weight:800;padding-top:0;padding-left:36px;padding-bottom:10px;border-bottom:1px solid var(--border);margin-bottom:6px;}}
      .comp-table tbody td:nth-child(2)::before{{display:none;}}
      .comp-table tbody td:nth-child(3){{display:none;}}
      .comp-table tbody td:nth-child(7){{display:none;}}
      .comp-table tbody td:last-child{{padding-top:10px;border-top:1px solid var(--border);margin-top:6px;justify-content:flex-end;}}
      .comp-table tbody td:last-child::before{{display:none;}}
      .btn-ver{{width:100%;text-align:center;padding:10px;font-size:13px;}}
      .price-strong{{font-size:16px;}}
      .incluye-grid{{grid-template-columns:1fr 1fr;}}
    }}
  </style>
</head>
<body>

<nav class="nav">
  <div class="nav-brand">
    <div class="nav-logo">M</div>
    <a href="/"><span class="nav-name">MiRenting</span></a>
  </div>
  <a href="/" class="nav-back">← Todas las ofertas</a>
</nav>

<div class="breadcrumb-bar">
  {data.get('breadcrumb', '<a href="/">MiRenting</a> › <a href="/">Ofertas</a>')} › {model_name}
</div>

<!-- HERO -->
<section class="hero" style="padding-bottom:28px;">
  <div>
    <div class="hero-badges">
      <span class="badge badge-type">{model_name.split()[0] if model_name else 'Renting'}</span>
      <span class="badge-count">{num_ofertas} ofertas · {gestoras} gestoras</span>
    </div>
    <h1 class="hero-title">Renting <em>{model_name}</em></h1>
    <p class="hero-sub">{hero_sub_clean}</p>

    <div class="precio-box">
      <div>
        <div class="precio-label">Mejor precio disponible</div>
        <div class="precio-val">
          <span class="precio-desde">desde</span>
          <span class="precio-num">{precio.replace(' €/mes','').replace('€/mes','').strip()}</span>
          <span class="precio-unit">€/mes</span>
        </div>
        <div class="precio-sub">Segun condiciones · Ver tabla para mas detalles</div>
      </div>
      <button class="btn-solicitar" onclick="abrirModal()">Solicitar info</button>
    </div>

    <div class="hero-stats">
      <div class="stat-box">
        <div class="stat-label">Desde</div>
        <div class="stat-val">{precio}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Gestoras</div>
        <div class="stat-val">{gestoras}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Ofertas</div>
        <div class="stat-val">{num_ofertas}</div>
      </div>
    </div>

    <div class="hero-tags">
      <span class="tag">Sin entrada</span>
      <span class="tag">Seguro incluido</span>
      <span class="tag">Mantenimiento</span>
      <span class="tag">Asistencia 24h</span>
    </div>
  </div>

  <div class="hero-img">
    {img_html}
  </div>
</section>

<!-- OFERTAS DESPLEGABLES -->
<div class="section" style="margin-top:8px;">
  <div class="section-title">Compara todas las ofertas</div>
  <div class="section-sub">Haz clic para desplegar y filtra por km, perfil o gestora</div>

  <div class="ofertas-header" onclick="toggleOfertas(this)">
    <div class="ofertas-header-left">
      <span class="ofertas-count-badge" id="badge-count">{num_ofertas}</span>
      <span class="ofertas-count">ofertas disponibles — {model_name}</span>
    </div>
    <span class="ofertas-toggle-icon" id="toggle-icon">▼</span>
  </div>
  <div class="ofertas-body collapsed" id="ofertas-body">
    <div class="filter-bar">
      <div class="filter-bar-inner">
        {data.get('filter_bar', '')}
      </div>
    </div>
    <div class="comp-table-wrap">
      <table class="comp-table">
        <thead>{data.get('thead', '')}</thead>
        <tbody id="comp-tbody">{data.get('tbody', '')}</tbody>
      </table>
      <div class="no-results-filter" id="no-results-msg" style="display:none">
        No hay ofertas con estos filtros. <button class="btn-reset" onclick="resetFiltros()">Ver todas</button>
      </div>
    </div>
  </div>
</div>

<!-- QUE INCLUYE -->
<div class="section">
  <div class="section-title">Que incluye el renting del {model_name}</div>
  <div class="section-sub" style="margin-bottom:14px;">Todo en una cuota mensual fija</div>
  <div class="incluye-grid">
    <div class="incluye-card"><div class="incluye-title">Seguro a todo riesgo</div><div class="incluye-sub">Sin franquicia en la mayoria de ofertas</div></div>
    <div class="incluye-card"><div class="incluye-title">Mantenimiento</div><div class="incluye-sub">Revisiones y piezas incluidas</div></div>
    <div class="incluye-card"><div class="incluye-title">Asistencia 24h</div><div class="incluye-sub">En carretera en toda Europa</div></div>
    <div class="incluye-card"><div class="incluye-title">Sin entrada</div><div class="incluye-sub">Solo pagas la cuota mensual</div></div>
  </div>
</div>

<!-- SEO CONTENT -->
<div class="section">
  {data.get('seo_section', '')}
  {data.get('eat_section', '')}
</div>

<!-- FAQ -->
<div class="section">
  {data.get('faq_section', '')}
</div>

<!-- SILO -->
<div class="section">
  {data.get('silo_section', '')}
</div>

<!-- MODAL CONTACTO -->
<div id="modal-overlay" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:200;align-items:center;justify-content:center;" onclick="cerrarModal(event)">
  <div style="background:#fff;border-radius:16px;padding:32px;max-width:460px;width:90%;position:relative;" onclick="event.stopPropagation()">
    <button onclick="document.getElementById('modal-overlay').style.display='none'" style="position:absolute;top:14px;right:14px;background:var(--surface-2);border:none;border-radius:50%;width:28px;height:28px;cursor:pointer;font-size:14px;">✕</button>
    <div id="modal-form-wrap">
      <h3 style="font-size:18px;font-weight:800;margin-bottom:6px;">Solicitar informacion</h3>
      <p style="font-size:13px;color:var(--ink-4);margin-bottom:20px;" id="modal-car-info">Sobre el {model_name}</p>
      <form onsubmit="enviarLead(event)">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;">
          <div><label style="font-size:11px;font-weight:600;display:block;margin-bottom:4px;">Nombre</label><input type="text" name="nombre" required placeholder="Tu nombre" style="width:100%;padding:9px 12px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-size:13px;font-family:inherit;outline:none;"></div>
          <div><label style="font-size:11px;font-weight:600;display:block;margin-bottom:4px;">Telefono</label><input type="tel" name="telefono" required placeholder="6XX XXX XXX" style="width:100%;padding:9px 12px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-size:13px;font-family:inherit;outline:none;"></div>
        </div>
        <div style="margin-bottom:12px;"><label style="font-size:11px;font-weight:600;display:block;margin-bottom:4px;">Email</label><input type="email" name="email" required placeholder="tu@email.com" style="width:100%;padding:9px 12px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-size:13px;font-family:inherit;outline:none;"></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;">
          <div><label style="font-size:11px;font-weight:600;display:block;margin-bottom:4px;">Perfil</label><select name="perfil" style="width:100%;padding:9px 12px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-size:13px;font-family:inherit;outline:none;"><option value="particular">Particular</option><option value="autonomo">Autonomo</option><option value="empresa">Empresa</option></select></div>
          <div><label style="font-size:11px;font-weight:600;display:block;margin-bottom:4px;">Km anuales</label><select name="km" style="width:100%;padding:9px 12px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-size:13px;font-family:inherit;outline:none;"><option value="10000">10.000 km/año</option><option value="15000">15.000 km/año</option><option value="20000">20.000 km/año</option><option value="25000">25.000+ km/año</option></select></div>
        </div>
        <div style="margin-bottom:16px;"><label style="font-size:11px;font-weight:600;display:block;margin-bottom:4px;">Mensaje (opcional)</label><textarea name="mensaje" placeholder="Dinos que version te interesa o cualquier duda..." style="width:100%;padding:9px 12px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-size:13px;font-family:inherit;outline:none;resize:vertical;min-height:70px;">{model_name}</textarea></div>
        <button type="submit" style="width:100%;background:var(--accent);color:#fff;border:none;padding:12px;border-radius:var(--radius-sm);font-size:14px;font-weight:700;cursor:pointer;font-family:inherit;">Enviar solicitud</button>
      </form>
    </div>
    <div id="modal-success" style="display:none;text-align:center;padding:20px 0;">
      <div style="width:56px;height:56px;background:var(--green-lt);border-radius:50%;font-size:24px;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;">✓</div>
      <h3 style="font-size:18px;font-weight:800;margin-bottom:8px;">Solicitud enviada</h3>
      <p style="color:var(--ink-4);">Te contactaremos en las proximas 24 horas.</p>
    </div>
  </div>
</div>

<button class="mobile-cta" onclick="abrirModal()">Solicitar informacion gratis</button>

<footer class="footer">
  <div class="footer-brand">
    <div class="footer-logo">M</div>
    <span class="footer-name">MiRenting</span>
  </div>
  <div class="footer-links">
    <a href="/aviso-legal.html">Aviso legal</a>
    <a href="/politica-privacidad.html">Privacidad</a>
    <a href="/blog/">Blog</a>
  </div>
  <span class="footer-copy">2026 MiRenting · Barcelona</span>
</footer>

<script>
  // Desplegable ofertas
  function toggleOfertas(header) {{
    const body = document.getElementById('ofertas-body');
    const icon = document.getElementById('toggle-icon');
    const collapsed = body.classList.contains('collapsed');
    body.classList.toggle('collapsed', !collapsed);
    icon.classList.toggle('open', collapsed);
    if (collapsed) {{
      body.scrollIntoView({{behavior:'smooth', block:'nearest'}});
    }}
  }}

  // Auto-abrir si hay pocas ofertas
  window.addEventListener('DOMContentLoaded', () => {{
    const total = document.querySelectorAll('#comp-tbody tr').length;
    document.getElementById('badge-count').textContent = total;
    document.getElementById('filter-count') && (document.getElementById('filter-count').textContent = total + ' ofertas');
    if (total <= 4) {{
      document.getElementById('ofertas-body').classList.remove('collapsed');
      document.getElementById('toggle-icon').classList.add('open');
    }}
  }});

  // Filtros
  function filtrarTabla() {{
    const plazo  = document.getElementById('f-plazo')?.value  || '';
    const fuel   = document.getElementById('f-fuel')?.value   || '';
    const tipo   = document.getElementById('f-tipo')?.value   || '';
    const fuente = document.getElementById('f-fuente')?.value || '';
    const hayFiltro = plazo || fuel || tipo || fuente;
    const btnReset = document.getElementById('btn-reset');
    if (btnReset) btnReset.style.display = hayFiltro ? 'inline-block' : 'none';
    ['f-plazo','f-fuel','f-tipo','f-fuente'].forEach(id => {{
      const el = document.getElementById(id);
      if (el) el.classList.toggle('active', el.value !== '');
    }});
    const filas = document.querySelectorAll('#comp-tbody tr');
    let visibles = 0;
    filas.forEach(tr => {{
      const match =
        (!plazo  || tr.dataset.plazo  === plazo)  &&
        (!fuel   || tr.dataset.fuel?.includes(fuel)) &&
        (!tipo   || tr.dataset.tipo   === tipo)   &&
        (!fuente || tr.dataset.fuente === fuente);
      tr.classList.toggle('hidden-row', !match);
      if (match) visibles++;
    }});
    let num = 1;
    filas.forEach(tr => {{
      if (!tr.classList.contains('hidden-row') && !tr.classList.contains('best-row')) {{
        const cell = tr.querySelector('.rank-cell');
        if (cell) cell.innerHTML = `<span class="rank-num">${{num}}</span>`;
        num++;
      }}
    }});
    const countEl = document.getElementById('filter-count');
    if (countEl) countEl.textContent = hayFiltro ? visibles + ' de ' + filas.length + ' ofertas' : filas.length + ' ofertas';
    const noRes = document.getElementById('no-results-msg');
    if (noRes) noRes.style.display = visibles === 0 ? 'block' : 'none';
    // Auto-abrir tabla al filtrar
    document.getElementById('ofertas-body').classList.remove('collapsed');
    document.getElementById('toggle-icon').classList.add('open');
  }}

  function resetFiltros() {{
    ['f-plazo','f-fuel','f-tipo','f-fuente'].forEach(id => {{
      const el = document.getElementById(id);
      if (el) {{ el.value = ''; el.classList.remove('active'); }}
    }});
    filtrarTabla();
  }}

  // Modal
  function abrirModal() {{
    document.getElementById('modal-overlay').style.display = 'flex';
    document.getElementById('modal-form-wrap').style.display = 'block';
    document.getElementById('modal-success').style.display = 'none';
  }}
  function cerrarModal(e) {{
    if (e.target === document.getElementById('modal-overlay'))
      document.getElementById('modal-overlay').style.display = 'none';
  }}
  async function enviarLead(e) {{
    e.preventDefault();
    const form = e.target;
    const data = new FormData(form);
    try {{
      await fetch('https://formsubmit.co/ajax/info@myrenting.es', {{
        method:'POST', headers:{{'Accept':'application/json'}}, body: data
      }});
    }} catch(err) {{}}
    document.getElementById('modal-form-wrap').style.display = 'none';
    document.getElementById('modal-success').style.display = 'block';
    setTimeout(() => {{ document.getElementById('modal-overlay').style.display = 'none'; }}, 3000);
  }}

  // FAQ
  function toggleFaq(el) {{
    const item = el.closest('.faq-item');
    item.classList.toggle('open');
  }}
</script>
</body>
</html>'''


# Procesar todas las páginas
ok = 0
err = 0
for path in pages:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        data = extract_data(content)
        if not data.get('model_name'):
            print(f"SKIP (sin modelo): {os.path.basename(path)}")
            continue
        new_html = build_page(data)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_html)
        ok += 1
    except Exception as e:
        print(f"ERROR {os.path.basename(path)}: {e}")
        err += 1

print(f"\nListo: {ok} paginas regeneradas, {err} errores")
