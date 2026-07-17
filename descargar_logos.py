#!/usr/bin/env python3
"""
descargar_logos.py
==================
Descarga los LOGOS de las gestoras (Arval, Ayvens, Alphabet, Kinto, Quadis,
KIA Armotors, Leasys, Revel...) y los SÍMBOLOS de las marcas de coche
(Audi, BMW, Tesla, BYD...) listos para usar en las tarjetas de la web.

  · Logos de gestoras  →  img/gestoras/<fuente>.png   (ej: arval.png)
  · Símbolos de marca  →  img/marcas/<marca>.png       (ej: bmw.png)

Las tarjetas de la web ya usan estos ficheros automáticamente si existen,
y si no, muestran las iniciales de color como fallback. No rompe nada.

USO (en tu Mac, que sí tiene internet):
    pip install requests pillow duckduckgo-search
    # opcional, para recortar fondos blancos con IA:
    pip install rembg onnxruntime

    python3 descargar_logos.py                 # descarga todo lo que falte
    python3 descargar_logos.py --solo gestoras # solo logos de gestoras
    python3 descargar_logos.py --solo marcas   # solo símbolos de marca
    python3 descargar_logos.py --forzar        # vuelve a bajar aunque exista
    python3 descargar_logos.py --quitar-fondo  # convierte fondo blanco a transparente
    python3 descargar_logos.py --marca BMW     # una sola marca
    python3 descargar_logos.py --gestora Arval # una sola gestora

Fuentes usadas (con fallback en cascada):
    Marcas   : car-logos-dataset (GitHub) → Wikimedia → DuckDuckGo imágenes
    Gestoras : Clearbit Logo API          → DuckDuckGo imágenes
"""

import argparse
import io
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

# ─── CONFIG ──────────────────────────────────────────────────────────────────
BASE          = Path(__file__).parent
DIR_GESTORAS  = BASE / "img" / "gestoras"
DIR_MARCAS    = BASE / "img" / "marcas"
JSON_PATH     = BASE / "ofertas-db.json"          # fuente de marcas
INDEX_PATH    = BASE / "index.html"               # fallback de marcas
MIN_SIZE      = 48                                # lado corto mínimo aceptable (px)

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/120.0.0.0 Safari/537.36"),
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
}

# ─── GESTORAS ────────────────────────────────────────────────────────────────
# slug de fichero  →  (nombre para buscar, dominio para Clearbit)
GESTORAS = {
    "arval":        ("Arval",        "arval.es"),
    "ayvens":       ("Ayvens",       "ayvens.com"),
    "alphabet":     ("Alphabet",     "alphabet.com"),
    "kinto":        ("Kinto",        "kinto-mobility.es"),
    "quadis":       ("Quadis",       "quadis.es"),
    "kia-armotors": ("KIA Armotors", "armotors.es"),
    "leasys":       ("Leasys",       "leasys.com"),
    "revel":        ("Revel",        "revel.es"),
}

# ─── MARCAS ──────────────────────────────────────────────────────────────────
# Normaliza las distintas grafías de _OFERTAS a un slug canónico.
MARCA_ALIAS = {
    "alfa romeo": "alfa-romeo", "alfa-romeo": "alfa-romeo",
    "citroen": "citroen", "citroën": "citroen",
    "mercedes": "mercedes-benz", "mercedes benz": "mercedes-benz",
    "mercedes-benz": "mercedes-benz",
    "land rover": "land-rover",
    "lynk and co": "lynk-co", "lynk & co": "lynk-co", "lynk co": "lynk-co",
    "ds": "ds", "mg": "mg",
}

# Slug del repositorio car-logos-dataset (a veces difiere del nuestro)
DATASET_SLUG = {
    "mercedes": "mercedes-benz", "mercedes-benz": "mercedes-benz",
    "alfa-romeo": "alfa-romeo", "land-rover": "land-rover", "citroen": "citroen",
    "ds": "ds-automobiles", "lynk-and-co": "lynk-co",
    "byd": "byd", "cupra": "cupra", "polestar": "polestar",
}
DATASET_URL = ("https://raw.githubusercontent.com/filippofilip95/"
               "car-logos-dataset/master/logos/optimized/{slug}.png")

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def slugify(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def marca_slug(make: str) -> str:
    # Mismo slug que usa la web (slugify plano) para que los PNG coincidan
    # con las rutas /img/marcas/<slug>.png de las tarjetas y el buscador.
    return slugify(make)


def descargar_url(url: str, timeout: int = 20) -> bytes | None:
    import requests
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, stream=True)
        ctype = r.headers.get("content-type", "")
        if r.status_code == 200 and ("image" in ctype or url.lower().endswith(".png")):
            content = b""
            for chunk in r.iter_content(8192):
                content += chunk
                if len(content) > 8_000_000:      # 8 MB máx
                    break
            return content
    except Exception:
        pass
    return None


