# -*- coding: utf-8 -*-
"""Sincroniza los datos del frontend Next.js con el catálogo consolidado."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOGO = ROOT / "data/build/catalogo.json"
WEB_DATA = ROOT / "web/data"


def consumo(specs):
    if specs.get("consumo_l100") is not None:
        return f'{str(specs["consumo_l100"]).replace(".", ",")} L/100 km'
    if specs.get("consumo_kwh100") is not None:
        return f'{str(specs["consumo_kwh100"]).replace(".", ",")} kWh/100 km'
    return "—"


catalogo = json.loads(CATALOGO.read_text(encoding="utf-8"))["modelos"]
vehicles = []
matrices = {}

for model in catalogo.values():
    offers = model.get("ofertas", [])
    if not offers:
        continue
    specs = model.get("specs") or {}
    cheapest = min(offers, key=lambda item: item.get("precio_desde", 10**9))
    commissionable = [offer for offer in offers if offer.get("fuente") == "Marcos Renting" and offer.get("url")]
    vehicles.append({
        "slug": model["slug"],
        "make": model["make"],
        "model": model["model"],
        "title": f'{model["make"]} {model["model"]}',
        "version": cheapest.get("version") or model["model"],
        "fuel": specs.get("combustible") or cheapest.get("fuel") or "—",
        "category": specs.get("category") or "—",
        "dgt": specs.get("etiqueta_dgt") or "—",
        "cv": specs.get("potencia") or "—",
        "seats": f'{specs["plazas"]} plazas' if specs.get("plazas") else "—",
        "cons": consumo(specs),
        "precio": round(model["precio_desde"]),
        "img": specs.get("imagen") or cheapest.get("image") or "",
        "fuentes": model.get("fuentes") or [],
        "tipoMin": cheapest.get("tipo") or "particular",
        "ofertas": [{
            "fuente": offer["fuente"],
            "version": offer.get("version") or model["model"],
            "fuel": offer.get("fuel") or specs.get("combustible") or "—",
            "precio": round(offer["precio_desde"]),
            "duracion": offer.get("duracion"),
            "km": offer.get("km"),
            "url": offer["url"],
        } for offer in commissionable[:2]],
    })

    by_type = {}
    for offer in offers:
        matrix = by_type.setdefault(offer.get("tipo") or "particular", {})
        for combination in offer.get("combinaciones", []):
            key = f'{combination["km"]}|{combination["meses"]}'
            price = round(combination["precio"])
            matrix[key] = min(matrix.get(key, price), price)
    matrices[model["slug"]] = by_type

vehicles.sort(key=lambda vehicle: (vehicle["precio"], vehicle["title"]))
WEB_DATA.mkdir(parents=True, exist_ok=True)
(WEB_DATA / "vehicles.json").write_text(json.dumps(vehicles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(WEB_DATA / "matrices.json").write_text(json.dumps(matrices, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Frontend sincronizado: {len(vehicles)} modelos, {sum(len(v['ofertas']) for v in vehicles)} ofertas comisionables")
