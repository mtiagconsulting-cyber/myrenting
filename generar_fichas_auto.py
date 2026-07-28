#!/usr/bin/env python3
"""
generar_fichas_auto.py — Crea fichas v4 para CUALQUIER modelo presente en
index.html (_OFERTAS) que aún no tenga ficha, clonando una plantilla de la
MISMA marca (o una por defecto) y sustituyendo nombre/precio/imagen/categoría.

Tras ejecutarlo:  python3 actualizar_fichas.py   (rellena tabla + IVA + datos)
Idempotente: si la ficha ya existe, la salta.
"""
import json, re, glob
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
IDX = BASE / 'index.html'
ALL = json.loads(re.search(r'const _OFERTAS\s*=\s*(\[.*?\]);', IDX.read_text(encoding='utf-8'), re.DOTALL).group(1))

# marcas que se muestran en mayúsculas/acrónimo (no title-case)
BRAND_DISP = {'MG': 'MG', 'BMW': 'BMW', 'BYD': 'BYD', 'DS': 'DS', 'DFSK': 'DFSK',
              'CUPRA': 'Cupra', 'SEAT': 'Seat', 'KIA': 'Kia'}


def slugify(s):
    s = s.lower()
    for a, b in [('á','a'),('à','a'),('ä','a'),('é','e'),('è','e'),('ë','e'),('í','i'),
                 ('ó','o'),('ö','o'),('ú','u'),('ü','u'),('ñ','n'),('š','s')]:
        s = s.replace(a, b)
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', s)).strip('-')


def disp(s):
    return ' '.join(BRAND_DISP.get(w, w.capitalize()) for w in str(s).split())


def stats(make, model):
    offs = [o for o in ALL if o['make'] == make and o['model'] == model]
    ps = [float(o['precio_desde']) for o in offs]
    return dict(low=int(min(ps)), high=int(round(max(ps))), n=len(offs),
                img=next((o['image'] for o in offs if o.get('image')), ''),
                cat=next((o['category'] for o in offs if o.get('category')), ''))


def existing_fichas():
    """marca-slug -> (stem, brand_disp, name_disp) de una ficha v4 existente."""
    m = {}
    for f in sorted(glob.glob(str(BASE / 'renting-*.html'))):
        c = open(f, encoding='utf-8').read()
        if 'compare-grid' not in c or 'car-header' not in c:
            continue
        bm = re.search(r'class="car-brand">([^<]+)</(?:div|h1)>', c)
        nm = re.search(r'class="car-name">([^<]+)</(?:div|h1)>', c)
        if bm and nm:
            bare = Path(f).stem[len('renting-'):]   # 'opel-corsa' (sin prefijo)
            m.setdefault(slugify(bm.group(1)), (bare, bm.group(1).strip(), nm.group(1).strip()))
    return m


def build(tpl, make, model, cat):
    stem, tbrand, tname = tpl        # stem SIN 'renting-'
    st = stats(make, model)
    new_slug = slugify(f'{make} {model}')
    dest = BASE / f'renting-{new_slug}.html'
    if dest.exists():
        return 'skip'
    c = (BASE / f'renting-{stem}.html').read_text(encoding='utf-8')
    disp_new = f'{disp(make)} {disp(model)}'
    t_low = re.search(r'desde (\d+)€', c)
    t_low = t_low.group(1) if t_low else None

    # 1) nombre completo "Marca Modelo" (display + MAYÚS + slug)
    c = c.replace(tname, disp_new)
    c = c.replace(tname.upper(), disp_new.upper())
    c = c.replace(stem, new_slug)
    # 2) marca suelta (breadcrumb/JSON-LD) + enlace al hub si cambia de marca
    if slugify(tbrand) != slugify(disp(make)):
        c = c.replace(tbrand, disp(make))
        c = c.replace(tbrand.upper(), disp(make).upper())
        c = c.replace(f'renting-{slugify(tbrand)}.html', f'renting-{slugify(disp(make))}.html')
    # 3) fuera sección "por ciudades" (enlaces a ciudades inexistentes)
    c = re.sub(r'<section class="ciudades-seo".*?</section>', '', c, flags=re.DOTALL)
    # 4) precios/contadores/categoría (head + JSON-LD; la tabla la regenera actualizar_fichas)
    c = re.sub(r'("lowPrice":\s*")\d+(")', rf'\g<1>{st["low"]}\g<2>', c)
    c = re.sub(r'("highPrice":\s*")\d+(")', rf'\g<1>{st["high"]}\g<2>', c)
    c = re.sub(r'("offerCount":\s*")\d+(")', rf'\g<1>{st["n"]}\g<2>', c)
    c = re.sub(r'("category":\s*")[^"]+(")', rf'\g<1>{(cat or st["cat"] or "SUV").lower()}\g<2>', c, count=1)
    if t_low:
        c = c.replace(f'desde {t_low}€', f'desde {st["low"]}€')
        c = re.sub(rf'\b{t_low}€', f'{st["low"]}€', c)
    c = re.sub(r'\b\d+ ofertas reales', f'{st["n"]} ofertas reales', c)
    # 5) imagen
    if st['img']:
        c = re.sub(r'(<meta property="og:image" content=")[^"]+(")', rf'\g<1>{st["img"]}\g<2>', c, count=1)
        c = re.sub(r'(class="car-img-wrap"><img src=")[^"]+(")', rf'\g<1>{st["img"]}\g<2>', c, count=1)

    # 6) SEO tags canónicos (no depender del título de la plantilla, que puede
    #    traer precio/gestora equivocados)
    titulo = f"Renting {disp_new} Sin Entrada — desde {st['low']}€/mes | MyRenting"
    desc = (f"Renting del {disp_new} desde {st['low']}€/mes con todo incluido: "
            f"seguro, mantenimiento e impuestos. Compara ofertas reales en MyRenting, "
            f"sin entrada y sin registro.")
    c = re.sub(r'<title>.*?</title>', f'<title>{titulo}</title>', c, count=1, flags=re.DOTALL)
    c = re.sub(r'(<meta name="description" content=")[^"]*(")', rf'\g<1>{desc}\g<2>', c, count=1)
    c = re.sub(r'(<meta property="og:title" content=")[^"]*(")', rf'\g<1>{titulo}\g<2>', c, count=1)
    c = re.sub(r'(<meta property="og:description" content=")[^"]*(")', rf'\g<1>{desc}\g<2>', c, count=1)
    dest.write_text(c, encoding='utf-8')
    return 'ok'


def main():
    tpl = existing_fichas()
    # plantilla por defecto para marcas sin ficha propia (un coche neutro)
    default = None
    for cand in ('opel-corsa', 'toyota-yaris', 'seat-leon'):
        b = tpl.get(cand.split('-')[0])
        if b and b[0] == cand:
            default = b; break
    default = default or tpl.get('opel') or tpl.get('toyota') or next(iter(tpl.values()))
    by = defaultdict(list)
    for o in ALL:
        by[(o['make'], o['model'])].append(o)
    created = skipped = 0
    for (make, model) in sorted(by):
        if (BASE / f'renting-{slugify(make + " " + model)}.html').exists():
            continue
        t = tpl.get(slugify(make), default)
        r = build(t, make, model, by[(make, model)][0].get('category', ''))
        if r == 'ok':
            created += 1
            print(f'  CREADA renting-{slugify(make + " " + model)}.html  (plantilla {t[0]}, desde {stats(make,model)["low"]}€)')
        else:
            skipped += 1
    print(f'Fichas creadas: {created} · saltadas: {skipped}')


if __name__ == '__main__':
    main()
