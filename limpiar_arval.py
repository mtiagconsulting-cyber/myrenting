import json
import re

with open("arval_definitivo.json") as f:
    data = json.load(f)

for o in data:
    # Precio: "206 €" -> 206
    o["precioNum"] = int(re.sub(r"[^\d]", "", o["precio"])) if o["precio"] else 0
    
    # Duración: "72 meses" -> 72
    o["duracionNum"] = int(re.sub(r"[^\d]", "", o["duracion"])) if o["duracion"] else 0
    
    # Km: "10000 kilómetros/año" -> 10000
    o["kmNum"] = int(re.sub(r"[^\d]", "", o["km"])) if o["km"] else 0
    
    # Marca separada del modelo
    partes = o["marca"].split(" ", 1)
    o["marcaLimpia"] = partes[0].capitalize()
    o["modeloLimpio"] = partes[1].capitalize() if len(partes) > 1 else ""

print(f"Total ofertas: {len(data)}")
print(f"Rango precios: {min(o['precioNum'] for o in data)}€ - {max(o['precioNum'] for o in data)}€")
print(f"Marcas: {sorted(set(o['marcaLimpia'] for o in data))}")

with open("arval_limpio.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("\nGuardado en arval_limpio.json")
