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


def main(csv_path, priority="P0"):
    output = ROOT / f"src/data/{priority.lower()}-redirects.json"
    report = ROOT / f"src/data/{priority.lower()}-routing-report.json"
    inventory = json.loads((ROOT / "src/data/imported-inventory.json").read_text())["vehicles"]
    groups = {}
    for vehicle in inventory:
        groups.setdefault(model_key(vehicle), []).append(vehicle)
    canonical_by_old_slug = {vehicle["slug"]: public_path(representative(groups[model_key(vehicle)])) for vehicle in inventory}
    pairs = sorted({(slug(vehicle["brand"]), model_slug(vehicle)) for vehicle in inventory}, key=lambda pair: -len("-".join(pair)))
    brands = sorted({brand for brand, _ in pairs}, key=len, reverse=True)
    canonical_routes = {
        "/", "/coches", "/renting", "/renting/baratos", "/renting/sin-entrada", "/renting/entrega-inmediata",
        "/renting/particulares", "/renting/autonomos", "/renting/empresas", "/renting/suv", "/renting/familiares",
        "/renting/furgonetas", "/renting/coches-pequenos", "/renting/electricos", "/renting/hibridos",
        "/renting/hibridos-enchufables", "/renting/gasolina", "/renting/diesel", "/renting/menos-de-300-euros",
        "/renting/menos-de-400-euros", "/renting/menos-de-500-euros", "/renting/7-plazas", "/renting/4x4",
        "/renting/automaticos", "/renting/etiqueta-eco", "/renting/etiqueta-cero", "/preguntas-frecuentes",
    }
    canonical_routes.update(f"/renting/{months}-meses" for months in (12, 24, 36, 48, 60))
    canonical_routes.update(f"/renting/{brand}" for brand in brands)
    canonical_routes.update(f"/renting/{brand}/{model}" for brand, model in pairs)
    canonical_routes.update(canonical_by_old_slug.values())
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
        if value in {"autonomo", "autonomos"}:
            return "/renting/autonomos", "perfil equivalente"
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
    excluded_sources = {item["source"] for item in json.loads((ROOT / "src/data/p0-redirects.json").read_text())} if priority == "P1" and (ROOT / "src/data/p0-redirects.json").exists() else set()
    preexisting_redirect_sources = {item["source"] for item in json.loads((ROOT / "src/data/legacy-redirects.json").read_text())}
    # Estas rutas históricas apuntaban a filtros con query string. Sustituirlas
    # por las landings canónicas de audiencia evita que terminen en 404.
    preexisting_redirect_sources.difference_update({
        "/renting-autonomos.html", "/renting-empresas.html", "/renting-particulares.html",
    })
    preexisting_redirect_sources.update(f"/coches/{vehicle['slug']}" for vehicle in inventory)
    preexisting_redirect_sources.update(f"/marcas/{brand}" for brand in brands)
    preexisting_redirect_sources.update(f"/modelos/{brand}/{model}" for brand, model in pairs)
    preexisting_redirect_sources.update({
        "/categorias/suv", "/categorias/familiares", "/categorias/urbanos", "/categorias/berlinas", "/categorias/empresas",
        "/combustibles/gasolina", "/combustibles/diesel", "/combustibles/hibridos", "/combustibles/hibridos-enchufables", "/combustibles/electricos",
        "/renting-suv", "/renting-hibridos", "/renting-electricos", "/renting-barato", "/renting-sin-entrada",
        "/renting-entrega-inmediata", "/renting-autonomos", "/renting-automaticos", "/renting-etiqueta-eco",
        "/renting-etiqueta-cero", "/renting-furgonetas", "/renting-menos-300-euros", "/renting-menos-350-euros",
        "/renting-menos-450-euros", "/renting-menos-500-euros", "/renting-menos-600-euros", "/renting-menos-700-euros",
    })
    for brand in brands:
        preexisting_redirect_sources.update(f"/marcas/{brand}/{audience}" for audience in ("particular", "autonomo", "empresa"))
    for brand, model in pairs:
        preexisting_redirect_sources.update(f"/modelos/{brand}/{model}/{audience}" for audience in ("particular", "autonomo", "empresa"))
    for category in ("suv", "familiares", "urbanos", "berlinas", "empresas"):
        preexisting_redirect_sources.update(f"/categorias/{category}/{audience}" for audience in ("particular", "autonomo", "empresa"))
    decisions = []
    with open(csv_path, encoding="utf-8-sig") as source:
        rows = [row for row in csv.DictReader(source) if row["Prioridad"] == priority]
    for row in rows:
        path = urlsplit(row["URL GSC"]).path.rstrip("/") or "/"
        if path in excluded_sources:
            decisions.append({"url": path, "action": "cubierta_P0", "destination": None, "reason": "regla ya definida en el lote P0", "clicks": row["Clics"], "impressions": row["Impresiones"]})
            continue
        if priority == "P1" and path in preexisting_redirect_sources:
            decisions.append({"url": path, "action": "mantener_301", "destination": None, "reason": "redirección estructural existente", "clicks": row["Clics"], "impressions": row["Impresiones"]})
            continue
        destination = None
        reason = "sin equivalente actual verificable"
        if priority != "P0" and (path in canonical_routes or not path.startswith(("/renting", "/coches/", "/marcas/", "/modelos/", "/categorias/", "/combustibles/"))):
            decisions.append({"url": path, "action": "mantener_200", "destination": None, "reason": "URL canónica o contenido editorial", "clicks": row["Clics"], "impressions": row["Impresiones"]})
            continue
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
        elif path.startswith("/renting/"):
            parts = path.split("/")[2:]
            intents = {"barato", "baratos", "sin-entrada", "entrega-inmediata"}
            if parts and (parts[-1] in intents or parts[-1].startswith("menos-de-")):
                base = "/renting/" + "/".join(parts[:-1])
                if base in canonical_routes:
                    destination, reason = base, "filtro secundario consolidado en su entidad canónica"
        if not destination:
            destination, reason = fallback_destination(path)
        if destination and destination != path:
            redirects[path] = destination
            action = "301" if "retirad" not in reason and "antiguo" not in reason else "301_contextual"
        else:
            action = "pendiente"
        decisions.append({"url": path, "action": action, "destination": destination, "reason": reason, "clicks": row["Clics"], "impressions": row["Impresiones"]})
    output.write_text(json.dumps([{"source": source, "destination": destination} for source, destination in sorted(redirects.items())], ensure_ascii=False, indent=2) + "\n")
    report.write_text(json.dumps({"priority": priority, "total": len(rows), "redirected": len(redirects), "decisions": decisions}, ensure_ascii=False, indent=2) + "\n")
    unique_urls = len({urlsplit(row["URL GSC"]).path.rstrip("/") or "/" for row in rows})
    print(f"{priority}: {len(rows)} filas, {unique_urls} URLs únicas; redirecciones directas: {len(redirects)}; URLs canónicas: {unique_urls - len(redirects)}")


if __name__ == "__main__":
    if len(sys.argv) not in {2, 3}:
        raise SystemExit("Uso: build-p0-redirects.py /ruta/myrenting_inventario_urls.csv [P0|P1]")
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "P0")
