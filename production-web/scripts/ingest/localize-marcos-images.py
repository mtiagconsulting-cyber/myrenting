#!/usr/bin/env python3
"""Guarda localmente las imágenes exactas de las ofertas de Marcos Automoción."""

import io
import json
import re
import sys
import unicodedata
from pathlib import Path

import requests
from PIL import Image, ImageOps


def slug(value: str) -> str:
    value = unicodedata.normalize("NFD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", value))


root = Path(sys.argv[1])
inventory_path = root / "src/data/imported-inventory.json"
manifest_path = root / "src/data/photo-manifest.json"
inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
marcos_ids = {offer["vehicleId"] for offer in inventory["offers"] if offer["provider"] == "Marcos Automoción"}
vehicles = {vehicle["id"]: vehicle for vehicle in inventory["vehicles"]}
output = root / "public/vehicle-images"
output.mkdir(parents=True, exist_ok=True)
session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0 MyRenting image localizer"
saved = 0

for vehicle_id in sorted(marcos_ids):
    record = manifest["photos"].get(vehicle_id, {})
    source = record.get("card", "")
    if not source.startswith("http"):
        continue
    vehicle = vehicles[vehicle_id]
    filename = f"marcos-{slug(vehicle['brand'] + '-' + vehicle['model'] + '-' + vehicle['version'])}-card.webp"
    target = output / filename
    response = session.get(source, timeout=40)
    response.raise_for_status()
    with Image.open(io.BytesIO(response.content)) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
        image.thumbnail((1400, 875), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (1400, 875), "white")
        canvas.paste(image, ((1400 - image.width) // 2, (875 - image.height) // 2))
        canvas.save(target, "WEBP", quality=88, method=6)
    public_path = f"/vehicle-images/{filename}"
    manifest["photos"][vehicle_id] = {
        "hero": public_path, "card": public_path, "compare": public_path,
        "interior": public_path, "trunk": public_path, "sourceFolder": "Marcos Automoción",
    }
    saved += 1

manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Marcos Automoción: {saved} imágenes exactas guardadas localmente")
