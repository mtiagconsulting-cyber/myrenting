#!/usr/bin/env python3
"""
actualizar_hubs.py — Rellena las paginas HUB (marca / categoria / ciudad /
rango de precio) con tarjetas de modelo reales + stats + texto SEO.

Estas paginas estaban vacias (tabla sin datos) y rankeaban mal. Este generador
lee const _OFERTAS de index.html, filtra segun el tipo de hub, y sustituye la
seccion de ofertas por una rejilla de modelos que enlaza a cada ficha.

Guardarrailes: backup + validacion; solo escribe si hay >=1 modelo y la pagina
conserva sus marcadores. No toca fichas (FICHA v4) ni home.

Uso: python3 actualizar_hubs.py [slug ...]
"""
import re, json, sys, html as _h, shutil
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent
IDX = BASE / 'index.html'

def clean(s): return re.sub(r'\s+',' ',re.sub(r'[\x00-\x1f\x7f]',' ',str(s or ''))).strip()
def esc(s): return _h.escape(str(s))

def slugify(s):
    s = clean(s).lower()
    for a,b in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u'),('ñ','n'),('ü','u')]:
        s = s.replace(a,b)
    return re.sub(r'-+','-', re.sub(r'[^a-z0-9]+','-', s)).strip('-')

# ── modelos desde index _OFERTAS ─────────────────────────────────────────────
def load_models():
    idx = IDX.read_text(encoding='utf-8')
    allo = json.loads(re.search(r'const _OFERTAS\s*=\s*(\[.*?\]);', idx, re.DOTALL).group(1))
    g = defaultdict(list)
    for o in allo:
        g[(o['make'], o['model'])].append(o)
    models = []
    for (make, model), offers in g.items():
        prices = [float(o['precio_desde']) for o in offers]
        slug = slugify(make + ' ' + model)
        models.append(dict(
            make=make, model=model, name=(make + ' ' + model).title(),
            slug=slug, url=f'/renting-{slug}.html',
            price=int(min(prices)), n_off=len(offers),
            gestoras=len({o['fuente'] for o in offers}),
            image=next((o.get('image') for o in offers if o.get('image')), ''),
            category=clean(next((o.get('category') for o in offers if o.get('category')), '')),
            fuels=' '.join(sorted({clean(o.get('fuel','')).lower() for o in offers if o.get('fuel')})),
            makeslug=slugify(make),
        ))
    return models

CATEGORIES = {
    'electrico': lambda m: 'ele' in m['fuels'] or 'eléc' in m['fuels'],
    'coche-electrico': lambda m: 'ele' in m['fuels'],
    'hibrido': lambda m: any(x in m['fuels'] for x in ['hib','hybr','plug','hibrido']),
    'suv': lambda m: 'suv' in m['category'].lower() or bool(re.search(r'Q[2-8]|X[1-7]|TUCSON|QASHQAI|TIGUAN|ATECA|ARONA|KAROQ|KODIAQ|SPORTAGE|TUCSON|KUGA|CAPTUR|DUSTER|C-HR|COUNTRYMAN|FRONTERA|GRANDLAND|3008|2008|5008|T-ROC|T-CROSS|FORMENTOR|TERRAMAR', m['model'].upper())),
    'berlina': lambda m: 'berlina' in m['category'].lower() or 'sedan' in m['category'].lower(),
    'urbano': lambda m: 'urban' in m['category'].lower() or 'porton' in m['category'].lower() or 'portón' in m['category'].lower(),
    'furgoneta': lambda m: 'furgon' in m['category'].lower() or bool(re.search(r'BERLINGO|PARTNER|KANGOO|TRANSIT|VITO|SPRINTER|DUCATO|TRAFIC|VIVARO|COMBO|CADDY|DOBLO|EXPERT|JUMPY|SCUDO', m['model'].upper())),
    'gasolina': lambda m: 'gasolina' in m['fuels'],
    'diesel': lambda m: 'diesel' in m['fuels'] or 'diésel' in m['fuels'],
    'barato': lambda m: True,       # se ordena por precio y se limita
    'coches-electricos': lambda m: 'ele' in m['fuels'],
}

