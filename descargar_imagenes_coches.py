#!/usr/bin/env python3
"""
descargar_imagenes_coches.py
============================
Descarga imágenes PNG sin fondo de todos los modelos de renting y las guarda
en img/modelos/<make>-<model>.png listas para usar en las tarjetas.

USO:
    pip install rembg pillow requests duckduckgo-search onnxruntime
    python3 descargar_imagenes_coches.py

Opciones:
    --solo-faltantes   Solo procesa los 49 modelos sin imagen (más rápido)
    --solo-fondos      Solo elimina fondos de los PNGs existentes (no descarga)
    --modelo "BMW X3"  Procesa un único modelo
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
BASE      = Path(__file__).parent
IMG_DIR   = BASE / "img" / "modelos"
JSON_PATH = BASE / "ofertas-db.json"
IMG_DIR.mkdir(parents=True, exist_ok=True)

# Búsqueda alternativa: términos para encontrar fotos de prensa con fondo transparente
SEARCH_SUFFIXES = [
    "PNG transparent background press photo",
    "official press image cutout white background",
    "PNG no background studio",
]

# Mínimo de píxeles del lado corto para aceptar una imagen
MIN_SIZE = 400

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def slugify(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def tiene_fondo_transparente(img) -> bool:
    """Devuelve True si la imagen ya tiene canal alfa con píxeles transparentes."""
    if img.mode not in ("RGBA", "LA"):
        return False
    import numpy as np
    arr = np.array(img)
    alpha = arr[:, :, 3] if arr.ndim == 3 else arr[:, 1]
    return bool((alpha < 240).sum() > 500)


def quitar_fondo(img_bytes: bytes) -> bytes:
    """Elimina el fondo con rembg y devuelve PNG bytes."""
    from rembg import remove
    out = remove(img_bytes)
    return out


def recortar_y_centrar(img_bytes: bytes, size: tuple = (800, 500)) -> bytes:
    """Recorta el espacio vacío alrededor del coche y ajusta el canvas."""
    from PIL import Image
    import numpy as np

    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    arr = np.array(img)
    alpha = arr[:, :, 3]
    rows = np.any(alpha > 10, axis=1)
    cols = np.any(alpha > 10, axis=0)
    if not rows.any():
        return img_bytes
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]

    # Añadir margen del 8%
    h, w = arr.shape[:2]
    margin_y = max(20, int((rmax - rmin) * 0.08))
    margin_x = max(20, int((cmax - cmin) * 0.08))
    rmin = max(0, rmin - margin_y)
    rmax = min(h - 1, rmax + margin_y)
    cmin = max(0, cmin - margin_x)
    cmax = min(w - 1, cmax + margin_x)

    cropped = img.crop((cmin, rmin, cmax + 1, rmax + 1))

    # Pegar centrado en canvas transparente
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    scale = min(size[0] / cropped.width, size[1] / cropped.height) * 0.88
    new_w = int(cropped.width * scale)
    new_h = int(cropped.height * scale)
    resized = cropped.resize((new_w, new_h), Image.LANCZOS)
    x = (size[0] - new_w) // 2
    y = (size[1] - new_h) // 2
    canvas.paste(resized, (x, y), resized)

    buf = io.BytesIO()
    canvas.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def buscar_imagen_duckduckgo(query: str, max_results: int = 8):
    """Devuelve lista de URLs de imágenes para la query dada."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.images(
                query,
                max_results=max_results,
                size="Large",
                type_image="photo",
            ))
        return [r["image"] for r in results if r.get("image")]
    except Exception as e:
        print(f"    ⚠ DuckDuckGo error: {e}")
        return []


def descargar_url(url: str, timeout: int = 15) -> bytes | None:
    """Descarga una URL y devuelve bytes o None."""
    import requests
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    }
    try:
        r = requests.get(url, headers=headers, timeout=timeout, stream=True)
        if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
            content = b""
            for chunk in r.iter_content(8192):
                content += chunk
                if len(content) > 10_000_000:  # 10 MB max
                    break
            return content
    except Exception:
        pass
    return None


def es_imagen_valida(img_bytes: bytes) -> bool:
    """Comprueba que los bytes son una imagen usable."""
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(img_bytes))
        return min(img.size) >= MIN_SIZE
    except Exception:
        return False


# ─── LÓGICA PRINCIPAL ─────────────────────────────────────────────────────────
def procesar_png_existente(path: Path) -> bool:
    """Elimina el fondo de un PNG existente si aún no es transparente."""
    from PIL import Image

    try:
        img = Image.open(path)
        if tiene_fondo_transparente(img):
            print(f"  ✓ {path.name} — ya transparente, sin cambios")
            return True

        raw = path.read_bytes()
        out = quitar_fondo(raw)
        final = recortar_y_centrar(out)
        path.write_bytes(final)
        print(f"  ✂ {path.name} — fondo eliminado")
        return True
    except Exception as e:
        print(f"  ✗ {path.name} — error: {e}")
        return False


