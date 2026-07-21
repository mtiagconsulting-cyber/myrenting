#!/usr/bin/env python3
"""
Descarga las imágenes de las ofertas de M Automoción (hoy servidas desde
m-renting.com) a /img/modelos y reescribe las URLs a rutas locales en
ofertas-manuales.json, index.html y las fichas.

Motivo: hoy las 119 imágenes cargan de un dominio externo (m-renting.com).
Si ese dominio bloquea el hotlink, va lento o cae, la tarjeta queda en blanco
y se pierden clics. Con las imágenes locales el rendimiento y la fiabilidad
suben, y controlamos el activo.

USO (en tu Mac, con salida a internet):
    python3 descargar_imagenes_mautomocion.py            # descarga + reescribe
    python3 descargar_imagenes_mautomocion.py --dry      # solo muestra qué haría

Luego:  git add img/modelos ofertas-manuales.json index.html renting-*.html
        git commit -m "Imagenes M Automocion locales" && git push
"""
import json, os, re, sys, urllib.request, hashlib, ssl

DRY = '--dry' in sys.argv

# --- contexto SSL robusto (Python en macOS a menudo no encuentra los certs) ---
try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CTX = ssl._create_unverified_context()   # imágenes públicas: verificación no crítica
OUT = 'img/modelos'
os.makedirs(OUT, exist_ok=True)

def slug(s):
    s = s.lower()
    for a, b in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u'),('ñ','n')]:
        s = s.replace(a, b)
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

man = json.load(open('ofertas-manuales.json'))
ma = [o for o in man if o.get('fuente') == 'M Automoción' and str(o.get('image','')).startswith('http')]
print(f"Ofertas M Automoción con imagen remota: {len(ma)}")

# map remote url -> local path (una descarga por URL única)
url_local = {}
for o in ma:
    u = o['image']
    if u in url_local:
        continue
    name = 'ma-' + slug(f"{o['make']}-{o['model']}-{o['tipo']}") + '.jpg'
    url_local[u] = f"/img/modelos/{name}"

ok = fail = 0
for u, local in url_local.items():
    dest = local.lstrip('/')
    if os.path.exists(dest):
        ok += 1
        continue
    if DRY:
        print(f"  [dry] {u}  ->  {local}")
        continue
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=30, context=SSL_CTX).read()
        if len(data) < 800:      # imagen sospechosamente pequeña / placeholder
            raise ValueError(f"respuesta muy pequeña ({len(data)} bytes)")
        open(dest, 'wb').write(data)
        ok += 1
        print(f"  OK  {local}")
    except Exception as e:
        fail += 1
        print(f"  FALLO {u}: {e}")

print(f"Descargadas/existentes: {ok} | fallos: {fail}")
if DRY:
    sys.exit(0)

# reescribir sólo las URLs cuya imagen local existe
def local_if_ready(u):
    loc = url_local.get(u)
    return loc if (loc and os.path.exists(loc.lstrip('/'))) else u

# 1) ofertas-manuales.json
for o in man:
    if o.get('fuente') == 'M Automoción' and str(o.get('image','')).startswith('http'):
        o['image'] = local_if_ready(o['image'])
json.dump(man, open('ofertas-manuales.json','w'), ensure_ascii=False, indent=2)

# 2) index.html _OFERTAS
idx = open('index.html').read()
m = re.search(r'(const _OFERTAS = )(\[.*?\])(;)', idx, re.DOTALL)
d = json.loads(m.group(2))
for o in d:
    if o.get('fuente') == 'M Automoción' and str(o.get('image','')).startswith('http'):
        o['image'] = local_if_ready(o['image'])
idx = idx[:m.start()] + m.group(1) + json.dumps(d, ensure_ascii=False) + m.group(3) + idx[m.end():]
open('index.html','w').write(idx)

# 3) fichas: reemplazo literal de cada URL remota por su local
repl = {u: l for u, l in url_local.items() if os.path.exists(l.lstrip('/'))}
import glob
n = 0
for f in glob.glob('renting-*.html'):
    h = open(f).read(); h0 = h
    for u, l in repl.items():
        if u in h:
            h = h.replace(u, l)
    if h != h0:
        open(f,'w').write(h); n += 1
print(f"index.html + ofertas-manuales.json reescritos | fichas actualizadas: {n}")
