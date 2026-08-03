#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORQUESTADOR SEMANAL · myrenting.es
Uso:  python3 run_weekly.py            (todo el ciclo, scrape rápido)
      python3 run_weekly.py --con-matrix   (scrape + matriz km×meses de M Automoción; LENTO ~15 min)
      python3 run_weekly.py --sin-scrape   (salta el scraping, usa data/raw actual)
      python3 run_weekly.py --sin-publicar (genera y valida, pero no hace commit/push)

Orden (para si algo falla):
  1. SCRAPE    -> data/raw/*.json
  2. BUILD     -> data/build/catalogo.json   (merge raw + manuales + specs)
  3. GENERATE  -> HTML (index, landings, sitemap, llms.txt)
  4. QA        -> valida; si falla, ABORTA sin publicar
  5. PUBLICAR  -> commit + push (opcional)
"""
import subprocess, sys, os, datetime
REPO=os.path.dirname(os.path.abspath(__file__))
def paso(nombre, cmd):
    print(f"\n{'='*54}\n▶ {nombre}\n{'='*54}")
    r=subprocess.run(cmd, cwd=REPO)
    if r.returncode!=0:
        print(f"\n🛑 '{nombre}' falló (código {r.returncode}). Se detiene el ciclo. NO se ha publicado nada.")
        sys.exit(r.returncode)

def main():
    args=set(sys.argv[1:])
    print(f"### CICLO SEMANAL myrenting.es · {datetime.datetime.now():%Y-%m-%d %H:%M} ###")
    if "--sin-scrape" not in args:
        scrape_cmd=["python3","scripts/1_scrape/run_scrapers.py"]
        if "--con-matrix" in args: scrape_cmd.append("--con-matrix")
        paso("1/5 SCRAPE", scrape_cmd)
    else:
        print("· (scraping omitido, uso data/raw actual)")
    paso("2/5 BUILD catálogo", ["python3","scripts/2_build/build_catalogo.py"])
    paso("2b/5 ENRICH modelos", ["python3","scripts/2_build/enrich_modelos.py"])
    paso("2c/5 REBUILD catálogo", ["python3","scripts/2_build/build_catalogo.py"])
    paso("3/5 GENERATE home",  ["python3","scripts/3_generate/generar_home.py"])
    paso("3/5 GENERATE resto", ["python3","scripts/3_generate/generar_todo.py"])
    paso("4/5 QA",             ["python3","scripts/4_qa/validar.py"])
    if "--sin-publicar" in args:
        print("\n✅ Ciclo OK (sin publicar). Revisa los cambios y sube a mano cuando quieras.")
        return
    print("\n"+"="*54+"\n▶ 5/5 PUBLICAR\n"+"="*54)
    subprocess.run(["git","add","-A"],cwd=REPO)
    msg=f"Actualización semanal {datetime.date.today():%Y-%m-%d}"
    subprocess.run(["git","commit","-m",msg],cwd=REPO)
    print("Commit hecho. Haz 'git push' cuando quieras publicar (o descomenta el push aquí).")

if __name__=="__main__":
    main()
