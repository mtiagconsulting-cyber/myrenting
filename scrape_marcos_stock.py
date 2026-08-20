#!/usr/bin/env python3
"""Scrapea exclusivamente la landing comisionable de Marcos Renting Stock.

La landing publica una tarjeta por unidad de stock, por lo que puede repetir la
misma versión con IDs diferentes. Este scraper consolida esas unidades y deja:

* una sola oferta por versión/motorización;
* un máximo de dos motorizaciones diferentes por modelo;
* la matriz completa de km/año, meses y cuota de la ficha del vehículo.

Salida: ``mautomocion-db.json`` (nombre conservado por compatibilidad con el
pipeline existente de Myrenting).
"""

from __future__ import annotations

import argparse
import json
import re
import time
import unicodedata
from collections import defaultdict
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_DIR = Path(__file__).resolve().parent
LANDING_URL = "https://ofertas.marcosautomocion.es/marcos-renting-stock"
OUTPUT = BASE_DIR / "mautomocion-db.json"
SOURCE = "Marcos Renting"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9",
}


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def norm(value: object) -> str:
    text = unicodedata.normalize("NFKD", clean(value)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def money(value: object) -> float | None:
    match = re.search(r"(\d[\d.]*(?:,\d+)?)", clean(value))
    if not match:
        return None
    return float(match.group(1).replace(".", "").replace(",", "."))


def integer(value: object) -> int | None:
    match = re.search(r"\d[\d.]*", clean(value))
    return int(match.group(0).replace(".", "")) if match else None


def infer_fuel(listing_fuel: str, version: str) -> str:
    text = norm(f"{listing_fuel} {version}")
    if any(token in text for token in ("phev", "hibrido enchufable", "plug in")):
        return "Híbrido enchufable"
    if any(token in text for token in ("hev", "mhev", "hybrid", "hibrido", "e tech")):
        return "Híbrido"
    if any(token in text for token in ("electrico", "electric", "bev")):
        return "Eléctrico"
    if any(token in text for token in ("diesel", "bluehdi", "dci", "tdi", "ecoblue")):
        return "Diésel"
    if any(token in text for token in ("glp", "eco g")):
        return "GLP"
    if "gasolina" in text:
        return "Gasolina"
    return clean(listing_fuel)


def request(session: requests.Session, url: str, retries: int = 2) -> str:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            response = session.get(url, timeout=35)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"No se pudo descargar {url}: {last_error}")


def parse_listing(html: str, page_url: str) -> tuple[list[dict], set[str]]:
    soup = BeautifulSoup(html, "lxml")
    offers: list[dict] = []
    for card in soup.select(".vehicle-item[data-id]"):
        link = card.select_one("a[href*='/marcos-renting-stock/']")
        title = card.select_one("h3")
        price = card.select_one(".item-price-data-value")
        if not link or not title or not price:
            continue

        full_name = clean(title.get_text(" "))
        make = clean(card.get("data-brand")).title()
        if not make:
            make = full_name.split(" ", 1)[0]
        model = re.sub(rf"^{re.escape(make)}\s+", "", full_name, flags=re.I).strip()
        if not model:
            model = clean(card.get("data-model")).title()

        version_node = card.select_one(".h-12 .notranslate")
        version = clean(version_node.get_text(" ") if version_node else "")
        metadata = [clean(node.get_text(" ")) for node in card.select(r".h-\[42px\] > div")]
        listing_fuel = metadata[0] if metadata else ""
        transmission = metadata[1] if len(metadata) > 1 else ""
        image = card.select_one(".item-thumbnail img")
        image_url = clean((image or {}).get("data-src") or (image or {}).get("src"))
        price_value = money(price.get_text(" "))
        if not price_value:
            continue

        offers.append({
            "fuente": SOURCE,
            "tipo": "particular",
            "make": make.upper(),
            "model": model.upper(),
            "version": version,
            "fuel": infer_fuel(listing_fuel, version),
            "precio_desde": price_value,
            "duracion": 60,
            "km": 10000,
            "url": urljoin(page_url, link.get("href")),
            "image": image_url,
            "category": "",
            "iva_incluido": True,
            "transmission": transmission,
            "stock_id": clean(card.get("data-id")),
        })

    pages = {
        urljoin(page_url, a.get("href"))
        for a in soup.select("a[href*='marcos-renting-stock?page=']")
        if a.get("href")
    }
    return offers, pages


def motor_key(offer: dict) -> str:
    """Firma estable de motorización; ignora el ID de stock y el año."""
    version = re.sub(r"\b20\d{2}\b", "", offer.get("version", ""))
    return norm(f"{version} {offer.get('fuel', '')} {offer.get('transmission', '')}")


