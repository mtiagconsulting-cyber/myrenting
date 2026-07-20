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
import argparse, json, re, sys, time, html as _html
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

MARCAS = ["volkswagen","audi","hyundai","seat","cupra","toyota","skoda","honda",
          "mazda","omoda","jaecoo","ebro","geely","lepas","kia","peugeot","citroen",
          "renault","dacia","opel","ford","nissan","bmw","mini","volvo","fiat","mg","byd"]

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
    for mk in MARCAS:
        if re.search(r"\b" + re.escape(mk) + r"\b", t):
            return mk.upper()
    return ""

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

# ─── PARSE (heurístico, 1ª pasada) ───────────────────────────────────────────────
def parse_cards(html, page_url):
    """Extrae ofertas de una página de listado. Heurística: bloques con precio €/mes."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    offers = []
    seen = set()

    # candidatos a "tarjeta": el ancestro más cercano con un precio y un enlace
    price_nodes = soup.find_all(string=re.compile(r"\d[\d.\s]{1,6}\s*€?\s*(?:/|al)?\s*mes", re.I))
    for pn in price_nodes:
        card = pn
        for _ in range(6):
            card = card.parent
            if card is None: break
            if card.name in ("article", "li", "div") and card.find("a", href=True):
                break
        if card is None:
            continue
        txt = clean(card.get_text(" "))
        a = card.find("a", href=True)
        img = card.find("img")
        precio = num(re.search(r"(\d[\d.\s]{1,6})\s*€?\s*(?:/|al)?\s*mes", txt, re.I).group(1))
        make = guess_make(txt)
        # modelo: texto del título/heading dentro de la tarjeta
        h = card.find(["h1","h2","h3","h4"])
        titulo = clean(h.get_text(" ")) if h else txt[:80]
        model = ""
        if make:
            mm = re.search(re.escape(make), titulo, re.I)
            if mm:
                model = clean(titulo[mm.end():]).split("desde")[0][:40]
        url = urljoin(page_url, a["href"]) if a else page_url
        plazo = re.search(r"(\d{2})\s*mes", txt, re.I)
        km = re.search(r"(\d[\d.\s]{2,6})\s*km", txt, re.I)
        key = (make, model, precio)
        if not precio or key in seen:
            continue
        seen.add(key)
        offers.append({
            "fuente": FUENTE,
            "tipo": "particular",
            "make": make or clean(titulo.split()[0]).upper(),
            "model": (model or titulo).upper()[:40].strip(),
            "version": titulo[:120],
            "fuel": guess_fuel(txt),
            "precio_desde": precio,
            "duracion": int(plazo.group(1)) if plazo else 48,
            "km": int(num(km.group(1))) if km else 10000,
            "url": url,
            "category": guess_cat(txt),
            "image": urljoin(page_url, img.get("src") or img.get("data-src") or "") if img else "",
        })
    return offers

def find_and_scrape():
    all_offers = []
    tried = []
    for path in CANDIDATE_PATHS:
        url = urljoin(BASE_URL, path)
        html = fetch(url)
        tried.append((url, bool(html)))
        if not html:
            continue
        offs = parse_cards(html, url)
        if offs:
            print(f"  ✓ {url}: {len(offs)} ofertas")
            all_offers.extend(offs)
        time.sleep(1)
    # dedupe global por (make, model, version)
    uniq = {}
    for o in all_offers:
        uniq[(o["make"], o["model"], o["version"])] = o
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
        offers = parse_cards(html, BASE_URL)
    else:
        print("── Scrapeando m-renting.com…")
        offers, tried = find_and_scrape()
        for u, ok in tried:
            print(f"    {'✓' if ok else '✗'} {u}")

    print(f"\n✅ {len(offers)} ofertas extraídas de {FUENTE}")
    for o in offers[:8]:
        print(f"   · {o['make']} {o['model']} — {o['precio_desde']}€/mes ({o['duracion']}m/{o['km']}km) [{o['category'] or '?'}]")
    if len(offers) > 8:
        print(f"   … y {len(offers)-8} más")

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
