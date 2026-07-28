#!/usr/bin/env python3
"""
scrape_quadis.py — Scraper de las ofertas de renting de QUADIS (coches y
furgonetas) para volcarlas en myrenting (ofertas-manuales.json, fuente="Quadis").

Quadis publica el renting en:
    https://www.quadis.es/coches-renting/particulares
    https://www.quadis.es/coches-renting/empresas
    https://www.quadis.es/furgonetas-renting
Precios mostrados CON IVA (particular).

USO (en tu Mac, con salida a internet):
    pip install requests beautifulsoup4 lxml

    # 1) EXPLORAR primero (muéstrame la estructura para afinar selectores):
    python3 scrape_quadis.py --inspect
    python3 scrape_quadis.py --inspect "https://www.quadis.es/coches-renting/particulares"

    # 2) SCRAPEAR -> quadis-db.json
    python3 scrape_quadis.py

    # 3) FUSIONAR en ofertas-manuales.json (lo que consume la web)
    python3 scrape_quadis.py --merge

    # parsear un HTML guardado (Ver código fuente -> guardar como pagina.html)
    python3 scrape_quadis.py --from-file pagina.html

Si el scrape sale con 0 ofertas: lanza --inspect y pégame la salida; con la
estructura real te dejo los selectores exactos (mismo método que M Automoción).
"""
import argparse, json, re, sys, time, html as _html, unicodedata
from pathlib import Path
from urllib.parse import urljoin

BASE = Path(__file__).resolve().parent
BASE_URL = "https://www.quadis.es"
FUENTE = "Quadis"
OUT_DB = BASE / "quadis-db.json"
MANUALES = BASE / "ofertas-manuales.json"

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"),
    "Accept-Language": "es-ES,es;q=0.9",
}

# listados a recorrer: (path, tipo_por_defecto, categoria_forzada)
LISTINGS = [
    ("/coches-renting",              "particular", None),
    ("/coches-renting/particulares", "particular", None),
    ("/coches-renting/empresas",     "empresa",    None),
    ("/furgonetas-renting",          "empresa",    "Furgoneta"),
]

MARCAS = ["abarth","alfa romeo","audi","bmw","byd","citroen","citroën","cupra","dacia","ds",
    "fiat","ford","honda","hyundai","jaguar","jeep","kia","land rover","lexus","mazda",
    "mercedes","mercedes-benz","mg","mini","mitsubishi","nissan","omoda","opel","peugeot",
    "polestar","porsche","renault","seat","skoda","škoda","smart","ssangyong","subaru",
    "suzuki","tesla","toyota","volkswagen","volvo","maxus","jaecoo","ebro","leapmotor",
    "lancia","dfsk","aiways","ford pro"]

CATS = {"suv":"SUV","todoterreno":"SUV","berlina":"Berlina","sedan":"Berlina",
    "compacto":"Compacto","urbano":"Urbano","utilitario":"Urbano","familiar":"Familiar",
    "monovolumen":"Monovolumen","furgon":"Furgoneta","furgoneta":"Furgoneta",
    "comercial":"Furgoneta","coupe":"Coupé","cabrio":"Cabrio","electrico":"Eléctrico"}


# ─── HTTP + helpers ──────────────────────────────────────────────────────────
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

def clean(s):
    return re.sub(r"\s+", " ", _html.unescape(str(s or ""))).strip()

def num(s):
    m = re.search(r"(\d[\d.\s]*)", str(s).replace(",", "."))
    return float(m.group(1).replace(".", "").replace(" ", "")) if m else None

