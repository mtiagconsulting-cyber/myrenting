# -*- coding: utf-8 -*-
"""
CAPA 4 · QA (semáforo antes de publicar).
Devuelve código de salida !=0 si algo está mal -> el orquestador ABORTA y NO publica.
"""
import json, os, sys, glob
REPO="/workspace/myrenting"
errores=[]; avisos=[]

cat_path=f"{REPO}/data/build/catalogo.json"
if not os.path.exists(cat_path):
    print("❌ No existe data/build/catalogo.json (¿corriste build?)"); sys.exit(1)
cat=json.load(open(cat_path,encoding='utf-8'))
mods=cat["modelos"]

# 1. debe haber modelos y ofertas
if cat["n_modelos"]<10: errores.append(f"Solo {cat['n_modelos']} modelos (¿scraping falló?)")
if cat["n_ofertas"]<20: errores.append(f"Solo {cat['n_ofertas']} ofertas (¿scraping vacío?)")

# 2. precios sanos
for k,m in mods.items():
    p=m.get("precio_desde",0)
    if p<=0: errores.append(f"{k}: precio_desde inválido ({p})")
    elif p<80: avisos.append(f"{k}: precio sospechosamente bajo ({p}€)")
    elif p>2500: avisos.append(f"{k}: precio sospechosamente alto ({p}€)")

# 3. imágenes referenciadas existen
faltan_img=0
for k,m in mods.items():
    img=(m.get("specs") or {}).get("imagen","")
    if img.startswith("/"):
        # aceptar .webp o .png
        base=REPO+img
        alt=base.rsplit(".",1)[0]+".webp"
        if not (os.path.exists(base) or os.path.exists(alt)): faltan_img+=1
if faltan_img: avisos.append(f"{faltan_img} modelos con imagen no encontrada en disco")

# 4. cobertura de specs
sin_spec=sum(1 for m in mods.values() if not (m.get("specs") or {}).get("combustible"))
if sin_spec: avisos.append(f"{sin_spec} modelos sin specs (revisar data/master/modelos.json)")

print(f"— QA catálogo: {cat['n_modelos']} modelos, {cat['n_ofertas']} ofertas —")
for a in avisos: print("  ⚠️ ",a)
for e in errores: print("  ❌ ",e)
if errores:
    print(f"\nQA FALLÓ ({len(errores)} errores). NO se publica."); sys.exit(1)
print(f"\n✅ QA OK ({len(avisos)} avisos, 0 errores).")
