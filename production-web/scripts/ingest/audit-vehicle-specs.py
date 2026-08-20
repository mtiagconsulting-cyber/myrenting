#!/usr/bin/env python3
"""Corrige potencia y transmisión visibles usando versión y fichas oficiales."""

import json
import re
import sys
from pathlib import Path


OVERRIDES = {
    ("ALFA ROMEO", "JUNIOR"): (145, "Automático"),
    ("ALFA-ROMEO", "ALFA ROMEO JUNIOR"): (145, "Automático"),
    ("BMW", "IX1"): (204, "Automático"),
    ("BMW", "SERIE 1"): (170, "Automático"),
    ("BYD", "ATTO"): (212, "Automático"),
    ("BYD", "DOLPHIN"): (88, "Automático"),
    ("CITROEN", "EBERLINGO"): (136, "Automático"),
    ("CITROEN", "Ë-BERLINGO"): (136, "Automático"),
    ("EBRO", "S400"): (211, "Automático"),
    ("HONDA", "CIVIC"): (184, "Automático"),
    ("HONDA", "HR-V"): (131, "Automático"),
    ("HONDA", "JAZZ"): (122, "Automático"),
    ("HONDA", "ZR-V"): (184, "Automático"),
    ("JAECOO", "5"): (224, "Automático"),
    ("JAECOO", "7"): (224, "Automático"),
    ("KIA", "PV5 CARGO"): (163, "Automático"),
    ("KIA", "PV5 PASSENGER"): (163, "Automático"),
    ("LANCIA", "YPSILON"): (110, "Automático"),
    ("MERCEDES-BENZ", "GLC COUPÉ"): (204, "Automático"),
    ("OMODA", "5"): (224, "Automático"),
    ("OMODA", "7"): (224, "Automático"),
    ("PEUGEOT", "RIFTER"): (100, "Manual"),
    ("RENAULT", "AUSTRAL"): (150, "Automático"),
    ("TOYOTA", "PROACE CITY"): (100, "Manual"),
    ("TOYOTA", "C-HR"): (140, "Automático"),
    ("HYUNDAI", "TUCSON"): (136, "Automático"),
}

MANUAL_MODELS = {
    ("FORD", "PUMA"), ("FORD", "TRANSIT COURIER"),
    ("FORD", "TRANSIT COURIER KOMBI DIESEL"), ("FORD", "TRANSIT CUSTOM"),
    ("NISSAN", "JUKE"), ("NISSAN", "PRIMASTAR"), ("OPEL", "VIVARO"),
    ("RENAULT", "TRAFIC COMBI DIESEL"), ("SEAT", "LEON"),
}


def inferred_power(version: str) -> int | None:
    cv = re.findall(r"(\d{2,3})\s*cv", version, re.I)
    if cv:
        return int(cv[-1])
    kw = [float(value.replace(",", ".")) for value in re.findall(r"(\d{2,3}(?:[.,]\d+)?)\s*kw", version, re.I)]
    return round(max(kw) * 1.35962) if kw else None


def inferred_transmission(vehicle: dict) -> str | None:
    version = vehicle["version"]
    key = (vehicle["brand"].upper(), vehicle["model"].upper())
    if key in MANUAL_MODELS or re.search(r"manual|\b[56]m/?t\b|\b[56]\s*vel", version, re.I):
        return "Manual"
    if re.search(r"auto|dsg|s\s*tronic|cvt|dct|1dht|e-cvt|edrive", version, re.I):
        return "Automático"
    if vehicle["fuel"] in {"Eléctrico", "Híbrido", "Híbrido enchufable"}:
        return "Automático"
    return None


def main() -> None:
    path = Path(sys.argv[1])
    data = json.loads(path.read_text(encoding="utf-8"))
    changes = 0
    for vehicle in data["vehicles"]:
        key = (vehicle["brand"].upper(), vehicle["model"].upper())
        override = OVERRIDES.get(key)
        power = override[0] if override else inferred_power(vehicle["version"])
        gearbox = override[1] if override else inferred_transmission(vehicle)
        if not vehicle.get("power") and power:
            vehicle["power"] = power
            changes += 1
        if not vehicle.get("transmission") and gearbox:
            vehicle["transmission"] = gearbox
            changes += 1
        if vehicle.get("transmission"):
            vehicle["transmission"] = "Automático" if vehicle["transmission"].lower().startswith("auto") else "Manual" if vehicle["transmission"].lower().startswith("man") else vehicle["transmission"]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Potencia/transmisión: {changes} campos corregidos")


if __name__ == "__main__":
    main()
