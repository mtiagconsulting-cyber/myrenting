#!/usr/bin/env python3
"""Añade a imported-inventory.json el stock de la landing de Marcos Automoción."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path


PROVIDER = "Marcos Automoción"


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", value))


def power(version: str) -> int:
    matches = re.findall(r"(\d{2,3})\s*(?:cv|CV)", version)
    return int(matches[-1]) if matches else 0


def transmission(version: str) -> str | None:
    if re.search(r"manual|\b6mt\b", version, re.I):
        return "Manual"
    if re.search(r"auto|autom[aá]tic|dsg|stronic|s tronic|\bat\b", version, re.I):
        return "Automático"
    return None


def body_type(value: str, model: str) -> str:
    text = f"{value} {model}".lower()
    if re.search(r"furg|van|cargo|transit|vivaro|primastar|berlingo|rifter|combo", text):
        return "Furgoneta"
    if re.search(r"suv|todoterreno|captur|kuga|puma|qashqai|juke|tucson|austral|cx-|hr-v|zr-v|cr-v|ix1", text):
        return "SUV"
    if "berlina" in text:
        return "Berlina"
    return "Compacto"


def label(fuel: str) -> str:
    if fuel == "Eléctrico":
        return "0"
    if fuel in {"Híbrido", "Híbrido enchufable", "GLP"}:
        return "ECO"
    return "C"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("photo_manifest", type=Path)
    args = parser.parse_args()

    raw = json.loads(args.input.read_text(encoding="utf-8"))
    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    manifest = json.loads(args.photo_manifest.read_text(encoding="utf-8"))
    marcos_ids = {offer["vehicleId"] for offer in inventory["offers"] if offer["provider"] == PROVIDER}
    inventory["offers"] = [offer for offer in inventory["offers"] if offer["provider"] != PROVIDER]
    inventory["vehicles"] = [vehicle for vehicle in inventory["vehicles"] if vehicle["id"] not in marcos_ids]
    for key in list(manifest["photos"]):
        if key.startswith("veh-marcos-"):
            del manifest["photos"][key]

    verified = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    added_offers = 0
    for item in raw:
        identity = slugify(f"{item['make']}-{item['model']}-{item['version']}")
        vehicle_id = f"veh-marcos-{identity}"
        image = item.get("image") or ""
        fuel = item.get("fuel") if item.get("fuel") in {"Gasolina", "Diésel", "Híbrido", "Híbrido enchufable", "Eléctrico"} else "Gasolina"
        inventory["vehicles"].append({
            "id": vehicle_id,
            "brand": item["make"],
            "model": item["model"],
            "version": item["version"],
            "slug": f"marcos-{identity}",
            "images": None,
            "fuel": fuel,
            "power": power(item["version"]),
            "trunk": None,
            "consumption": None,
            "consumptionUnit": "kWh/100 km" if fuel == "Eléctrico" else "l/100 km",
            "label": label(fuel),
            "bodyType": body_type(item.get("category", ""), item["model"]),
            "transmission": transmission(item["version"]),
            "doors": None,
            "seats": None,
            "colors": [item["color"]] if item.get("color") else None,
            "campaign": "Marcos Renting Stock",
            "sourceUrl": item["url"],
        })
        if image:
            manifest["photos"][vehicle_id] = {
                "hero": image, "card": image, "compare": image,
                "interior": image, "trunk": image, "sourceFolder": "Marcos Automoción",
            }
        combinations = item.get("combinaciones") or [{"precio": item["precio_desde"], "meses": item["duracion"], "km": item["km"]}]
        for combo in combinations:
            offer_id = slugify(f"marcos-{identity}-{combo['meses']}-{combo['km']}-{combo['precio']}")
            inventory["offers"].append({
                "id": f"off-{offer_id}", "vehicleId": vehicle_id, "provider": PROVIDER,
                "audience": "particular", "monthlyPrice": combo["precio"], "priceIncludesVat": True,
                "monthlyPriceExVat": round(combo["precio"] / 1.21, 2), "monthlyPriceIncVat": combo["precio"],
                "initialPayment": 0, "duration": combo["meses"], "kilometers": combo["km"],
                "maintenance": None, "insurance": None, "tyres": None, "coverage": [],
                "availability": "Disponible", "sourceUrl": item["url"], "verifiedAt": verified,
            })
            added_offers += 1

    inventory["generatedAt"] = verified
    args.inventory.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.photo_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Marcos Automoción: {len(raw)} vehículos y {added_offers} combinaciones añadidas")


if __name__ == "__main__":
    main()
