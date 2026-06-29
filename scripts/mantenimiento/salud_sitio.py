import requests
from bs4 import BeautifulSoup
import glob
import os
import random
import time

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SITE_URL = "https://myrenting.es"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; MyrentingHealthBot/1.0)"}
TIMEOUT = 15


def check_url(url, session):
    try:
        r = session.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        return r.status_code
    except requests.exceptions.Timeout:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR"


def main():
    session = requests.Session()
    print("=" * 50)
    print("  AUDITORÍA SALUD MYRENTING.ES")
    print("=" * 50)

    # --- PASO 1: Verificar URLs clave ---
    print("\n[1/3] Comprobando URLs...")
    all_pages = glob.glob(os.path.join(BASE_DIR, 'renting-*.html'))
    muestra = random.sample(all_pages, min(60, len(all_pages)))

    urls = [
        f"{SITE_URL}/",
        f"{SITE_URL}/aviso-legal.html",
        f"{SITE_URL}/politica-privacidad.html",
        f"{SITE_URL}/politica-cookies.html",
        f"{SITE_URL}/blog/",
    ] + [f"{SITE_URL}/{os.path.basename(p)}" for p in muestra]

    rotas = []
    ok_count = 0
    for url in urls:
        status = check_url(url, session)
        if status == 200:
            ok_count += 1
        else:
            rotas.append((url, status))
            print(f"  ❌ {status} — {url}")
        time.sleep(0.2)

    print(f"  ✅ {ok_count} OK  |  ❌ {len(rotas)} con error")

    # --- PASO 2: Verificar imágenes ---
    print("\n[2/3] Comprobando imágenes en 20 páginas...")
    muestra_imgs = random.sample(all_pages, min(20, len(all_pages)))
    imgs_rotas = []
    sin_alt = 0

    for page_path in muestra_imgs:
        with open(page_path, encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        page_name = os.path.basename(page_path)

        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '').strip()
            if not alt:
                sin_alt += 1

            if src.startswith('/img/'):
                img_path = os.path.join(BASE_DIR, src.lstrip('/'))
                if not os.path.exists(img_path):
                    imgs_rotas.append((page_name, src))
            elif src.startswith('http'):
                status = check_url(src, session)
                if status != 200:
                    imgs_rotas.append((page_name, f"{src} → {status}"))
                time.sleep(0.1)

    print(f"  ❌ {len(imgs_rotas)} imágenes rotas  |  ⚠️ {sin_alt} sin atributo alt")
    for page, src in imgs_rotas[:10]:
        print(f"     {page}: {src}")

    # --- PASO 3: Verificar estructura HTML ---
    print("\n[3/3] Comprobando estructura de páginas...")
    problemas_estructura = {}

    for page_path in muestra_imgs:
        with open(page_path, encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        page_name = os.path.basename(page_path)
        issues = []

        if not soup.find('nav'):                                         issues.append('sin nav')
        if not soup.find('h1'):                                          issues.append('sin h1')
        if not soup.find('meta', {'name': 'description'}):              issues.append('sin meta description')
        if not soup.find('link', {'rel': 'canonical'}):                 issues.append('sin canonical')
        if not soup.find('footer'):                                      issues.append('sin footer')
        if not soup.find('script', {'type': 'application/ld+json'}):   issues.append('sin schema JSON-LD')

        robots = soup.find('meta', {'name': 'robots'})
        if robots and 'noindex' in (robots.get('content') or ''):
            issues.append('⚠️ noindex activo')

        form = soup.find('form', {'onsubmit': True})
        if not form:
            issues.append('sin formulario')

        if issues:
            problemas_estructura[page_name] = issues

    if problemas_estructura:
        print(f"  {len(problemas_estructura)} páginas con problemas:")
        for page, issues in list(problemas_estructura.items())[:10]:
            print(f"     {page}: {', '.join(issues)}")
    else:
        print("  ✅ Todas las páginas tienen estructura correcta")

    # --- INFORME FINAL ---
    print("\n" + "=" * 50)
    print("  INFORME FINAL")
    print("=" * 50)
    print(f"URLs:       {ok_count} OK  /  {len(rotas)} rotas")
    print(f"Imágenes:   {len(imgs_rotas)} rotas  /  {sin_alt} sin alt")
    print(f"Estructura: {len(problemas_estructura)} páginas con problemas")

    total_issues = len(rotas) + len(imgs_rotas) + len(problemas_estructura)
    if total_issues == 0:
        print("\n✅ El sitio está en perfecto estado.")
    else:
        print(f"\nTotal de issues encontrados: {total_issues}")
        if rotas:
            print("\n🔴 PRIORIDAD ALTA — Links rotos:")
            for url, status in rotas:
                print(f"   {status} → {url}")
        if imgs_rotas:
            print("\n🟡 PRIORIDAD MEDIA — Imágenes rotas:")
            for page, src in imgs_rotas:
                print(f"   {page}: {src}")
        if problemas_estructura:
            print("\n🟢 PRIORIDAD BAJA — Estructura:")
            for page, issues in list(problemas_estructura.items())[:5]:
                print(f"   {page}: {', '.join(issues)}")


if __name__ == '__main__':
    main()
