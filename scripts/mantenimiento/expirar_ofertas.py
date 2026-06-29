import json
import glob
import re
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def load_modelos_activos():
    path = os.path.join(BASE_DIR, 'ofertas_combinadas.json')
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    modelos = set()
    for o in data:
        make = (o.get('make') or '').strip().upper()
        model = (o.get('model') or '').strip().upper()
        if make and model:
            modelos.add((make, model))
    return modelos


def extraer_make_model(content):
    m = re.search(r'<h1[^>]*>Renting\s+<em>(.*?)</em>', content, re.IGNORECASE)
    if m:
        partes = m.group(1).strip().upper().split()
        if len(partes) >= 2:
            return partes[0], ' '.join(partes[1:])
    m = re.search(r'<title>Renting\s+([A-ZÀ-Ü][a-zA-ZÀ-ÿ\-]+)\s+([^|<\n]+)', content)
    if m:
        make = m.group(1).upper()
        model_raw = re.sub(r'\s*(en|desde|por)\s+.*', '', m.group(2), flags=re.IGNORECASE)
        return make, model_raw.strip().upper()
    return None, None


def tiene_oferta_activa(make, model, modelos_activos):
    model_prefix = model[:5] if len(model) >= 5 else model
    for m, mo in modelos_activos:
        if m == make and mo.startswith(model_prefix):
            return True
    return False


AVISO_HTML = '''<div class="sin-ofertas-aviso" style="background:#fff3cd;border:1.5px solid #ffc107;border-radius:10px;padding:14px 18px;margin-bottom:18px;font-size:13px;color:#856404;">
  ⚠️ <strong>Sin ofertas disponibles actualmente</strong> — Este modelo no tiene ofertas activas en este momento. <a href="/" style="color:#856404;font-weight:600;">Ver todas las ofertas disponibles →</a>
</div>
'''


def marcar_expirada(content):
    content = re.sub(
        r'<meta name="robots" content="[^"]*">',
        '<meta name="robots" content="noindex, nofollow">',
        content
    )
    if 'sin-ofertas-aviso' not in content:
        content = re.sub(r'(<div class="precio-box")', AVISO_HTML + r'\1', content, count=1)
    return content


def restaurar_activa(content):
    content = re.sub(
        r'<meta name="robots" content="noindex[^"]*">',
        '<meta name="robots" content="index, follow">',
        content
    )
    content = re.sub(
        r'<div class="sin-ofertas-aviso"[^>]*>.*?</div>\n?',
        '',
        content,
        flags=re.DOTALL
    )
    return content


def main():
    modelos_activos = load_modelos_activos()
    print(f"Modelos activos: {len(modelos_activos)}")

    pages = glob.glob(os.path.join(BASE_DIR, 'renting-*.html'))
    print(f"Páginas a revisar: {len(pages)}")

    reactivadas = expiradas = sin_cambio = sin_modelo = 0

    for path in pages:
        with open(path, encoding='utf-8') as f:
            content = f.read()

        make, model = extraer_make_model(content)
        if not make or not model:
            sin_modelo += 1
            continue

        activa = tiene_oferta_activa(make, model, modelos_activos)
        ya_expirada = 'sin-ofertas-aviso' in content

        if not activa and not ya_expirada:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(marcar_expirada(content))
            expiradas += 1
            print(f"  EXPIRADA: {os.path.basename(path)}")
        elif activa and ya_expirada:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(restaurar_activa(content))
            reactivadas += 1
            print(f"  REACTIVADA: {os.path.basename(path)}")
        else:
            sin_cambio += 1

    print(f"\nResumen: {reactivadas} reactivadas · {expiradas} nuevas expiradas · {sin_cambio} sin cambios · {sin_modelo} sin modelo detectado")


if __name__ == '__main__':
    main()