def es_imagen_valida(img_bytes: bytes) -> bool:
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(img_bytes))
        img.verify()
        img = Image.open(io.BytesIO(img_bytes))
        return min(img.size) >= MIN_SIZE
    except Exception:
        return False


def buscar_duckduckgo(query: str, max_results: int = 8):
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            res = list(ddgs.images(query, max_results=max_results,
                                   type_image="transparent"))
        urls = [r["image"] for r in res if r.get("image")]
        # segunda pasada sin filtro por si transparent devuelve poco
        if len(urls) < 3:
            with DDGS() as ddgs:
                res = list(ddgs.images(query, max_results=max_results))
            urls += [r["image"] for r in res if r.get("image")]
        return urls
    except Exception as e:
        print(f"    ⚠ DuckDuckGo error: {e}")
        return []


def fondo_blanco_a_transparente(img_bytes: bytes) -> bytes:
    """Convierte píxeles casi-blancos del borde en transparentes (logos con
    fondo blanco). Ligero y sin dependencias de IA."""
    from PIL import Image
    import numpy as np
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    arr = np.array(img).astype(np.int16)
    r, g, b, a = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]
    blanco = (r > 240) & (g > 240) & (b > 240)
    arr[..., 3] = np.where(blanco, 0, a)
    out = Image.fromarray(arr.astype("uint8"), "RGBA")
    buf = io.BytesIO()
    out.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def quitar_fondo_rembg(img_bytes: bytes) -> bytes:
    from rembg import remove
    return remove(img_bytes)


def recortar_transparente(img_bytes: bytes, pad: int = 12) -> bytes:
    """Recorta el margen transparente sobrante alrededor del logo."""
    from PIL import Image
    import numpy as np
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    arr = np.array(img)
    alpha = arr[..., 3]
    rows = np.any(alpha > 15, axis=1)
    cols = np.any(alpha > 15, axis=0)
    if not rows.any() or not cols.any():
        return img_bytes
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    h, w = arr.shape[:2]
    rmin, rmax = max(0, rmin - pad), min(h - 1, rmax + pad)
    cmin, cmax = max(0, cmin - pad), min(w - 1, cmax + pad)
    cropped = img.crop((cmin, rmin, cmax + 1, rmax + 1))
    buf = io.BytesIO()
    cropped.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def guardar_png(img_bytes: bytes, dest: Path, quitar_fondo: bool) -> None:
    from PIL import Image
    if quitar_fondo:
        try:
            try:
                import rembg  # noqa: F401
                img_bytes = quitar_fondo_rembg(img_bytes)
            except ImportError:
                img_bytes = fondo_blanco_a_transparente(img_bytes)
            img_bytes = recortar_transparente(img_bytes)
        except Exception as e:
            print(f"      ⚠ no se pudo limpiar el fondo: {e}")
    # normalizar a PNG siempre
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode not in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, format="PNG", optimize=True)


# ─── DESCARGA POR ELEMENTO ─────────────────────────────────────────────────────
def procesar(dest: Path, urls, label: str, quitar_fondo: bool, forzar: bool) -> bool:
    if dest.exists() and not forzar:
        print(f"  ✓ {dest.name} ya existe")
        return True
    for url in urls:
        if not url:
            continue
        print(f"      ↳ {url[:90]}")
        raw = descargar_url(url)
        if not raw or not es_imagen_valida(raw):
            continue
        try:
            guardar_png(raw, dest, quitar_fondo)
            print(f"  ✅ Guardado: {dest.name}")
            return True
        except Exception as e:
            print(f"      ⚠ error procesando: {e}")
            continue
    print(f"  ❌ No se encontró logo para {label}")
    return False


def urls_marca(slug: str, make: str):
    """Cascada de fuentes para el símbolo de una marca."""
    ds = DATASET_SLUG.get(slug, slug)
    urls = [DATASET_URL.format(slug=ds)]
    if ds != slug:
        urls.append(DATASET_URL.format(slug=slug))
    # DuckDuckGo como fallback
    urls += buscar_duckduckgo(f"{make} car logo emblem png transparent", 6)
    return urls


