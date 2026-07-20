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
def fetch(url):
    import requests
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        return r.text if r.status_code == 200 else None
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
        price = p.get("price_main") or p.get("price_sale")
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
        offers.append({
            "fuente": FUENTE, "tipo": tipo, "make": make.upper(),
            "model": (model or name).upper()[:40],
            "version": (name + (" " + trim if trim else "")).strip()[:120],
            "fuel": guess_fuel(txt),
            "precio_desde": round(price, 2),
            "duracion": plazo, "km": km,
            "url": mn.get("url") or urljoin(base_url, SEGMENT_PATHS[0]),
            "category": guess_cat(txt),
            "image": mn.get("img", ""),
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
    for o in offers:                       # 1 oferta por producto y segmento (sin fragmento)
        uniq[(o["tipo"], o["url"].split("#")[0])] = o
    return list(uniq.values()), tried

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
    args = ap.parse_args()

    for pkg, imp in [("requests","requests"), ("beautifulsoup4","bs4"), ("lxml","lxml")]:
        try: __import__(imp)
        except ImportError:
            print(f"❌ Falta dependencia. Instala con:  pip install requests beautifulsoup4 lxml"); sys.exit(1)

    if args.inspect:
        inspect(args.inspect); return

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