def deduplicate(offers: list[dict], max_motors: int = 2) -> list[dict]:
    exact: dict[tuple[str, str, str], dict] = {}
    for offer in offers:
        key = (norm(offer.get("make")), norm(offer.get("model")), motor_key(offer))
        current = exact.get(key)
        if current is None or offer["precio_desde"] < current["precio_desde"]:
            exact[key] = offer

    by_model: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for offer in exact.values():
        by_model[(norm(offer["make"]), norm(offer["model"]))].append(offer)

    selected: list[dict] = []
    for model_offers in by_model.values():
        model_offers.sort(key=lambda item: (item["precio_desde"], motor_key(item)))
        selected.extend(model_offers[:max_motors])
    return sorted(selected, key=lambda item: (item["precio_desde"], item["make"], item["model"]))


def first_json_ld(soup: BeautifulSoup) -> dict:
    for script in soup.select("script[type='application/ld+json']"):
        try:
            payload = json.loads(script.string or script.get_text())
        except (TypeError, json.JSONDecodeError):
            continue
        graph = payload.get("@graph", []) if isinstance(payload, dict) else []
        for node in graph:
            types = node.get("@type", []) if isinstance(node, dict) else []
            if isinstance(types, str):
                types = [types]
            if "Car" in types or "Product" in types:
                return node
    return {}


def enrich_detail(offer: dict, html: str) -> None:
    soup = BeautifulSoup(html, "lxml")
    combinations = []
    for radio in soup.select("input[name='renting_radios'][data-fee][data-months][data-km]"):
        price = money(radio.get("data-fee"))
        months = integer(radio.get("data-months"))
        km = integer(radio.get("data-km"))
        if price and months and km:
            combinations.append({"km": km, "meses": months, "precio": price})

    unique = {(c["km"], c["meses"], c["precio"]): c for c in combinations}
    combinations = sorted(unique.values(), key=lambda c: (c["precio"], c["km"], c["meses"]))
    if combinations:
        best = combinations[0]
        offer["combinaciones"] = combinations
        offer["precio_desde"] = best["precio"]
        offer["duracion"] = best["meses"]
        offer["km"] = best["km"]

    vehicle = first_json_ld(soup)
    if vehicle:
        offer["category"] = clean(vehicle.get("bodyType"))
        offer["fuel"] = infer_fuel(clean(vehicle.get("fuelType")), offer.get("version", ""))
        offer["year"] = vehicle.get("vehicleModelDate") or vehicle.get("productionDate")
        offer["color"] = clean(vehicle.get("color"))
        if vehicle.get("image"):
            offer["image"] = clean(vehicle["image"])

    equipment = {}
    for button in soup.select("button.equipment-item-title[data-tab], button.equipment-item-title"):
        target = button.get("aria-controls")
        pane = soup.find(id=target) if target else None
        label = clean(button.get_text(" "))
        if pane and label:
            equipment[label] = [clean(li.get_text(" ")) for li in pane.select("li.equipment-item")]
    if equipment:
        offer["detalle"] = {"equipamiento": equipment}


def scrape(max_motors: int = 2, detail: bool = True) -> list[dict]:
    session = requests.Session()
    session.headers.update(HEADERS)

    first_html = request(session, LANDING_URL)
    all_offers, pages = parse_listing(first_html, LANDING_URL)
    for page_url in sorted(pages):
        page_number = re.search(r"[?&]page=(\d+)", page_url)
        if page_number and page_number.group(1) == "1":
            continue
        page_html = request(session, page_url)
        page_offers, _ = parse_listing(page_html, page_url)
        all_offers.extend(page_offers)

    selected = deduplicate(all_offers, max_motors=max_motors)
    print(
        f"Landing: {len(all_offers)} unidades de stock -> "
        f"{len(selected)} ofertas únicas (máx. {max_motors} motorizaciones/modelo)"
    )

    if detail:
        for index, offer in enumerate(selected, 1):
            try:
                enrich_detail(offer, request(session, offer["url"]))
                status = f"{len(offer.get('combinaciones', []))} tarifas"
            except Exception as exc:  # conserva la oferta del listado si falla una ficha
                status = f"sin detalle: {exc}"
            print(f"  {index:02d}/{len(selected):02d} {offer['make']} {offer['model']} - {status}")
            time.sleep(0.15)

    for offer in selected:
        offer.pop("transmission", None)
        offer.pop("stock_id", None)
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listing-only", action="store_true", help="No visita las fichas de detalle")
    parser.add_argument("--max-motors", type=int, default=2, choices=(1, 2))
    parser.add_argument("--from-file", type=Path, help="Parsea una copia local de la primera página")
    args = parser.parse_args()

    if args.from_file:
        html = args.from_file.read_text(encoding="utf-8")
        offers, _ = parse_listing(html, LANDING_URL)
        result = deduplicate(offers, max_motors=args.max_motors)
    else:
        result = scrape(max_motors=args.max_motors, detail=not args.listing_only)

    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Guardado: {OUTPUT.name} ({len(result)} ofertas de {SOURCE})")


if __name__ == "__main__":
    main()
