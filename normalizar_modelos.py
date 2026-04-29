"""
Normaliza make/model en el index.html para que sean comparables entre gestoras.
Problema: Arval/Alphabet meten marca+modelo en 'make' y dejan 'model' vacío o con datos raros.
Solución: separar correctamente y normalizar capitalización.

Ejecutar: python3 normalizar_modelos.py
"""

import json, re, shutil
from datetime import datetime
from pathlib import Path

BASE = Path("/Users/matthiasthomassen/Documents/Myrenting")
HTML_PATH = BASE / "index.html"
BACKUP_PATH = BASE / f"index_backup_norm_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

# Mapa de normalización: clave = lo que aparece en make (uppercase), valor = (make_correcto, model_correcto)
# Casos donde make contiene modelo embebido
MAKE_CORRECTIONS = {
    # Alpine
    "ALPINE A290": ("ALPINE", "A290"),
    # Audi
    "AUDI A1": ("AUDI", "A1"),
    "AUDI A3": ("AUDI", "A3"),
    "AUDI A4": ("AUDI", "A4"),
    "AUDI Q3": ("AUDI", "Q3"),
    "AUDI Q5": ("AUDI", "Q5"),
    "AUDI Q8": ("AUDI", "Q8"),
    # BMW
    "BMW I4": ("BMW", "i4"),
    "BMW IX1": ("BMW", "iX1"),
    "BMW IX3": ("BMW", "iX3"),
    "BMW SERIE 1": ("BMW", "Serie 1"),
    "BMW SERIE 2": ("BMW", "Serie 2"),
    "BMW SERIE 3": ("BMW", "Serie 3"),
    "BMW SERIE 5": ("BMW", "Serie 5"),
    "BMW X1": ("BMW", "X1"),
    "BMW X2": ("BMW", "X2"),
    "BMW X3": ("BMW", "X3"),
    "BMW X3 20D XDRIVE": ("BMW", "X3"),
    "BMW X4": ("BMW", "X4"),
    "BMW X5": ("BMW", "X5"),
    # BYD
    "BYD ATTO 2": ("BYD", "ATTO 2"),
    "BYD ATTO 2 DMI ACTIVE 122KW 166 CV": ("BYD", "ATTO 2"),
    "BYD DOLPHIN SURF": ("BYD", "DOLPHIN SURF"),
    "BYD SEAL U": ("BYD", "SEAL U"),
    # Cupra
    "CUPRA FORMENTOR": ("CUPRA", "FORMENTOR"),
    "CUPRA TERRAMAR": ("CUPRA", "TERRAMAR"),
    # Dacia
    "DACIA SANDERO": ("DACIA", "SANDERO"),
    # Fiat
    "FIAT 500": ("FIAT", "500"),
    "FIAT DOBLÓ": ("FIAT", "DOBLO"),
    "FIAT SCUDO": ("FIAT", "SCUDO"),
    "FIAT DUCATO": ("FIAT", "DUCATO"),
    # Ford
    "FORD PUMA / 5P / TODOTERRENO": ("FORD", "PUMA"),
    "FORD RANGER": ("FORD", "RANGER"),
    # Honda
    "HONDA CR-V": ("HONDA", "CR-V"),
    "HONDA ZR-V": ("HONDA", "ZR-V"),
    # Hyundai
    "HYUNDAI BAYON": ("HYUNDAI", "BAYON"),
    "HYUNDAI I20": ("HYUNDAI", "I20"),
    "HYUNDAI IONIQ 5": ("HYUNDAI", "IONIQ 5"),
    "HYUNDAI KONA": ("HYUNDAI", "KONA"),
    "HYUNDAI TUCSON": ("HYUNDAI", "TUCSON"),
    # Jaecoo
    "JAECOO 7": ("JAECOO", "7"),
    # Kia
    "KIA EV3": ("KIA", "EV3"),
    "KIA EV6": ("KIA", "EV6"),
    "KIA NIRO": ("KIA", "NIRO"),
    "KIA SPORTAGE": ("KIA", "SPORTAGE"),
    "KIA STONIC": ("KIA", "STONIC"),
    "KIA XCEED": ("KIA", "XCEED"),
    # Land Rover
    "LAND ROVER DEFENDER": ("LAND ROVER", "DEFENDER"),
    "LAND ROVER RANGE ROVER EVOQUE": ("LAND ROVER", "RANGE ROVER EVOQUE"),
    "LAND ROVER SPORT": ("LAND ROVER", "RANGE ROVER SPORT"),
    # Mazda
    "MAZDA CX-60": ("MAZDA", "CX-60"),
    # Mercedes
    "MERCEDES BENZ CITAN FURGON": ("MERCEDES BENZ", "CITAN FURGON"),
    "MERCEDES BENZ CITAN TOURER": ("MERCEDES BENZ", "CITAN TOURER"),
    "MERCEDES BENZ CLASE A": ("MERCEDES BENZ", "CLASE A"),
    "MERCEDES BENZ GLA": ("MERCEDES BENZ", "GLA"),
    "MERCEDES BENZ SPRINTER": ("MERCEDES BENZ", "SPRINTER"),
    "MERCEDES BENZ VITO": ("MERCEDES BENZ", "VITO"),
    # MG
    "MG HS": ("MG", "HS"),
    "MG ZS": ("MG", "ZS"),
    # Omoda
    "OMODA 5": ("OMODA", "5"),
    "OMODA 9": ("OMODA", "9"),
    # Peugeot
    "PEUGEOT 2008": ("PEUGEOT", "2008"),
    "PEUGEOT 208": ("PEUGEOT", "208"),
    "PEUGEOT 3008": ("PEUGEOT", "3008"),
    "PEUGEOT 308": ("PEUGEOT", "308"),
    # Polestar
    "POLESTAR 4": ("POLESTAR", "4"),
    # Renault
    "RENAULT CLIO": ("RENAULT", "CLIO"),
    "RENAULT ESPACE": ("RENAULT", "ESPACE"),
    "RENAULT KANGOO": ("RENAULT", "KANGOO"),
    "RENAULT MASTER": ("RENAULT", "MASTER"),
    "RENAULT RAFALE": ("RENAULT", "RAFALE"),
    "RENAULT SYMBIOZ": ("RENAULT", "SYMBIOZ"),
    "RENAULT TRAFIC": ("RENAULT", "TRAFIC"),
    # Seat
    "SEAT ARONA": ("SEAT", "ARONA"),
    "SEAT IBIZA": ("SEAT", "IBIZA"),
    "SEAT LEON": ("SEAT", "LEON"),
    # Skoda
    "SKODA FABIA": ("SKODA", "FABIA"),
    "SKODA KAROQ": ("SKODA", "KAROQ"),
    "SKODA KODIAQ": ("SKODA", "KODIAQ"),
    "SKODA OCTAVIA": ("SKODA", "OCTAVIA"),
    # Tesla
    "TESLA 3": ("TESLA", "MODEL 3"),
    # Volkswagen
    "VOLKSWAGEN GOLF": ("VOLKSWAGEN", "GOLF"),
    "VOLKSWAGEN POLO": ("VOLKSWAGEN", "POLO"),
    "VOLKSWAGEN T-CROSS": ("VOLKSWAGEN", "T-CROSS"),
    "VOLKSWAGEN T-ROC": ("VOLKSWAGEN", "T-ROC"),
    "VOLKSWAGEN TAIGO": ("VOLKSWAGEN", "TAIGO"),
    # Volvo
    "VOLVO XC40": ("VOLVO", "XC40"),
    "VOLVO XC60": ("VOLVO", "XC60"),
}

