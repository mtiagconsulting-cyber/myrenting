# -*- coding: utf-8 -*-
"""
CAPA 1 · SCRAPING
Ejecuta los scrapers de cada fuente y deja el resultado crudo en data/raw/.
Los scrapers reales viven en la raíz / scripts/scrapers/ (en tu Mac).
Este wrapper los llama; si uno falla, conserva el data/raw anterior (no lo borra a medias).

Fuentes:
  - M Automoción  -> scrape_mautomocion.py  -> data/raw/mautomocion.json
  - Quadis        -> scrape_quadis.py       -> data/raw/quadis.json
  - Kia Renting   -> (manual, en data/master/ofertas-manuales.json)
"""
import subprocess, sys, os, shutil, datetime
REPO="/workspace/myrenting"
RAW=f"{REPO}/data/raw"

SCRAPERS=[
  ("M Automoción", ["python3", f"{REPO}/scrape_mautomocion.py"], f"{RAW}/mautomocion.json"),
  ("Quadis",       ["python3", f"{REPO}/scrape_quadis.py"],       f"{RAW}/quadis.json"),
]

def run():
    os.makedirs(RAW,exist_ok=True)
    ok=True
    for nombre,cmd,salida in SCRAPERS:
        if not os.path.exists(cmd[1]):
            print(f"  ⏭️  {nombre}: scraper no encontrado ({cmd[1]}), se conserva data/raw anterior"); continue
        bak=salida+".bak"
        if os.path.exists(salida): shutil.copy(salida,bak)
        print(f"  ▶️  {nombre}...")
        r=subprocess.run(cmd,cwd=REPO)
        if r.returncode!=0:
            print(f"  ❌ {nombre} falló; restauro copia previa")
            if os.path.exists(bak): shutil.move(bak,salida)
            ok=False
        else:
            print(f"  ✅ {nombre} -> {os.path.basename(salida)}")
            if os.path.exists(bak): os.remove(bak)
    return ok

if __name__=="__main__":
    print("== CAPA 1: SCRAPING ==",datetime.date.today())
    sys.exit(0 if run() else 1)