def classify(slug, models):
    """Devuelve (tipo, filtro_fn, limite) para el hub, o None si no aplica."""
    makes = {m['makeslug'] for m in models}
    # rango de precio renting-200-300
    mprice = re.fullmatch(r'renting-(\d{2,4})-(\d{2,4})', slug)
    if mprice:
        lo, hi = int(mprice.group(1)), int(mprice.group(2))
        return ('precio', lambda m: lo <= m['price'] <= hi, 60)
    m2 = re.fullmatch(r'renting-menos-(\d+)|renting-hasta-(\d+)', slug)
    if m2:
        hi = int(m2.group(1) or m2.group(2))
        return ('precio', lambda m: m['price'] <= hi, 60)
    body = slug[len('renting-'):] if slug.startswith('renting-') else slug
    parts = body.split('-')
    # marca (renting-audi) o marca+ciudad (renting-audi-madrid)
    if parts[0] in makes:
        mk = parts[0]
        return ('marca', lambda m, mk=mk: m['makeslug'] == mk, 40)
    # categoria (electrico, hibrido, suv, barato...)
    if body in CATEGORIES:
        limit = 24 if body != 'barato' else 40
        return ('categoria', CATEGORIES[body], limit)
    # ciudad u otras: mostrar todos (mas baratos primero)
    return ('generico', lambda m: True, 24)

HUB_CSS = """
    /* ===== HUB v4 ===== */
    .hub-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:16px;margin-top:6px;}
    .hub-card{background:#fff;border:1.5px solid var(--border);border-radius:16px;overflow:hidden;text-decoration:none;color:inherit;display:flex;flex-direction:column;transition:box-shadow .18s,transform .18s;}
    .hub-card:hover{box-shadow:0 12px 30px rgba(30,20,15,.12);transform:translateY(-3px);border-color:#e0d6ce;}
    .hub-img{height:120px;background:radial-gradient(circle at 50% 45%,#f6f3f0,#ece9e4);display:flex;align-items:center;justify-content:center;padding:12px;}
    .hub-img img{max-width:100%;max-height:100%;object-fit:contain;filter:drop-shadow(0 6px 8px rgba(0,0,0,.12));}
    .hub-body{padding:14px 16px 16px;display:flex;flex-direction:column;gap:3px;flex:1;}
    .hub-brand{font-size:10.5px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:var(--accent);}
    .hub-model{font-size:16px;font-weight:800;letter-spacing:-.3px;color:var(--ink);line-height:1.15;}
    .hub-meta{font-size:11.5px;color:var(--ink-4,#6a615b);margin-top:1px;}
    .hub-price{margin-top:auto;padding-top:8px;font-size:12.5px;color:var(--ink-4,#6a615b);}
    .hub-price b{font-size:19px;color:var(--accent);font-weight:850;letter-spacing:-.5px;}
    .hub-empty{padding:26px;text-align:center;color:var(--ink-4,#6a615b);font-size:14px;}
    .seo-block{max-width:820px;line-height:1.7;color:var(--ink-3,#4a423d);font-size:15px;}
    .seo-block p{margin:0 0 14px;}
"""

def cards_html(models):
    out = []
    for m in models:
        img = f'<img src="{esc(m["image"])}" alt="{esc(m["name"])}" loading="lazy" onerror="this.style.display=\'none\'">' if m['image'] else ''
        out.append(f'''    <a class="hub-card" href="{m['url']}">
      <div class="hub-img">{img}</div>
      <div class="hub-body">
        <div class="hub-brand">{esc(m['make'].title())}</div>
        <div class="hub-model">{esc(m['model'].title())}</div>
        <div class="hub-meta">{m['gestoras']} gestora{'s' if m['gestoras']!=1 else ''} &middot; {m['n_off']} oferta{'s' if m['n_off']!=1 else ''}</div>
        <div class="hub-price">desde <b>{m['price']}&euro;</b>/mes</div>
      </div>
    </a>''')
    return '\n'.join(out)

def seo_text(tipo, label, n, minp):
    label = clean(label)
    if tipo == 'marca':
        return (f"<p>En MyRenting comparamos <strong>{n} modelos de renting de {label}</strong> de las principales gestoras del mercado, "
                f"con precios desde <strong>{minp}&euro;/mes</strong>. Todas las ofertas incluyen seguro a todo riesgo, mantenimiento, "
                f"asistencia en carretera y sin entrada: solo pagas la cuota mensual.</p>"
                f"<p>Compara aqui todas las versiones disponibles de {label} y elige la que mejor encaja con tu perfil y kilometraje. "
                f"Al pulsar en un modelo veras las ofertas de cada gestora comparadas en las mismas condiciones.</p>")
    if tipo == 'categoria':
        return (f"<p>Encuentra tu <strong>renting {label}</strong> comparando {n} modelos de todas las gestoras, desde <strong>{minp}&euro;/mes</strong>. "
                f"Precios reales, sin entrada y con seguro y mantenimiento incluidos.</p>"
                f"<p>Filtra por marca y modelo y compara las ofertas en igualdad de condiciones (mismo plazo y kilometraje) antes de decidir.</p>")
    if tipo == 'precio':
        return (f"<p>Estos son los <strong>{n} coches en renting {label}</strong> disponibles ahora mismo, ordenados por precio. "
                f"Todo incluido en la cuota: seguro, mantenimiento y asistencia, sin entrada.</p>")
    return (f"<p>Compara <strong>{n} modelos en renting</strong> desde <strong>{minp}&euro;/mes</strong>, con seguro y mantenimiento incluidos y sin entrada.</p>")