def slugify(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")

def _asc(s):
    return unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().upper()

def guess_make(text):
    t = " " + _asc(text) + " "
    for mk in sorted(MARCAS, key=len, reverse=True):
        if re.search(r"\b" + re.escape(_asc(mk)) + r"\b", t):
            return _asc(mk).replace("-", " ")
    return ""

def price_mes(text):
    for pat in (r"(\d[\d.]{1,6})\s*€\s*/?\s*mes", r"€\s*(\d[\d.]{1,6})\s*/?\s*mes",
                r"(\d[\d.]{1,6})\s*€\s*al\s*mes", r"desde\s*(\d[\d.]{1,6})\s*€",
                r"(\d[\d.]{1,6})\s*€"):
        m = re.search(pat, text, re.I)
        if m:
            v = num(m.group(1))
            if v and 50 <= v <= 6000:
                return v
    return None

def km_year(text):
    m = re.search(r"(\d{1,3}(?:[.\s]?\d{3}))\s*km", text, re.I)
    if m:
        v = int(num(m.group(1)) or 0)
        if 3000 <= v <= 60000:
            return v
    return None

def plazo_meses(text):
    m = re.search(r"(\d{2})\s*mes", text, re.I)
    return int(m.group(1)) if m else None

def guess_fuel(text):
    t = _asc(text)
    if "ELECTRIC" in t or " EV" in t or "BEV" in t: return "Eléctrico"
    if "PHEV" in t or "ENCHUFABLE" in t: return "Híbrido enchufable"
    if "HYBRID" in t or "HIBRID" in t or "HEV" in t or "ECO" in t: return "Híbrido"
    if "DIESEL" in t or "TDI" in t or "HDI" in t or "BLUEHDI" in t or "CRDI" in t: return "Diésel"
    if "GASOLINA" in t or "TSI" in t or "TGDI" in t or "MPI" in t: return "Gasolina"
    return ""

def guess_cat(text, forced=None):
    if forced: return forced
    t = _asc(text)
    for k, v in CATS.items():
        if _asc(k) in t: return v
    return ""


# ─── PARSE (varias estrategias) ───────────────────────────────────────────────
def _from_jsonld(html, url, tipo, cat):
    """Estrategia 1: JSON-LD (schema.org Product / ItemList / Offer)."""
    offers = []
    for m in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S):
        try:
            data = json.loads(m.group(1))
        except Exception:
            continue
        nodes = data if isinstance(data, list) else [data]
        stack = list(nodes)
        while stack:
            n = stack.pop()
            if isinstance(n, dict):
                if n.get("@type") in ("ItemList",) and isinstance(n.get("itemListElement"), list):
                    stack += n["itemListElement"]
                if "item" in n and isinstance(n["item"], dict):
                    stack.append(n["item"])
                if n.get("@type") in ("Product", "Car", "Vehicle"):
                    name = clean(n.get("name", ""))
                    off = n.get("offers", {})
                    if isinstance(off, list): off = off[0] if off else {}
                    price = num(off.get("price") or off.get("lowPrice") or "")
                    img = n.get("image")
                    if isinstance(img, list): img = img[0] if img else ""
                    if isinstance(img, dict): img = img.get("url", "")
                    link = clean(n.get("url") or off.get("url") or "")
                    if name and price and 50 <= price <= 6000:
                        offers.append(_mk_offer(name, price, tipo, cat,
                                                urljoin(url, link) if link else url,
                                                urljoin(url, img) if img else ""))
                for v in n.values():
                    if isinstance(v, (dict, list)): stack.append(v)
            elif isinstance(n, list):
                stack += n
    return offers


