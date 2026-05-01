"""
Busca imágenes PNG de coches en Google Images usando Playwright
y genera tarjetas con fondo blanco + logo MiRenting.

Ejecutar: python3 generar_imagenes_google.py
"""

import json, re, time, requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from playwright.sync_api import sync_playwright

BASE    = Path("/Users/matthiasthomassen/Documents/Myrenting")
IMG_DIR = BASE / "img" / "modelos"
IMG_DIR.mkdir(parents=True, exist_ok=True)

W, H         = 800, 480
LOGO_H       = 60
ACCENT_COLOR = (232, 56, 13)
BG_COLOR     = (255, 255, 255)
BANNER_COLOR = (17, 19, 24)

def slug(texto):
    t = texto.lower()
    for a, b in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u'),('ü','u')]:
        t = t.replace(a, b)
    t = re.sub(r'[^a-z0-9]+', '-', t)
    return re.sub(r'-+', '-', t).strip('-')

def get_font(size, bold=False):
    fuentes = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for f in fuentes:
        try:
            return ImageFont.truetype(f, size)
        except:
            pass
    return ImageFont.load_default()

def buscar_imagen_google(page, query):
    """Busca en Google Images y devuelve URL de la primera imagen PNG"""
    try:
        url = f"https://www.google.com/search?q={requests.utils.quote(query)}&tbm=isch&tbs=ic:specific,isc:white,ift:png"
        page.goto(url, timeout=15000)
        page.wait_for_timeout(2000)

        # Aceptar cookies si aparece
        try:
            page.click("button:has-text('Aceptar todo')", timeout=3000)
            page.wait_for_timeout(1000)
        except:
            pass

        # Buscar imágenes en los resultados
        imagenes = page.query_selector_all("img[src^='https']")
        for img in imagenes:
            src = img.get_attribute("src") or ""
            if src.startswith("https://") and "gstatic" not in src and "google" not in src and len(src) > 50:
                return src

        # Alternativa: buscar en los datos de la página
        content = page.content()
        urls = re.findall(r'"(https://[^"]+\.png[^"]*)"', content)
        for u in urls:
            if "car" in u.lower() or any(w in u.lower() for w in ["auto", "vehicle", "coche"]):
                return u

        # Última opción: cualquier imagen grande
        urls2 = re.findall(r'https://[^\s"\']+(?:\.jpg|\.jpeg|\.png|\.webp)', content)
        for u in urls2:
            if "gstatic" not in u and "google" not in u and "favicon" not in u:
                return u

    except Exception as e:
        print(f"    Error búsqueda: {e}")
    return None

def buscar_imagen_bing(page, query):
    """Fallback: buscar en Bing Images"""
    try:
        url = f"https://www.bing.com/images/search?q={requests.utils.quote(query)}&qft=+filterui:photo-transparent"
        page.goto(url, timeout=15000)
        page.wait_for_timeout(2000)

        content = page.content()
        # Bing guarda las URLs en murl
        urls = re.findall(r'"murl":"(https://[^"]+)"', content)
        for u in urls:
            if any(ext in u.lower() for ext in ['.png', '.jpg', '.jpeg', '.webp']):
                return u
    except Exception as e:
        print(f"    Error Bing: {e}")
    return None

def descargar_imagen(url, timeout=10):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        r = requests.get(url, timeout=timeout, headers=headers)
        if r.status_code == 200 and len(r.content) > 2000:
            img = Image.open(BytesIO(r.content)).convert("RGBA")
            return img
    except:
        pass
    return None

def quitar_fondo(img, umbral=235):
    img = img.convert("RGBA")
    data = list(img.getdata())
    nueva = []
    for r, g, b, a in data:
        if r > umbral and g > umbral and b > umbral:
            nueva.append((255, 255, 255, 0))
        else:
            nueva.append((r, g, b, a))
    img.putdata(nueva)
    return img