def transform(path, models):
    c = path.read_text(encoding='utf-8')
    if 'comp-tbody' not in c or 'hero-title' not in c:
        return None
    slug = path.stem
    cls = classify(slug, models)
    if not cls: return None
    tipo, fn, limit = cls
    sel = [m for m in models if fn(m)]
    sel.sort(key=lambda m: m['price'])
    sel = sel[:limit]
    if not sel:
        return None
    minp = sel[0]['price']
    n = len(sel); ngest = len({g for m in sel for g in [m['gestoras']]})
    n_off = sum(m['n_off'] for m in sel)
    ngest_total = max(m['gestoras'] for m in sel)
    # etiqueta legible
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', c, re.DOTALL)
    label = clean(re.sub(r'<[^>]+>','', h1.group(1))) if h1 else slug
    label = re.sub(r'(?i)^renting\s+', '', label)

    # 1) stats del hero
    c = c.replace('<span class="badge-count">— ofertas · — gestoras</span>',
                  f'<span class="badge-count">{n_off} ofertas &middot; {ngest_total} gestoras</span>', 1)
    c = re.sub(r'<span class="precio-num">—</span>', f'<span class="precio-num">{minp}</span>', c, count=1)
    # los 3 stat-val "—"
    def repl_stats(m, vals=[f'{minp}€', str(ngest_total), str(n_off)]):
        repl_stats.i = getattr(repl_stats, 'i', 0)
        v = vals[repl_stats.i] if repl_stats.i < len(vals) else '—'
        repl_stats.i += 1
        return f'<div class="stat-val">{v}</div>'
    c = re.sub(r'<div class="stat-val">—</div>', repl_stats, c, count=3)
    c = c.replace('<span class="ofertas-count-badge" id="badge-count">—</span>',
                  f'<span class="ofertas-count-badge" id="badge-count">{n}</span>', 1)

    # 2) sustituir la seccion OFERTAS DESPLEGABLES por la rejilla de modelos
    grid = (f'<!-- MODELOS -->\n<div class="section" style="margin-top:8px;">\n'
            f'  <div class="section-title">{n} modelos disponibles</div>\n'
            f'  <div class="section-sub">Pulsa un modelo para comparar todas las gestoras</div>\n'
            f'  <div class="hub-grid">\n{cards_html(sel)}\n  </div>\n</div>')
    c = re.sub(r'<!-- OFERTAS DESPLEGABLES -->.*?(?=\n<!-- QUE INCLUYE -->)', grid + '\n\n', c, count=1, flags=re.DOTALL)

    # 3) SEO CONTENT
    seo = (f'<!-- SEO CONTENT -->\n<div class="section">\n  <div class="section-title">Renting {esc(label)}: como funciona</div>\n'
           f'  <div class="seo-block">{seo_text(tipo, label, n, minp)}</div>\n</div>')
    c = re.sub(r'<!-- SEO CONTENT -->\s*<div class="section">.*?</div>\s*(?=\n<!-- FAQ -->)', seo + '\n\n', c, count=1, flags=re.DOTALL)

    # 4) neutralizar el JS viejo de la tabla (referenciaba #comp-tbody, ya eliminado)
    c = re.sub(r"window\.addEventListener\('DOMContentLoaded', \(\) => \{.*?\n  \}\);",
               "/* tabla antigua eliminada */", c, count=1, flags=re.DOTALL)

    # 5) CSS
    if 'HUB v4' not in c:
        c = c.replace('</style>', HUB_CSS + '\n  </style>', 1)
    return c


def main():
    models = load_models()
    only = [a.lower().replace('renting-','') for a in sys.argv[1:]]
    fixed = skip = err = 0
    for path in sorted(BASE.glob('renting-*.html')):
        c0 = None
        try:
            c0 = path.read_text(encoding='utf-8')
        except Exception:
            continue
        if 'FICHA v4' in c0 or 'comp-tbody' not in c0:
            continue
        if only and path.stem.replace('renting-','') not in only:
            continue
        try:
            new = transform(path, models)
            if new is None:
                skip += 1; continue
            if 'hub-grid' not in new or 'MyRenting' not in new or len(new) < len(c0)*0.6:
                skip += 1; continue
            shutil.copy2(path, str(path)+'.bak')
            path.write_text(new, encoding='utf-8')
            fixed += 1
        except Exception as e:
            err += 1
            if err <= 8: print(f'  ERR {path.stem}: {e}')
    print(f'Hubs actualizadas: {fixed} | Saltadas: {skip} | Errores: {err}')

if __name__ == '__main__':
    main()