# Normalización de modelos cuando make ya es correcto pero model tiene variantes
MODEL_CORRECTIONS = {
    # Fiat
    "DOBLÓ": "DOBLO",
    "DOBLO CARGO": "DOBLO",
    # Ford
    "PUMA / 5P / TODOTERRENO": "PUMA",
    "TRANSIT CONNECT": "TRANSIT CONNECT",
    # Citroen
    "C3 AIRCROSS": "C3 AIRCROSS",
    # Peugeot
    " 208 5P ALLURE ": "208",
    "208 5P ALLURE": "208",
    # Seat
    "LEON ": "LEON",
    "ARONA": "ARONA",
    # BMW
    "SERIE 1": "SERIE 1",
    "SERIE 2": "SERIE 2",
    # Mercedes
    "CLASE A": "CLASE A",
    # Tesla
    "3": "MODEL 3",
}

def normalizar_oferta(o):
    make_raw = (o.get("make") or "").strip().upper()
    model_raw = (o.get("model") or "").strip().upper()

    # Caso 1: make contiene marca+modelo embebidos
    if make_raw in MAKE_CORRECTIONS:
        make_norm, model_norm = MAKE_CORRECTIONS[make_raw]
        o["make"] = make_norm.upper()
        o["model"] = model_norm.upper()
        return o

    # Caso 2: model tiene variantes a corregir
    if model_raw in MODEL_CORRECTIONS:
        o["model"] = MODEL_CORRECTIONS[model_raw].upper()

    # Caso 3: limpiar espacios extra en model
    o["model"] = o.get("model","").strip().upper()
    o["make"]  = o.get("make","").strip().upper()

    return o

def main():
    # Backup
    shutil.copy2(HTML_PATH, BACKUP_PATH)
    print(f"Backup: {BACKUP_PATH.name}")

    # Leer HTML y extraer ofertas
    html = HTML_PATH.read_text(encoding="utf-8")
    start = html.find("const _OFERTAS = [") + len("const _OFERTAS = ")
    end = html.find("];", start) + 1
    ofertas = json.loads(html[start:end])
    print(f"Ofertas leídas: {len(ofertas)}")

    # Normalizar
    ofertas_norm = [normalizar_oferta(o) for o in ofertas]

    # Estadísticas post-normalización
    modelos = {}
    for o in ofertas_norm:
        key = f"{o['make']} {o['model']}".strip()
        if key not in modelos:
            modelos[key] = {"count": 0, "gestoras": set()}
        modelos[key]["count"] += 1
        modelos[key]["gestoras"].add(o.get("fuente",""))

    multi = [(n, d) for n, d in modelos.items() if len(d["gestoras"]) > 1]
    multi.sort(key=lambda x: x[1]["count"], reverse=True)
    print(f"\nModelos únicos: {len(modelos)}")
    print(f"Modelos con 2+ gestoras: {len(multi)}")
    print("\nTop modelos comparables:")
    for nombre, datos in multi[:20]:
        print(f"  {nombre}: {len(datos['gestoras'])} gestoras, {datos['count']} ofertas")

    # Inyectar en HTML
    json_str = json.dumps(ofertas_norm, ensure_ascii=False, separators=(",", ":"))
    nuevo_bloque = f"const _OFERTAS = {json_str};"
    html_nuevo = html[:html.find("const _OFERTAS = [")] + nuevo_bloque + html[end+1:]
    HTML_PATH.write_text(html_nuevo, encoding="utf-8")
    print(f"\n✓ index.html actualizado")

if __name__ == "__main__":
    main()
