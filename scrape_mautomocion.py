#!/usr/bin/env python3
"""
scrape_mautomocion.py
=====================
Scraper del catálogo de renting de M Automoción (división M Renting, m-renting.com).
Vuelca las ofertas al formato _OFERTAS de MyRenting y las fusiona en
ofertas-manuales.json preservando el resto de gestoras (KIA Armotors, etc.).

USO (en tu Mac, que sí tiene internet):
    pip install requests beautifulsoup4 lxml

    # 1) EXPLORAR primero: muéstrame la estructura real de su web
    python3 scrape_mautomocion.py --inspect
    python3 scrape_mautomocion.py --inspect "https://m-renting.com/coches-renting"

    # 2) SCRAPEAR: escribe mautomocion-db.json
    python3 scrape_mautomocion.py

    # 3) FUSIONAR en ofertas-manuales.json (lo que consume la web)
    python3 scrape_mautomocion.py --merge

    # 3b) CON MATRIZ km×meses por coche (más lento; visita cada ficha)
    python3 scrape_mautomocion.py --matrix --merge

    # ver la matriz de UN coche (diagnóstico)
    python3 scrape_mautomocion.py --combos

    # parsear un HTML ya guardado (Ver código fuente -> guardar como pagina.html)
    python3 scrape_mautomocion.py --from-file pagina.html

Flujo recomendado la primera vez:
    lanza --inspect y pégame la salida; con eso te dejo los selectores exactos.
"""
import argparse, json, re, sys, time, unicodedata, html as _html
from pathlib import Path
from urllib.parse import urljoin, urlparse

BASE      = Path(__file__).parent
BASE_URL  = "https://m-renting.com"
FUENTE    = "M Automoción"
OUT_DB    = BASE / "mautomocion-db.json"
MANUALES  = BASE / "ofertas-manuales.json"

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
    "Accept-Language": "es-ES,es;q=0.9",
}

# Rutas candidatas donde suele vivir el catálogo (se prueban en orden)
CANDIDATE_PATHS = [
    "/", "/coches-renting", "/renting-particulares", "/renting-empresas",
    "/renting-autonomos", "/coches", "/vehiculos", "/ofertas", "/catalogo",
]

MARCAS = ["alfa romeo","land rover","mercedes benz","mercedes-benz","aston martin",
          "volkswagen","audi","hyundai","seat","cupra","toyota","skoda","honda","mazda",
          "omoda","jaecoo","ebro","geely","lepas","kia","peugeot","citroen","citroën",
          "renault","dacia","opel","ford","nissan","bmw","mini","volvo","fiat","mg","byd",
          "lexus","jeep","maserati","porsche","jaguar","tesla","smart","subaru","suzuki",
          "mitsubishi","infiniti","lancia","alpine","polestar","mercedes","ds"]

CATS = {
    "suv":"SUV","todoterreno":"SUV","crossover":"SUV",
    "berlina":"Berlina","sedan":"Berlina","compacto":"Compacto",
    "urbano":"Urbano","utilitario":"Urbano","pequeno":"Urbano",
    "familiar":"Familiar","monovolumen":"Monovolumen","ranchera":"Familiar",
    "furgon":"Furgoneta","furgoneta":"Furgoneta","comercial":"Furgoneta",
    "coupe":"Coupé","cabrio":"Cabrio","descapotable":"Cabrio",
    "electrico":"Eléctrico","hibrido":"Híbrido",
}

# ─── HTTP ──────────────────────────────────────────────────────────────────────
def fetch(url, verbose=False):
    import requests
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        if r.status_code != 200:
            if verbose:
                print(f"    ⚠ HTTP {r.status_code} en {url}")
            return None
        return r.text
    except Exception as e:
        print(f"    ⚠ error {url}: {e}")
        return None

# ─── HELPERS ────────────────────────────────────────────────────────────────────
def clean(s):
    return re.sub(r"\s+", " ", _html.unescape(str(s or ""))).strip()

def num(s):
    m = re.search(r"(\d[\d.\s]*)", str(s).replace(",", "."))
    return float(m.group(1).replace(".", "").replace(" ", "")) if m else None