def urls_gestora(nombre: str, dominio: str):
    urls = [f"https://logo.clearbit.com/{dominio}?size=256&format=png"]
    urls += buscar_duckduckgo(f"{nombre} renting logo png transparent", 6)
    return urls


# ─── CARGA DE MARCAS ───────────────────────────────────────────────────────────
def cargar_marcas() -> dict:
    """Devuelve {slug: make_legible} a partir de ofertas-db.json o index.html."""
    makes = set()
    if JSON_PATH.exists():
        try:
            data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
            for o in data:
                if o.get("make"):
                    makes.add(o["make"].strip())
        except Exception as e:
            print(f"⚠ No se pudo leer {JSON_PATH.name}: {e}")
    if not makes and INDEX_PATH.exists():
        html = INDEX_PATH.read_text(encoding="utf-8")
        for m in re.findall(r'"make"\s*:\s*"([^"]+)"', html):
            makes.add(m.strip())
    out = {}
    for m in sorted(makes):
        out.setdefault(marca_slug(m), m)   # primera grafía gana como etiqueta
    return out


# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--solo", choices=["gestoras", "marcas"], default=None)
    ap.add_argument("--marca", type=str, default=None, help='Ej: "BMW"')
    ap.add_argument("--gestora", type=str, default=None, help='Ej: "Arval"')
    ap.add_argument("--quitar-fondo", action="store_true",
                    help="Convierte el fondo blanco en transparente")
    ap.add_argument("--forzar", action="store_true",
                    help="Vuelve a descargar aunque el fichero ya exista")
    args = ap.parse_args()

    # dependencias mínimas
    faltan = []
    for pkg, imp in [("requests", "requests"), ("Pillow", "PIL.Image"),
                     ("duckduckgo-search", "duckduckgo_search")]:
        try:
            __import__(imp)
        except ImportError:
            faltan.append(pkg)
    if faltan:
        print("❌ Faltan dependencias. Instálalas con:")
        print(f"   pip install {' '.join(faltan)}")
        print("   (opcional, mejor recorte de fondos: pip install rembg onnxruntime)")
        sys.exit(1)

    qf = args.quitar_fondo

    # ── una sola marca ──
    if args.marca:
        slug = marca_slug(args.marca)
        print(f"\n── Marca: {args.marca} → img/marcas/{slug}.png")
        procesar(DIR_MARCAS / f"{slug}.png",
                 urls_marca(slug, args.marca), args.marca, qf, args.forzar)
        return

    # ── una sola gestora ──
    if args.gestora:
        slug = slugify(args.gestora)
        nombre, dominio = GESTORAS.get(slug, (args.gestora, f"{slug}.com"))
        print(f"\n── Gestora: {nombre} → img/gestoras/{slug}.png")
        procesar(DIR_GESTORAS / f"{slug}.png",
                 urls_gestora(nombre, dominio), nombre, qf, args.forzar)
        return

    # ── gestoras ──
    if args.solo in (None, "gestoras"):
        print(f"\n── Logos de gestoras ({len(GESTORAS)})\n")
        ok = err = 0
        for slug, (nombre, dominio) in GESTORAS.items():
            print(f"• {nombre}")
            if procesar(DIR_GESTORAS / f"{slug}.png",
                        urls_gestora(nombre, dominio), nombre, qf, args.forzar):
                ok += 1
            else:
                err += 1
            time.sleep(1.0)
        print(f"\n  gestoras → ✅ {ok}  ❌ {err}")

    # ── marcas ──
    if args.solo in (None, "marcas"):
        marcas = cargar_marcas()
        print(f"\n── Símbolos de marca ({len(marcas)})\n")
        ok = err = 0
        for slug, make in marcas.items():
            print(f"• {make}  ({slug})")
            if procesar(DIR_MARCAS / f"{slug}.png",
                        urls_marca(slug, make), make, qf, args.forzar):
                ok += 1
            else:
                err += 1
            time.sleep(0.8)
        print(f"\n  marcas → ✅ {ok}  ❌ {err}")

    print("\n✔ Listo. Sube los PNG con:  git add img/gestoras img/marcas && git commit && git push")


if __name__ == "__main__":
    main()