def generar_tarjeta(make, model, img_coche=None):
    nombre = f"{make.title()} {model.title()}"
    slug_name = slug(f"{make}-{model}")
    output_path = IMG_DIR / f"{slug_name}.png"

    canvas = Image.new("RGBA", (W, H), BG_COLOR + (255,))

    if img_coche:
        img_coche = quitar_fondo(img_coche)
        area_h = H - LOGO_H - 30
        ratio = min((W * 0.88) / img_coche.width, area_h / img_coche.height)
        new_w = int(img_coche.width * ratio)
        new_h = int(img_coche.height * ratio)
        img_coche = img_coche.resize((new_w, new_h), Image.LANCZOS)
        x = (W - new_w) // 2
        y = (H - LOGO_H - new_h) // 2 + 10
        canvas.paste(img_coche, (x, y), img_coche)

    # Banner inferior
    draw = ImageDraw.Draw(canvas)
    banner_y = H - LOGO_H
    draw.rectangle([(0, banner_y), (W, H)], fill=BANNER_COLOR)

    # Punto rojo
    dot_y = banner_y + LOGO_H // 2
    draw.ellipse([(24, dot_y - 6), (36, dot_y + 6)], fill=ACCENT_COLOR)

    # Logo MiRenting
    font_logo = get_font(26, bold=True)
    draw.text((44, dot_y - 14), "MiRenting", font=font_logo, fill=(255, 255, 255))

    # Nombre modelo
    font_model = get_font(16)
    text_w = draw.textlength(nombre, font=font_model) if hasattr(draw, 'textlength') else 200
    draw.text((W - text_w - 20, dot_y - 10), nombre, font=font_model, fill=(160, 160, 170))

    # Línea separadora
    draw.line([(0, banner_y), (W, banner_y)], fill=(40, 40, 50), width=1)

    canvas.convert("RGB").save(output_path, "PNG", optimize=True)
    return output_path

def main():
    # Leer modelos del HTML
    html = (BASE / "index.html").read_text(encoding="utf-8")
    start = html.find("const _OFERTAS = [") + len("const _OFERTAS = ")
    end = html.find("];", start) + 1
    ofertas = json.loads(html[start:end])

    modelos = {}
    for o in ofertas:
        make  = (o.get("make") or "").strip().upper()
        model = (o.get("model") or "").strip().upper()
        if make and model:
            modelos[f"{make}||{model}"] = None

    # Filtrar los que ya tienen imagen generada
    pendientes = []
    for key in modelos:
        make, model = key.split("||")
        slug_name = slug(f"{make}-{model}")
        if not (IMG_DIR / f"{slug_name}.png").exists():
            pendientes.append((make, model))

    print(f"Total modelos: {len(modelos)}")
    print(f"Ya generados: {len(modelos) - len(pendientes)}")
    print(f"Pendientes: {len(pendientes)}")

    if not pendientes:
        print("¡Todo generado!")
        return

    generadas = 0
    errores   = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        for i, (make, model) in enumerate(pendientes):
            nombre = f"{make.title()} {model.title()}"
            print(f"[{i+1}/{len(pendientes)}] {nombre}...", end=" ", flush=True)

            # Buscar imagen
            query = f"{nombre} car PNG transparent background"
            url_img = buscar_imagen_google(page, query)

            if not url_img:
                # Fallback a Bing
                url_img = buscar_imagen_bing(page, query)

            img_coche = None
            if url_img:
                img_coche = descargar_imagen(url_img)

            try:
                generar_tarjeta(make, model, img_coche)
                estado = "✓ con imagen" if img_coche else "✓ sin imagen (solo logo)"
                print(estado)
                generadas += 1
            except Exception as e:
                print(f"✗ {e}")
                errores += 1

            # Pausa para no ser bloqueado
            time.sleep(1.5)

        browser.close()

    print(f"\n{'='*40}")
    print(f"✓ {generadas} tarjetas generadas")
    print(f"✗ {errores} errores")
    print(f"Imágenes en: {IMG_DIR}")

if __name__ == "__main__":
    main()