def guess_make(text):
    t = text.lower()
    for mk in sorted(MARCAS, key=len, reverse=True):   # multi-palabra primero
        if re.search(r"\b" + re.escape(mk) + r"\b", t):
            return mk.upper().replace("-", " ")
    return ""

def price_mes(text):
    """Precio mensual: exige símbolo € (para no confundir '60 meses' con 60€)."""
    for pat in (r"(\d[\d.]{1,6})\s*€\s*/?\s*mes",
                r"€\s*(\d[\d.]{1,6})\s*/?\s*mes",
                r"(\d[\d.]{1,6})\s*€\s*al\s*mes",
                r"desde\s*(\d[\d.]{1,6})\s*€"):
        m = re.search(pat, text, re.I)
        if m:
            v = num(m.group(1))
            if v and 50 <= v <= 5000:
                return v
    return None

def km_year(text):
    m = re.search(r"(\d{1,3}(?:[.\s]\d{3}))\s*km", text, re.I)   # 10.000 km, 15 000 km
    if m:
        v = int(num(m.group(1)))
        if 3000 <= v <= 60000:
            return v
    return None

def guess_cat(text):
    t = text.lower()
    for k, v in CATS.items():
        if k in t:
            return v
    return ""

def guess_fuel(text):
    t = text.lower()
    if "eléctric" in t or "electric" in t: return "Eléctrico"
    if "híbrido enchufable" in t or "phev" in t: return "Híbrido enchufable"
    if "híbrid" in t or "hibrid" in t or "hev" in t: return "Híbrido"
    if "diésel" in t or "diesel" in t or "tdi" in t or "hdi" in t or "bluehdi" in t: return "Diésel"
    if "gasolina" in t or "tsi" in t or "tgdi" in t or "mpi" in t: return "Gasolina"
    if "glp" in t: return "GLP"
    return ""

# ─── INSPECT ──────────────────────────────────────────────────────────────────
def inspect(url):
    from bs4 import BeautifulSoup
    print(f"\n── INSPECT {url}")
    html = fetch(url)
    if not html:
        print("  ✗ no se pudo cargar (¿403/anti-bot? prueba a guardar la página y usar --from-file)")
        return
    Path("/tmp/mauto_inspect.html").write_text(html, encoding="utf-8")
    print(f"  ✓ {len(html)} bytes  (guardado en /tmp/mauto_inspect.html)")
    soup = BeautifulSoup(html, "lxml")
    ttl = soup.find("title")
    print(f"  <title>: {clean(ttl.text) if ttl else '—'}")

    # ¿datos en JSON embebido? (Next.js / configuradores)
    for tag in soup.find_all("script"):
        t = tag.get("type", "")
        idv = tag.get("id", "")
        if idv == "__NEXT_DATA__" or t == "application/json" or (tag.string and '"price"' in (tag.string or "")):
            body = (tag.string or "")[:400]
            print(f"  ★ posible JSON embebido (id={idv} type={t}): {body[:200]}…")

    # precios €/mes en el HTML
    prices = re.findall(r"(\d[\d.\s]{1,6})\s*€?\s*(?:/|al)?\s*mes", html, re.I)
    print(f"  precios '€/mes' encontrados: {len(prices)}  ej: {prices[:6]}")

    # muestra de bloque alrededor del primer precio
    m = re.search(r".{0,300}\d[\d.\s]{1,6}\s*€?\s*(?:/|al)?\s*mes.{0,120}", html, re.I | re.S)
    if m:
        frag = re.sub(r"\s+", " ", m.group(0))
        print(f"  contexto 1er precio:\n    …{frag[:360]}…")

    # enlaces internos que parezcan de coche/renting
    links = set()
    for a in soup.find_all("a", href=True):
        h = a["href"]
        if any(k in h.lower() for k in ("renting", "coche", "vehiculo", "modelo", "/p/")):
            links.add(urljoin(url, h))
    print(f"  enlaces coche/renting: {len(links)}")
    for l in list(links)[:12]:
        print(f"    → {l}")
    print("\n  ➜ Pega esta salida en el chat y te dejo los selectores exactos del scraper.")

