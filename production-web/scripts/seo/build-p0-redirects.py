#!/usr/bin/env python3
"""Construye el registro P0 desde la exportación de la auditoría y el inventario actual."""

import csv
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "src/data/p0-redirects.json"
REPORT = ROOT / "src/data/p0-routing-report.json"
CITIES = {"madrid", "barcelona", "valencia", "sevilla", "malaga", "zaragoza", "bilbao", "alicante"}
ALL_LEGACY_CITIES = CITIES | {"murcia", "palma", "las-palmas", "giron", "gijon", "lleida", "tarragona", "vigo", "valladolid"}


def slug(value):
    value = unicodedata.normalize("NFD", str(value)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", value))


def model_slug(vehicle):
    brand = slug(vehicle["brand"])
    model = slug(vehicle["model"])
    return model[len(brand) + 1 :] if model.startswith(f"{brand}-") else model


def identity(value):
    value = unicodedata.normalize("NFD", str(value)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def model_key(vehicle):
    brand = identity(vehicle["brand"])
    model = identity(vehicle["model"])
    if model.startswith(f"{brand} "):
        model = model[len(brand) + 1 :]
    return f"{brand}|{model}"


def public_path(vehicle):
    return "/coches/" + slug(f'{vehicle["brand"]}-{vehicle["model"]}-{vehicle["version"]}-{vehicle["power"]}-cv-{vehicle["fuel"]}')


def representative(group):
    def rank(vehicle):
        audience = 0 if "particular" in vehicle["slug"] else 1 if "autonomo" in vehicle["slug"] else 2
        return audience, vehicle["slug"]
    return sorted(group, key=rank)[0]


def main(csv_path):
    inventory = json.loads((ROOT / "src/data/imported-inventory.json").read_text())["vehicles"]
    groups = {}
    for vehicle in inventory:
        groups.setdefault(model_key(vehicle), []).append(vehicle)
    canonical_by_old_slug = {vehicle["slug"]: public_path(representative(groups[model_key(vehicle)])) for vehicle in inventory}
    pairs = sorted({(slug(vehicle["brand"]), model_slug(vehicle)) for vehicle in inventory}, key=lambda pair: -len("-".join(pair)))
    brands = sorted({brand for brand, _ in pairs}, key=len, reverse=True)
    static = {
        "renting-barato": "/renting/baratos", "renting-hibrido": "/renting/hibridos",
        "renting-electrico": "/renting/electricos", "renting-electrico-puro": "/renting/electricos",
        "renting-hibrido-enchufable": "/renting/hibridos-enchufables", "renting-hasta-400": "/renting/menos-de-400-euros",
        "renting-hasta-300": "/renting/menos-de-300-euros", "renting-coches-menos-350": "/renting/menos-de-400-euros",
        "renting-coches-menos-500": "/renting/menos-de-500-euros", "renting-electrico-menos-400": "/renting/electricos",
        "renting-hibrido-menos-350": "/renting/hibridos", "renting-suv-menos-400": "/renting/suv",
        "renting-suv-menos-300": "/renting/suv", "renting-autonomo": "/renting/autonomos",
    }

    def fallback_destination(path):
        """Destino útil cuando la entidad antigua ya no tiene inventario equivalente."""
        if path.startswith("/coches/"):
            return "/coches", "ficha retirada; catálogo activo"
        if path.startswith("/modelos/"):
            parts = path.split("/")
            brand = parts[2] if len(parts) > 2 else ""
            return (f"/renting/{brand}", "modelo retirado; alternativas de la marca") if brand in brands else ("/renting", "modelo y marca retirados; catálogo activo")
        if path.startswith("/renting/"):
            value = path.removeprefix("/renting/")
            if re.fullmatch(r"menos-de-(200|250)-euros", value):
                return "/renting/menos-de-300-euros", "presupuesto antiguo; tramo vigente más próximo"
            brand = value.split("/", 1)[0]
            return (f"/renting/{brand}", "modelo retirado; alternativas de la marca") if brand in brands else ("/renting", "segmento retirado; catálogo activo")
        stem = path[1:-5] if path.endswith(".html") else path.strip("/")
        value = stem.removeprefix("renting-")
        for city in sorted(ALL_LEGACY_CITIES, key=len, reverse=True):
            if value.endswith(f"-{city}"):
                value = value[: -(len(city) + 1)]
                break
        if value in {"empresa", "empresas"}:
            return "/renting/empresas", "perfil equivalente"
        if re.search(r"(?:menos|hasta)-?(?:200|250)|200-300", value):
            return "/renting/menos-de-300-euros", "presupuesto antiguo; tramo vigente más próximo"
        if "300-500" in value:
            return "/renting/menos-de-500-euros", "presupuesto antiguo; tramo vigente más próximo"
        if any(term in value for term in {"todoterreno", "crossover"}):
            return "/renting/suv", "categoría vigente equivalente"
        if "hibrido" in value:
            return "/renting/hibridos", "motorización vigente equivalente"
        if any(term in value for term in {"electrico", "ev"}):
            return "/renting/electricos", "motorización vigente equivalente"
        for brand in brands:
            if value == brand or value.startswith(f"{brand}-") or brand == "mercedes-benz" and value.startswith("mercedes-"):
                return f"/renting/{brand}", "modelo retirado; alternativas de la marca"
        return "/renting", "entidad retirada; catálogo activo"
    redirects = {}
    decisions = []
    with open(csv_path, encoding="utf-8-sig") as source:
        rows = [row for row in csv.DictReader(source) if row["Prioridad"] == "P0"]
    for row in rows:
        path = urlsplit(row["URL GSC"]).path.rstrip("/") or "/"
        destination = None
        reason = "sin equivalente actual verificable"
        if path.endswith(".html"):
            stem = path[1:-5]
            destination = static.get(stem)
            if destination:
                reason = "taxonomía o presupuesto equivalente"
            else:
                value = stem.removeprefix("renting-")
                tokens = value.split("-")
                city = tokens[-1] if tokens[-1] in ALL_LEGACY_CITIES else None
                if city:
                    value = "-".join(tokens[:-1])
                if not value and city in CITIES:
                    destination, reason = f"/renting/{city}", "ciudad canónica existente"
                else:
                    for brand, model in pairs:
                        if value == f"{brand}-{model}" or brand == "mercedes-benz" and value in {f"mercedes-{model}", f"mercedes-benz-{model}"}:
                            destination, reason = f"/renting/{brand}/{model}", "modelo activo equivalente"
                            break
                    if not destination:
                        for brand in brands:
                            if value == brand or brand == "mercedes-benz" and value == "mercedes":
                                destination, reason = f"/renting/{brand}", "marca activa equivalente"
                                break
        elif path.startswith("/coches/"):
            destination = canonical_by_old_slug.get(path.rsplit("/", 1)[-1])
            if destination:
                reason = "ficha canónica del modelo activo"
        if not destination:
            destination, reason = fallback_destination(path)
        if destination and destination != path:
            redirects[path] = destination
            action = "301" if "retirad" not in reason and "antiguo" not in reason else "301_contextual"
        else:
            action = "pendiente"
        decisions.append({"url": path, "action": action, "destination": destination, "reason": reason, "clicks": row["Clics"], "impressions": row["Impresiones"]})
    OUTPUT.write_text(json.dumps([{"source": source, "destination": destination} for source, destination in sorted(redirects.items())], ensure_ascii=False, indent=2) + "\n")
    REPORT.write_text(json.dumps({"totalP0": len(rows), "redirected": len(redirects), "decisions": decisions}, ensure_ascii=False, indent=2) + "\n")
    unique_urls = len({urlsplit(row["URL GSC"]).path.rstrip("/") or "/" for row in rows})
    print(f"P0: {len(rows)} filas, {unique_urls} URLs únicas; redirecciones directas: {len(redirects)}; pendientes: {unique_urls - len(redirects)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: build-p0-redirects.py /ruta/myrenting_inventario_urls.csv")
    main(sys.argv[1])
