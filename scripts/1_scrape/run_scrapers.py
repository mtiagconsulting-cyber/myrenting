# -*- coding: utf-8 -*-
"""
CAPA 1 · SCRAPING
Ejecuta los scrapers de cada fuente y deja el resultado crudo en data/raw/.
Los scrapers reales viven en la raíz del repo.
Este wrapper los llama; si uno falla, conserva el data/raw anterior (no lo borra a medias).

Fuentes:
  - Marcos Renting Stock -> scrape_marcos_stock.py -> mautomocion-db.json -> data/raw/mautomocion.json
  - Quadis        -> NO se scrapea. Las ofertas de Quadis vienen del PDF de precios,
                     ya cargadas a mano en data/master/ofertas-manuales.json.
  - Kia Renting   -> (manual, en data/master/ofertas-manuales.json)

Nota: cada scraper escribe su propio "<fuente>-db.json" en la raíz; este wrapper
lo copia a data/raw/ (lo único que lee build_catalogo.py). Así el scrape de
M Automoción llega de verdad al catálogo y a la web.
"""
import subprocess, sys, os, shutil, datetime
import pathlib as _pl; REPO=str(_pl.Path(__file__).resolve().parents[2])
RAW=f"{REPO}/data/raw"

# La landing comisionable incluye la matriz km×meses dentro de cada ficha. Se
# extrae siempre para que el configurador de Myrenting muestre precios reales.
_marcos_cmd = ["python3", f"{REPO}/scrape_marcos_stock.py"]

# (nombre, comando, fichero-db que produce el scraper, salida en data/raw)
# Quadis NO va aquí: sus ofertas son manuales (PDF) en data/master/ofertas-manuales.json.
SCRAPERS=[
  ("Marcos Renting Stock", _marcos_cmd, f"{REPO}/mautomocion-db.json", f"{RAW}/mautomocion.json"),
]

def run():
    os.makedirs(RAW,exist_ok=True)
    ok=True
    for nombre,cmd,db_src,salida in SCRAPERS:
        if not os.path.exists(cmd[1]):
            print(f"  ⏭️  {nombre}: scraper no encontrado ({cmd[1]}), se conserva data/raw anterior"); continue
        bak=salida+".bak"
        if os.path.exists(salida): shutil.copy(salida,bak)
        print(f"  ▶️  {nombre}...")
        r=subprocess.run(cmd,cwd=REPO)
        if r.returncode==0 and os.path.exists(db_src):
            shutil.copy(db_src,salida)
            print(f"  ✅ {nombre} -> {os.path.basename(salida)}")
            if os.path.exists(bak): os.remove(bak)
        else:
            print(f"  ❌ {nombre} falló (rc={r.returncode}, db={'ok' if os.path.exists(db_src) else 'no generado'}); restauro copia previa")
            if os.path.exists(bak): shutil.move(bak,salida)
            ok=False
    return ok

if __name__=="__main__":
    print("== CAPA 1: SCRAPING ==",datetime.date.today())
    sys.exit(0 if run() else 1)