# ─── PARSE PrestaShop ───────────────────────────────────────────────────────────
def product_links_from(html, page_url):
    """Devuelve URLs de producto de una página de listado/marca (PrestaShop)."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    links = set()
    for p in soup.select(".product-miniature, article.product-miniature, .js-product-miniature, .product_list .product"):
        a = p.select_one(".product-title a, h2 a, h3 a, a.product-thumbnail, a.thumbnail")
        if a and a.get("href"):
            links.add(urljoin(page_url, a["href"]))
    # fallback: SOLO páginas de producto reales (/oferta-renting-...), nunca listados/filtros
    for a in soup.find_all("a", href=True):
        h = a["href"]
        if re.search(r"/oferta-renting-", h, re.I) and "?" not in h and "#" not in h:
            links.add(urljoin(page_url, h))
    # paginación
    pages = set()
    for a in soup.select("a[href*='page='], .pagination a[href]"):
        pages.add(urljoin(page_url, a["href"]))
    return links, pages

def parse_product(html, url):
    """Extrae una oferta de una página de PRODUCTO (detalle) de PrestaShop."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    full = clean(soup.get_text(" "))
    h1 = soup.select_one("h1.product-title, h1[itemprop='name'], h1")
    titulo = clean(h1.get_text()) if h1 else ""
    # precio/mes: el precio actual del producto o el primer "€/mes"
    # precio fiable desde el JSON de producto PrestaShop (€/mes, IVA incl)
    precio = None
    pj = re.search(r'"price_sale"\s*:\s*([\d.]+)', html) or re.search(r'"price_main"\s*:\s*([\d.]+)', html)
    if pj:
        v = float(pj.group(1))
        if 50 <= v <= 5000: precio = v
    if not precio:                               # fallbacks
        pe = soup.select_one(".current-price [itemprop='price'], .current-price .price, .product-price .price, .current-price")
        if pe:
            v = num(pe.get("content") or pe.get_text())
            if v and 50 <= v <= 5000: precio = v
    if not precio:
        precio = price_mes(full)
    # ficha de datos (Marca / Modelo / Combustible / Plazo / Kilómetros)
    specs = {}
    for row in soup.select(".data-sheet dt, .product-features dt, table tr"):
        pass
    for dt in soup.select("dt.name, .data-sheet .name"):
        dd = dt.find_next_sibling(["dd", "td"])
        if dd: specs[clean(dt.get_text()).lower()] = clean(dd.get_text())
    txt = titulo + " " + full[:1500]
    mj = re.search(r'"manufacturer_name"\s*:\s*"([^"]+)"', html)
    make = guess_make(titulo) or (mj.group(1) if mj else "") or specs.get("marca", "") or guess_make(full[:800])
    if not precio or not make:          # descarta contenido que no es un vehículo
        return None
    # descarta páginas de aterrizaje/listado ("Renting Empresas/Autónomos/Particulares")
    if re.search(r"renting\s+(empresas?|aut[oó]nomos?|particulares?)", titulo, re.I) or "/oferta-renting-" not in url:
        return None
    model = specs.get("modelo", "")
    if not model:
        mm = re.search(re.escape(make), titulo, re.I)
        if mm: model = clean(titulo[mm.end():])
    model = re.split(r"\bdesde\b|\d+\s*€|\|", model, maxsplit=1)[0].strip()
    # quita marca duplicada al principio del modelo (p.ej. 'ŠKODA KAMIQ' -> 'KAMIQ')
    def _asc(s): return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper()
    mp = model.split()
    if mp and _asc(mp[0]) == _asc(make.split()[0]):
        model = " ".join(mp[1:])
    model = model[:40].strip()
    # plazo y km: de la combinación en la URL (#/..-10000_kms/..-60_meses) o del texto
    kmm = re.search(r"(\d{4,6})_kms", url) or re.search(r"(\d{4,6})[ .]?kms?/a", full)
    plm = re.search(r"(\d{2})_meses", url) or re.search(r"(\d{2})\s*mes", full, re.I)
    dur = int(plm.group(1)) if plm else 60
    kmv = int(kmm.group(1)) if kmm else (km_year(full) or 10000)
    u = (url + " " + titulo).lower()
    tipo = ("autonomo" if re.search(r"aut[oó]nom", u)
            else "empresa" if "empresa" in u
            else "particular")
    img = soup.select_one(".product-cover img, #product img, img[itemprop='image'], .product-thumbnail img, img")
    return {
        "fuente": FUENTE, "tipo": tipo,
        "make": make.upper(),
        "model": (model or titulo).upper()[:40].strip(),
        "version": titulo[:120],
        "fuel": guess_fuel(txt) or specs.get("combustible", ""),
        "precio_desde": precio,
        "duracion": dur,
        "km": kmv,
        "url": url,
        "category": guess_cat(txt),
        "image": urljoin(url, img.get("src") or img.get("data-src") or "") if img else "",
    }