def _from_cards(html, url, tipo, cat):
    """Estrategia 2: tarjetas HTML — ancla en el precio '€/mes' y sube al contenedor."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    offers, seen = [], set()
    # nodos con un precio mensual visible
    for el in soup.find_all(string=re.compile(r"\d[\d.]{1,5}\s*€\s*/?\s*mes", re.I)):
        price = price_mes(str(el))
        if not price:
            continue
        card = el.parent
        for _ in range(6):                        # sube hasta un contenedor con enlace/imagen
            if card and (card.find("a") or card.find("img")):
                break
            card = card.parent if card else None
        if not card:
            continue
        txt = clean(card.get_text(" "))
        a = card.find("a", href=True)
        link = urljoin(url, a["href"]) if a else url
        if link in seen:
            continue
        seen.add(link)
        img = card.find("img")
        src = (img.get("data-src") or img.get("src") or "") if img else ""
        # título: el enlace o el heading más cercano
        h = card.find(["h1","h2","h3","h4"])
        name = clean(h.get_text()) if h else (clean(a.get_text()) if a else txt[:80])
        if not guess_make(name):
            name = txt[:100]
        offers.append(_mk_offer(name, price, tipo, cat, link,
                                urljoin(url, src) if src else "", ctx=txt))
    return offers


def _mk_offer(name, price, tipo, cat, url, img, ctx=""):
    make = guess_make(name) or guess_make(ctx)
    model = name
    if make:
        mm = re.search(re.escape(make.split()[0]), _asc(name))
        if mm:
            model = clean(name[mm.end():])
    model = re.split(r"\bdesde\b|\d+\s*€|\|", model, maxsplit=1)[0].strip()[:40]
    txt = name + " " + ctx
    return {
        "fuente": FUENTE, "tipo": tipo,
        "make": (make or "").upper(),
        "model": (model or name).upper()[:40].strip(),
        "version": clean(name)[:120],
        "fuel": guess_fuel(txt),
        "precio_desde": round(price, 2),
        "duracion": plazo_meses(txt) or 60,
        "km": km_year(txt) or 10000,
        "url": url,
        "category": guess_cat(txt, cat),
        "image": img,
    }


# ─── API (quadis.es/api-vehicles/...) ─────────────────────────────────────────
API_ENDPOINTS = [
    ("/api-vehicles/coches-renting",    None),
    ("/api-vehicles/furgonetas-renting", "Furgoneta"),
]

def parse_quadis_cards(frag, tipo="particular", cat=None):
    """La API devuelve las tarjetas renderizadas en HTML (campo 'html').
    Cada .car-card trae: enlace /coches-renting/{marca}/{modelo}/{version}/{id},
    <h2><strong>Marca Modelo</strong><span>versión</span></h2>, precio en
    .monthlyPayment (IVA incluido) e imagen en .car-card-img-1."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(frag, "lxml")
    offers = []
    for card in soup.select(".car-card"):
        a = card.select_one("a[href*='renting/']") or card.select_one("a[href]")
        href = a.get("href", "") if a else ""
        m = re.search(r"/(?:coches|furgonetas)-renting/([^/]+)/([^/]+)/([^/]+)/(\d+)", href)
        make = model = vslug = ""
        cid = None
        if m:
            make, model, vslug, cid = m.group(1), m.group(2), m.group(3), m.group(4)
        strong = card.select_one("h2 strong")
        span = card.select_one("h2 span")
        disp = clean(strong.get_text()) if strong else ""      # "Peugeot 208"
        version = clean(span.get_text()) if span else ""        # "Allure Gasolina..."
        if not make and disp:
            make = guess_make(disp)
            model = clean(disp[len(make):]) if make else disp
        pe = card.select_one(".monthlyPayment")
        price = num(pe.get_text()) if pe else price_mes(clean(card.get_text(" ")))
        if not (make and price and 50 <= price <= 6000):
            continue
        img_el = card.select_one("img.car-card-img-1, .car-card-img img, img")
        img = (img_el.get("data-src") or img_el.get("src") or "") if img_el else ""
        if img and "car-cover" in img:
            img = ""
        fuel_el = card.select_one(".tags-renting .tag, .tag-gasolina, .tag-diesel, .tag-electrico, .tag-hibrido")
        fuel = clean(fuel_el.get_text()) if fuel_el else ""
        name = f"{make} {model} {version}"
        version_full = clean(f"{disp} {version}") if disp else clean(f"{make.replace('-',' ')} {model.replace('-',' ')} {version}")
        offers.append({
            "fuente": FUENTE, "tipo": tipo,
            "make": _asc(make.replace("-", " ")),
            "model": _asc(model.replace("-", " "))[:40].strip(),
            "version": version_full[:120],
            "fuel": (fuel or guess_fuel(name + " " + version)),
            "precio_desde": round(float(price), 2),
            "precio_con_iva": round(float(price), 2), "precio_sin_iva": None,
            "duracion": 60, "km": 10000,
            "url": urljoin(BASE_URL, href) if href else BASE_URL + "/coches-renting",
            "category": guess_cat(name + " " + version, cat),
            "image": img,
            "_id": cid,
        })
    return offers