def descargar_modelo(make: str, model: str, slug: str) -> bool:
    """Busca, descarga y procesa la imagen de un modelo."""
    dest = IMG_DIR / f"{slug}.png"
    if dest.exists():
        print(f"  ✓ {slug}.png ya existe")
        return True

    # Construir query de búsqueda limpia
    make_clean = re.sub(r"[^a-zA-Z0-9 ]", " ", make).strip()
    model_clean = re.sub(r"[^a-zA-Z0-9 ]", " ", model).strip()
    base_query = f"{make_clean} {model_clean}"

    for suffix in SEARCH_SUFFIXES:
        query = f"{base_query} {suffix}"
        print(f"  🔍 Buscando: {query[:80]}")
        urls = buscar_imagen_duckduckgo(query, max_results=6)

        for url in urls:
            print(f"      ↳ {url[:90]}")
            raw = descargar_url(url)
            if not raw or not es_imagen_valida(raw):
                continue

            try:
                out = quitar_fondo(raw)
                final = recortar_y_centrar(out)
                dest.write_bytes(final)
                print(f"  ✅ Guardado: {slug}.png")
                return True
            except Exception as e:
                print(f"      ⚠ Error procesando: {e}")
                continue

        time.sleep(1.5)  # respetar rate-limit de DuckDuckGo

    print(f"  ❌ No se encontró imagen para {make} {model}")
    return False


# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solo-faltantes", action="store_true")
    parser.add_argument("--solo-fondos",    action="store_true")
    parser.add_argument("--modelo",         type=str, default=None,
                        help='Ej: "BMW X3"')
    args = parser.parse_args()

    # Verificar dependencias
    missing = []
    for pkg in ["rembg", "PIL", "requests", "duckduckgo_search"]:
        try:
            __import__(pkg if pkg != "PIL" else "PIL.Image")
        except ImportError:
            missing.append(pkg if pkg != "PIL" else "Pillow")
    if missing:
        print("❌ Faltan dependencias. Instálalas con:")
        print(f"   pip install {' '.join(missing)} onnxruntime")
        sys.exit(1)

    # Cargar base de datos
    with open(JSON_PATH, encoding="utf-8") as f:
        raw_data = json.load(f)

    modelos_db = {}
    for o in raw_data:
        if o.get("make") and o.get("model"):
            key = f"{o['make']}||{o['model']}"
            if key not in modelos_db:
                modelos_db[key] = (o["make"], o["model"])

    existing_slugs = {p.stem for p in IMG_DIR.glob("*.png")}

    # ── Modo: modelo individual ──
    if args.modelo:
        parts = args.modelo.strip().split(" ", 1)
        if len(parts) < 2:
            print("Usa: --modelo 'MAKE MODEL'")
            sys.exit(1)
        make, model = parts
        slug = slugify(f"{make} {model}")
        print(f"\n── Procesando: {make} {model} → {slug}.png")
        descargar_modelo(make, model, slug)
        return

    # ── Modo: solo eliminar fondos en PNGs existentes ──
    if args.solo_fondos:
        print(f"\n── Eliminando fondos en {len(list(IMG_DIR.glob('*.png')))} PNGs existentes...\n")
        ok = err = 0
        for p in sorted(IMG_DIR.glob("*.png")):
            if procesar_png_existente(p):
                ok += 1
            else:
                err += 1
        print(f"\n✅ {ok} OK  ❌ {err} errores")
        return

    # ── Modo: descargar faltantes ──
    faltantes = []
    for (make, model) in modelos_db.values():
        slug = slugify(f"{make} {model}")
        if slug not in existing_slugs and not any(k.startswith(slug) for k in existing_slugs):
            faltantes.append((make, model, slug))

    # Deduplicar por slug
    seen = set()
    faltantes_uniq = []
    for item in faltantes:
        if item[2] not in seen:
            seen.add(item[2])
            faltantes_uniq.append(item)

    if args.solo_faltantes or True:
        print(f"\n── Descargando imágenes para {len(faltantes_uniq)} modelos sin imagen...\n")
        ok = err = 0
        for i, (make, model, slug) in enumerate(faltantes_uniq, 1):
            print(f"[{i}/{len(faltantes_uniq)}] {make} {model}")
            if descargar_modelo(make, model, slug):
                ok += 1
            else:
                err += 1
            print()

        print(f"\n✅ {ok} descargados  ❌ {err} sin imagen")

    if not args.solo_faltantes:
        print(f"\n── Procesando fondos de los PNGs existentes...\n")
        ok = err = 0
        for p in sorted(IMG_DIR.glob("*.png")):
            if procesar_png_existente(p):
                ok += 1
            else:
                err += 1
        print(f"\n✅ {ok} OK  ❌ {err} errores")


if __name__ == "__main__":
    main()