def matrix_from_product(html, url=""):
    """Extrae TODAS las combinaciones km × meses × precio de una ficha de producto
    PrestaShop. Devuelve (matriz, diag) donde matriz = [{km, meses, price, id_pa}].

    PrestaShop guarda las combinaciones en un objeto 'combinations' (dentro de un
    <script> o de data-product='...'). Cada combinación tiene atributos (kms/meses)
    y su precio. Probamos las variantes habituales de PrestaShop 1.6/1.7/8.
    """
    diag = {}
    combos_json = None
    # 1) data-product='{...}' (PrestaShop 1.7/8)
    m = re.search(r"data-product\s*=\s*(['\"])(\{.*?\})\1", html, re.DOTALL)
    if m:
        try:
            combos_json = json.loads(_html.unescape(m.group(2)))
            diag["fuente"] = "data-product"
        except Exception as e:
            diag["data-product_error"] = str(e)[:120]
    # 2) var productDetails = {...}  /  "combinations": {...}
    if not combos_json:
        m = re.search(r'(?:var\s+productDetails\s*=\s*|"product"\s*:\s*)(\{.*?\})\s*[;,]\s*\n', html, re.DOTALL)
        if m:
            try:
                combos_json = json.loads(m.group(1)); diag["fuente"] = "productDetails"
            except Exception as e:
                diag["productDetails_error"] = str(e)[:120]

    matriz = []
    d = combos_json if isinstance(combos_json, dict) else {}
    pid = d.get("id_product") or d.get("id")
    base = (url or "").split("#")[0]

    # grupos de atributos (id_grupo -> slug) desde data-product.attributes
    grupos = {}
    for gid, a in (d.get("attributes") or {}).items():
        if isinstance(a, dict):
            grupos[str(a.get("id_attribute_group", gid))] = _slug_attr(a.get("group", ""))

    # slug de grupo -> id_grupo (nombre en data-product; si no, heurística)
    def gid_for(slug):
        for gid, gslug in grupos.items():
            if gslug and (gslug in slug or slug in gslug):
                return gid
        return "5" if "km" in slug else "6"

    # Combos COMPLETAS = combinaciones REALES ofertadas (con labels correctos):
    #   /30-kms_al_ano-10000_kms/33-plazos-60_meses
    # (no todas las parejas km×meses existen; PrestaShop hace fallback silencioso,
    #  por eso NO usamos el producto cartesiano)
    pat = re.compile(r'(\d+)-([a-z_]+)-(\d+)_(kms|meses)/(\d+)-([a-z_]+)-(\d+)_(kms|meses)')
    completas = {}   # (km,meses) -> {slug:(aid,val)}
    val2attr = {}
    for a1, s1, v1, u1, a2, s2, v2, u2 in pat.findall(html):
        seg = {s1: (a1, int(v1)), s2: (a2, int(v2))}
        km = next(v for s, (a, v) in seg.items() if "km" in s)
        me = next(v for s, (a, v) in seg.items() if "km" not in s)
        completas[(km, me)] = seg
        for s, (a, v) in seg.items():
            val2attr.setdefault(s, {})[v] = a

    diag["id_product"] = pid
    diag["grupos"] = grupos
    diag["combos_reales"] = sorted(completas.keys())
    diag["valores"] = {s: sorted(v) for s, v in val2attr.items()}

    if pid and completas and base:
        seen_ipa = set()
        items = list(completas.items())
        # 1) combos reales (labels fiables)
        for n, ((km, me), seg) in enumerate(items):
            params = {gid_for(s): a for s, (a, v) in seg.items()}
            info = _combo_price(base, pid, params, want_keys=(n == 0))
            if n == 0:
                diag["respuesta_keys"] = info.pop("_keys", None)
            if info.get("id_pa"):
                seen_ipa.add(info["id_pa"])
            matriz.append({"km": km, "meses": me, **info})
        # 2) parejas extra del cartesiano SOLO si dan un id_pa nuevo (no fallback)
        import itertools
        slugs = list(val2attr.keys())
        for combo in itertools.product(*[sorted(val2attr[s].items()) for s in slugs]):
            row = {("km" if "km" in slugs[i] else "meses"): val for i, (val, aid) in enumerate(combo)}
            if (row["km"], row["meses"]) in completas:
                continue
            params = {gid_for(slugs[i]): aid for i, (val, aid) in enumerate(combo)}
            info = _combo_price(base, pid, params)
            if not info.get("id_pa") or info["id_pa"] in seen_ipa:
                continue   # PrestaShop hizo fallback -> esa pareja no existe
            seen_ipa.add(info["id_pa"])
            matriz.append({**row, **info})
    else:
        diag["motivo_sin_matriz"] = f"pid={pid} combos_reales={len(completas)} base={'si' if base else 'no'}"

    diag["kms_en_pagina"] = sorted(set(re.findall(r"(\d{4,6})_kms", html)))
    diag["meses_en_pagina"] = sorted(set(re.findall(r"(\d{2})_meses", html)))
    return matriz, diag