def api_scrape():
    offers, tried = [], []
    # (endpoint, categoria_forzada, tipo)  ·  precio de Quadis = CON IVA (particular)
    for path, cat in API_ENDPOINTS:
        page, total, got_total = 1, None, 0
        while page <= 40:
            u = f"{BASE_URL}{path}?page={page}&limit=48"
            h = fetch(u, verbose=(page == 1)); tried.append((u, bool(h)))
            if not h:
                break
            try:
                data = json.loads(h)
            except Exception:
                print(f"    ⚠ {path} no devolvió JSON"); break
            frag = data.get("html") or ""
            if total is None:
                try: total = int(str(data.get("total_count") or 0))
                except Exception: total = 0
            offs = parse_quadis_cards(frag, "particular", cat)
            if not offs:
                break
            offers += offs; got_total += len(offs)
            print(f"  {path} p{page}: {len(offs)}  (total_count {total})")
            if total and got_total >= total:
                break
            if len(offs) < 48:
                break
            page += 1; time.sleep(0.4)
    uniq = {}
    for o in offers:
        key = o.get("_id") or (o["make"], o["model"], o["version"], o["precio_desde"])
        uniq[key] = o
    out = list(uniq.values())
    for o in out:
        o.pop("_id", None)
    return out, tried


def parse_listing(html, url, tipo="particular", cat=None):
    for strat in (_from_jsonld, _from_cards):
        try:
            offs = strat(html, url, tipo, cat)
        except Exception as e:
            offs = []
        offs = [o for o in offs if o.get("make") and o.get("precio_desde")]
        if offs:
            return offs, strat.__name__
    return [], "ninguna"


def next_pages(html, url):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    pages = set()
    for a in soup.select("a[href*='page='], a[href*='pagina='], .pagination a[href], a[rel='next']"):
        if a.get("href"): pages.add(urljoin(url, a["href"]))
    return pages


# ─── INSPECT ───────────────────────────────────────────────────────────────────
def inspect(url):
    print(f"── Inspeccionando: {url}")
    html = fetch(url, verbose=True)
    if not html:
        print("  ✗ no cargó (¿403/anti-bot? prueba a guardar la página y usar --from-file)")
        return
    Path("/tmp/quadis_inspect.html").write_text(html, encoding="utf-8")
    print(f"  ✓ {len(html)} bytes (guardado en /tmp/quadis_inspect.html)")
    n_jsonld = len(re.findall(r'application/ld.json', html))
    n_mes = len(re.findall(r'€\s*/?\s*mes', html, re.I))
    precios = sorted(set(re.findall(r'(\d[\d.]{2,5})\s*€', html)))[:8]
    print(f"  · JSON-LD bloques: {n_jsonld}")
    print(f"  · '€/mes' apariciones: {n_mes}  (pocas => catálogo por JS/API)")
    print(f"  · precios ejemplo: {precios}")
    for var in ("__NEXT_DATA__", "__NUXT__", "__INITIAL_STATE__", "window.__DATA__", "self.__next_f"):
        if var in html: print(f"  · estado JS embebido: {var}")

    # contenido del/los JSON-LD (a veces trae el listado)
    for i, m in enumerate(re.finditer(r'application/ld\+json[^>]*>(.*?)</script>', html, re.S)):
        blob = m.group(1).strip()
        print(f"  · JSON-LD[{i}] ({len(blob)}b): {blob[:200]}")

    # posibles endpoints de API en el HTML/JS
    urls = set(re.findall(r'https?://[^\s"\'<>]+', html))
    api = sorted(u for u in urls if re.search(r'(api|graphql|/ofertas|/renting|/vehic|/search|\.json)', u, re.I)
                 and 'quadis' in u.lower())[:20]
    print(f"  · posibles endpoints API (mismo dominio): {len(api)}")
    for u in api: print(f"       {u}")
    ext = sorted(u for u in urls if re.search(r'(api|graphql)', u, re.I) and 'quadis' not in u.lower())[:10]
    if ext:
        print("  · APIs de terceros:")
        for u in ext: print(f"       {u}")
    # scripts de la app (bundles)
    srcs = re.findall(r'<script[^>]+src="([^"]+)"', html)
    print(f"  · <script src> ({len(srcs)}): " + ", ".join(s.split('/')[-1] for s in srcs[:12]))

    offs, strat = parse_listing(html, url)
    print(f"  · ofertas detectadas ('{strat}'): {len(offs)}")
    for o in offs[:8]:
        print(f"     {o['make']} {o['model']} — {o['precio_desde']}€ [{o['tipo']}/{o['category'] or '?'}]")
    if not offs or len(offs) < 4:
        print("\n  ⚠ El catálogo no está en el HTML (carga por API). Necesito la URL de esa API:")
        print("     En Chrome: abre la página → F12 → pestaña 'Red'/'Network' → filtro 'Fetch/XHR'")
        print("     → recarga → busca una petición que devuelva JSON con coches (mira 'Preview').")
        print("     Copia su URL (botón derecho → Copy → Copy link address) y pégamela.")