def _slug_attr(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def _deep_find(obj, keys):
    """Busca recursivamente la primera aparición de cualquiera de 'keys'."""
    found = {}
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in keys and k not in found and not isinstance(v, (dict, list)):
                    found[k] = v
                walk(v)
        elif isinstance(o, list):
            for it in o:
                walk(it)
    walk(obj)
    return found


def _combo_price(base_url, pid, group_params, want_keys=False):
    """Pide a PrestaShop (AJAX refresh) el precio de UNA combinación.
    El precio mostrado es el del segmento de esa ficha (particular=con IVA,
    aut/empresa=sin IVA)."""
    import requests
    q = f"?ajax=1&action=refresh&quantity_wanted=1&id_product={pid}"
    for gid, aid in group_params.items():
        q += f"&group[{gid}]={aid}"
    try:
        r = requests.get(base_url + q, headers={**HEADERS, "X-Requested-With": "XMLHttpRequest"}, timeout=25)
        data = r.json()
    except Exception as e:
        return {"error": str(e)[:80]}
    f = _deep_find(data, {"price_amount", "price_tax_exc", "attribute_price", "id_product_attribute"})
    price = f.get("price_amount")
    # PrestaShop 1.7/8: el precio suele venir dentro del HTML 'product_prices'
    if price is None and isinstance(data, dict):
        pp = ""
        for k, v in data.items():
            if isinstance(v, str) and "price" in k.lower() and "€" in v:
                pp = v; break
        if pp:
            mm = (re.search(r'content="([\d.]+)"', pp)
                  or re.search(r'(\d[\d.]*,\d{2})\s*€', pp)
                  or re.search(r'(\d[\d.]+)\s*€', pp))
            if mm:
                price = mm.group(1)
    out = {"price": price, "sin_iva": f.get("price_tax_exc") or f.get("attribute_price"),
           "id_pa": f.get("id_product_attribute")}
    if want_keys:
        out["_keys"] = list(data.keys()) if isinstance(data, dict) else str(type(data))
    return out


def _discover_product_url():
    """Busca en los listados la primera URL de ficha de producto real."""
    for path in SEGMENT_PATHS:
        html = fetch(BASE_URL + path, verbose=True)
        if not html:
            continue
        links, _ = product_links_from(html, BASE_URL + path)
        prod = sorted(l for l in links if "/oferta-renting-" in l)
        if prod:
            return prod[0]
    return None


def combos_cmd(url):
    """Diagnóstico: vuelca la matriz km×meses de UNA ficha de producto.
    Si la URL no carga (o es 'auto'), descubre una ficha desde el listado."""
    if url == "auto":
        url = None
    if url:
        print(f"── Analizando combinaciones de: {url}")
        html = fetch(url, verbose=True)
    else:
        html = None
    if not html:
        if url:
            print("  ✗ esa URL no cargó; busco una ficha real en el listado…")
        else:
            print("── Buscando una ficha de producto en el listado…")
        url = _discover_product_url()
        if not url:
            print("  ✗ no encontré ninguna ficha de producto en los listados."); return
        print(f"  ✓ ficha encontrada: {url}")
        html = fetch(url, verbose=True)
    if not html:
        print("  ✗ no se pudo cargar la ficha"); return
    Path("/tmp/mauto_producto.html").write_text(html, encoding="utf-8")
    print(f"  ✓ {len(html)} bytes (guardado en /tmp/mauto_producto.html)")
    matriz, diag = matrix_from_product(html, url)
    print("  diagnóstico:", json.dumps(diag, ensure_ascii=False))
    if matriz:
        print(f"\n  ✅ {len(matriz)} combinaciones (precio = el del segmento de esta ficha):")
        for c in sorted(matriz, key=lambda x: (x.get('km') or 0, x.get('meses') or 0)):
            print(f"     {c.get('km')} km/año · {c.get('meses')} meses → "
                  f"{c.get('price')} €  (sin_iva {c.get('sin_iva')}, id_pa {c.get('id_pa')})")
    else:
        print("\n  ⚠ No leí la matriz aún. Volcado de estructura (pégame TODO esto):")
        # a) estructura del data-product
        m = re.search(r"data-product\s*=\s*(['\"])(\{.*?\})\1", html, re.DOTALL)
        if m:
            try:
                d = json.loads(_html.unescape(m.group(2)))
                print("  · data-product KEYS:", list(d.keys()))
                for k, v in d.items():
                    kl = k.lower()
                    if isinstance(v, (dict, list)):
                        print(f"    - {k} ({type(v).__name__}, n={len(v)}): {str(v)[:220]}")
                    elif any(t in kl for t in ("price", "attr", "combination", "id_product")):
                        print(f"    - {k} = {v}")
            except Exception as e:
                print("  · data-product no parsea:", str(e)[:120])
        # b) ¿hay un mapa de combinaciones / id_product_attribute en algún script?
        for pat, lbl in [(r'"id_product_attribute"\s*:\s*"?\d+', "id_product_attribute"),
                         (r'combinations?\s*[:=]\s*[\[{]', "combinations var"),
                         (r'"price_amount"\s*:\s*[\d.]+', "price_amount"),
                         (r'quantity_discounts', "quantity_discounts"),
                         (r'\d+-plazos-\d+_meses', "friendly combo url")]:
            hits = re.findall(pat, html)
            print(f"  · {lbl}: {len(hits)} coincidencias" + (f"  ej: {hits[0][:80]}" if hits else ""))
        # c) primeros 3 fragmentos de combinación con su contexto de precio
        for frag in sorted(set(re.findall(r'/[\w-]*kms_al_ano-\d+_kms/[\w-]*plazos-\d+_meses', html)))[:6]:
            print(f"  · combo url: {frag}")


# listados por segmento (PrestaShop pagina con ?page=N, 12 productos/página)
SEGMENT_PATHS = ["/renting-particulares", "/renting-autonomos", "/renting-empresas"]

def _seg_from_path(cat):
    c = " ".join(cat).lower()
    if "aut" in c: return "autonomo"
    if "empresa" in c: return "empresa"
    return "particular"

def parse_listing(html, base_url):
    """Parsea una página de listado: JSON de productos (js-rcpgtm-data) cruzado
    con las tarjetas (versión/acabado, URL, imagen)."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    # tarjetas por id_product -> url, acabado, imagen
    mini = {}
    for art in soup.select("article.js-product-miniature, article.product-miniature"):
        pid = art.get("data-id-product")
        if not pid: continue
        a = art.select_one("a.product_name") or art.select_one("h3 a") or art.select_one("a[title]")
        d = art.select_one(".product-desc")
        img = art.select_one("img")
        src = (img.get("data-src") or img.get("src")) if img else ""
        mini.setdefault(pid, {
            "url": urljoin(base_url, a["href"]) if a and a.get("href") else "",
            "trim": clean(d.get_text()) if d else "",
            "img": urljoin(base_url, src) if src else "",
        })
    # JSON con todos los productos de la página
    m = re.search(r'id="js-rcpgtm-data"[^>]*>(.*?)</script>', html, re.S)
    if not m: return []
    try:
        data = json.loads(m.group(1))
    except Exception:
        return []
    offers = []
    for p in data.get("detail_products_list", []):
        name = clean(p.get("name", ""))
        make = clean(p.get("manufacturer_name", "")) or guess_make(name)
        tipo = _seg_from_path(p.get("category_path", []))
        # particular -> precio con IVA · empresa/autónomo -> sin IVA (deducible)
        if tipo == "particular":
            price = p.get("price_main") or p.get("price_sale")
        else:
            price = (p.get("price_main_tax_excl") or p.get("price_sale_tax_excl")
                     or p.get("price_main") or p.get("price_sale"))
        if not name or not make or not price: continue
        try: price = float(price)
        except Exception: continue
        if not (50 <= price <= 6000): continue
        attrs = {str(k).lower(): str(v) for k, v in p.get("attributes", []) if isinstance(k, str)}
        km = int(num(attrs.get("kms al año", "") or attrs.get("kms al ano", "") or "10000") or 10000)
        plazo = int(num(attrs.get("plazos", "") or "60") or 60)
        tipo = _seg_from_path(p.get("category_path", []))
        mn = mini.get(str(p.get("id_product", "")), {})
        # modelo = nombre sin la marca al principio (insensible a acentos: 'Škoda Kamiq' -> 'Kamiq')
        def _asc(s): return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper()
        nw, mkw = name.split(), make.split()
        i = 0
        while i < len(nw) and i < len(mkw) and _asc(nw[i]) == _asc(mkw[i]):
            i += 1
        model = (" ".join(nw[i:]) if i < len(nw) else name)[:40].strip()
        trim = mn.get("trim", "")
        txt = name + " " + trim
        url = mn.get("url") or f"{BASE_URL}/oferta-renting-{tipo}-{slugify(name)}"
        offers.append({
            "fuente": FUENTE, "tipo": tipo, "make": make.upper(),
            "model": (model or name).upper()[:40],
            "version": (name + (" " + trim if trim else "")).strip()[:120],
            "fuel": guess_fuel(txt),
            "precio_desde": round(price, 2),
            "duracion": plazo, "km": km,
            "url": url,
            "category": guess_cat(txt),
            "image": mn.get("img", ""),
            "_id": p.get("id_product"),
        })
    return offers

def find_and_scrape(deep=True):
    tried, offers = [], []
    for path in SEGMENT_PATHS:
        page = 1
        while page <= 15:
            url = urljoin(BASE_URL, path) + (f"?page={page}" if page > 1 else "")
            h = fetch(url); tried.append((url, bool(h)))
            if not h: break
            offs = parse_listing(h, url)
            if not offs: break
            offers += offs
            print(f"  {path} p{page}: {len(offs)}")
            page += 1
            time.sleep(0.6)
    uniq = {}
    for o in offers:                       # 1 oferta por producto (id_product) y segmento
        uniq[(o["tipo"], o.get("_id") or o["url"].split("#")[0])] = o
    out = list(uniq.values())
    for o in out:
        o.pop("_id", None)
    return out, tried

# ─── MATRIZ km×meses por oferta ───────────────────────────────────────────────
def enrich_with_matrix(offers):
    """Visita la ficha de cada oferta y le añade 'combinaciones': la matriz
    km×meses×precio real (precio del segmento de esa ficha). Es LENTO: una
    petición por ficha + varias por combinación."""
    total = len(offers)
    n_ok = n_combos = 0
    print(f"── Extrayendo matriz km×meses de {total} ofertas (esto tarda)…")
    for i, o in enumerate(offers, 1):
        u = (o.get("url") or "").split("#")[0]
        if "/oferta-renting-" not in u:
            continue
        h = fetch(u)
        if not h:
            continue
        matriz, _ = matrix_from_product(h, u)
        combos = []
        for r in matriz:
            p = r.get("price")
            try:
                p = float(str(p).replace(".", "").replace(",", ".")) if isinstance(p, str) and "," in str(p) else float(p)
            except Exception:
                p = None
            if r.get("km") and r.get("meses") and p:
                combos.append({"km": r["km"], "meses": r["meses"], "precio": round(p, 2)})
        if combos:
            o["combinaciones"] = sorted(combos, key=lambda x: (x["km"], x["meses"]))
            n_ok += 1
            n_combos += len(combos)
        if i % 10 == 0 or i == total:
            print(f"    {i}/{total}  (ofertas con matriz: {n_ok}, combinaciones: {n_combos})")
        time.sleep(0.3)
    print(f"  ✓ matriz añadida a {n_ok}/{total} ofertas ({n_combos} combinaciones en total)")


# ─── MERGE ────────────────────────────────────────────────────────────────────
def merge_into_manuales(offers):
    data = []
    if MANUALES.exists():
        data = json.loads(MANUALES.read_text(encoding="utf-8"))
    # quita las de M Automoción antiguas y añade las nuevas
    data = [o for o in data if o.get("fuente") != FUENTE]
    data.extend(offers)
    MANUALES.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✓ ofertas-manuales.json: {len(offers)} de {FUENTE} (total {len(data)})")

# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inspect", nargs="?", const=BASE_URL, help="Explora la web y muestra su estructura")
    ap.add_argument("--from-file", help="Parsea un HTML guardado en disco")
    ap.add_argument("--merge", action="store_true", help="Fusiona el resultado en ofertas-manuales.json")
    ap.add_argument("--combos", nargs="?", const="auto", metavar="URL",
                    help="Vuelca la matriz km×meses×precio de UNA ficha (sin URL: la busca solo)")
    ap.add_argument("--matrix", action="store_true",
                    help="Añade a cada oferta su matriz km×meses×precio (LENTO: visita cada ficha)")
    args = ap.parse_args()

    for pkg, imp in [("requests","requests"), ("beautifulsoup4","bs4"), ("lxml","lxml")]:
        try: __import__(imp)
        except ImportError:
            print(f"❌ Falta dependencia. Instala con:  pip install requests beautifulsoup4 lxml"); sys.exit(1)

    if args.inspect:
        inspect(args.inspect); return

    if args.combos:
        combos_cmd(args.combos); return

    if args.from_file:
        html = Path(args.from_file).read_text(encoding="utf-8")
        offers = parse_listing(html, BASE_URL)
        print(f"  (from-file) {len(offers)} ofertas parseadas del listado")
    else:
        print("── Scrapeando m-renting.com…")
        offers, tried = find_and_scrape()
        for u, ok in tried:
            print(f"    {'✓' if ok else '✗'} {u}")

    print(f"\n✅ {len(offers)} ofertas extraídas de {FUENTE}")
    from collections import Counter
    seg = Counter(o["tipo"] for o in offers)
    print(f"   por segmento: " + " · ".join(f"{k}: {v}" for k, v in seg.items()))
    for o in offers[:10]:
        print(f"   · [{o['tipo'][:4]}] {o['make']} {o['model']} — {o['precio_desde']}€/mes ({o['duracion']}m/{o['km']}km) [{o['category'] or '?'}]")
    if len(offers) > 10:
        print(f"   … y {len(offers)-10} más")

    if args.matrix:
        enrich_with_matrix(offers)

    OUT_DB.write_text(json.dumps(offers, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n💾 Guardado en {OUT_DB.name}")
    if args.merge:
        merge_into_manuales(offers)
    else:
        print("   (usa --merge para volcarlas a ofertas-manuales.json)")

    if not offers:
        print("\n⚠ 0 ofertas: probablemente el catálogo carga por JS/API.")
        print("   Lanza:  python3 scrape_mautomocion.py --inspect   y pégame la salida.")

if __name__ == "__main__":
    main()