# ─── SCRAPE ────────────────────────────────────────────────────────────────────
def scrape_all():
    all_offers, tried = [], []
    for path, tipo, cat in LISTINGS:
        seen_pages = set()
        queue = [urljoin(BASE_URL, path)]
        while queue:
            u = queue.pop(0)
            if u in seen_pages or len(seen_pages) > 25:
                continue
            seen_pages.add(u)
            h = fetch(u); tried.append((u, bool(h)))
            if not h:
                continue
            offs, strat = parse_listing(h, u, tipo, cat)
            all_offers += offs
            print(f"  {u} -> {len(offs)} ({strat})")
            for np in sorted(next_pages(h, u)):
                if np not in seen_pages:
                    queue.append(np)
            time.sleep(0.6)
    # dedupe por (tipo, make, model, version, precio)
    uniq = {}
    for o in all_offers:
        uniq[(o["tipo"], o["make"], o["model"], o["version"], o["precio_desde"])] = o
    return list(uniq.values()), tried


def merge_into_manuales(offers):
    data = []
    if MANUALES.exists():
        data = json.loads(MANUALES.read_text(encoding="utf-8"))
    data = [o for o in data if o.get("fuente") != FUENTE]   # quita Quadis anteriores
    data.extend(offers)
    MANUALES.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✓ ofertas-manuales.json: {len(offers)} de {FUENTE} (total {len(data)})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inspect", nargs="?", const=BASE_URL + "/coches-renting/particulares")
    ap.add_argument("--api-dump", nargs="?", const=BASE_URL + "/api-vehicles/coches-renting?page=1&limit=3",
                    help="Descarga y muestra el JSON crudo de la API (para ver los campos)")
    ap.add_argument("--from-file")
    ap.add_argument("--html", action="store_true", help="Fuerza scrape del HTML en vez de la API")
    ap.add_argument("--merge", action="store_true")
    args = ap.parse_args()

    for imp in ("requests", "bs4", "lxml"):
        try: __import__(imp)
        except ImportError:
            print("❌ Falta dependencia:  pip install requests beautifulsoup4 lxml"); sys.exit(1)

    if args.inspect:
        inspect(args.inspect); return

    if args.api_dump is not None:
        h = fetch(args.api_dump, verbose=True)
        if not h:
            print("  ✗ no cargó (403/anti-bot). Abre la URL en tu navegador y pégame el JSON.")
        else:
            try:
                print(json.dumps(json.loads(h), ensure_ascii=False, indent=2)[:4000])
            except Exception:
                print(h[:3000])
        return

    if args.from_file:
        html = Path(args.from_file).read_text(encoding="utf-8")
        offers, strat = parse_listing(html, BASE_URL)
        print(f"  (from-file) {len(offers)} ofertas ({strat})")
    elif args.html:
        print("── Scrapeando quadis.es por HTML…")
        offers, tried = scrape_all()
        for u, ok in tried:
            print(f"    {'✓' if ok else '✗'} {u}")
    else:
        print("── Scrapeando quadis.es por API (api-vehicles)…")
        offers, tried = api_scrape()

    from collections import Counter
    print(f"\n✅ {len(offers)} ofertas de {FUENTE}")
    print("   por segmento: " + " · ".join(f"{k}: {v}" for k, v in Counter(o['tipo'] for o in offers).items()))
    print("   por categoría: " + " · ".join(f"{k or '?'}: {v}" for k, v in Counter(o['category'] for o in offers).items()))
    for o in offers[:12]:
        print(f"   · [{o['tipo'][:4]}] {o['make']} {o['model']} — {o['precio_desde']}€ ({o['duracion']}m/{o['km']}km) [{o['category'] or '?'}]")
    if len(offers) > 12:
        print(f"   … y {len(offers)-12} más")

    OUT_DB.write_text(json.dumps(offers, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n💾 Guardado en {OUT_DB.name}")
    if args.merge:
        merge_into_manuales(offers)
    else:
        print("   (usa --merge para volcarlas a ofertas-manuales.json)")
    if not offers:
        print("\n⚠ 0 ofertas: lanza  python3 scrape_quadis.py --inspect  y pégame la salida.")


if __name__ == "__main__":
    main()
