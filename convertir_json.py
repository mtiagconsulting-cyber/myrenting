"""
Convierte todas_ofertas.json (formato scraper) al formato que usa el index.html (_OFERTAS).
Ejecutar: python3 convertir_json.py
Output: ofertas_para_html.json
"""

import json
import re

ENTRADA = "/Users/matthiasthomassen/Documents/Myrenting/todas_ofertas.json"
SALIDA  = "/Users/matthiasthomassen/Documents/Myrenting/ofertas_para_html.json"

def normalizar_combustible(combustible):
    """Normaliza el campo combustible al formato del HTML."""
    if not combustible:
        return "Gasolina"
    c = combustible.lower().strip()
    if "eléctrico" in c or "electrico" in c or "electric" in c:
        return "Eléctrico"
    if "enchufable" in c or "plug" in c or "phev" in c:
        return "Híbrido Enchufable"
    if "híbrido" in c or "hibrido" in c or "hybrid" in c or "hev" in c or "mhev" in c:
        return "Híbrido"
    if "diésel" in c or "diesel" in c:
        return "Diésel"
    if "gasolina" in c or "gasoline" in c or "petrol" in c:
        return "Gasolina"
    if "glp" in c or "gas" in c:
        return "GLP"
    return combustible  # devolver tal cual si no se reconoce

def normalizar_tipo(tipo_cliente):
    """Normaliza el tipo de cliente."""
    if not tipo_cliente:
        return "empresa"
    t = tipo_cliente.lower().strip()
    if "particular" in t:
        return "particular"
    return "empresa"

def construir_precios(oferta):
    """
    Construye la matriz precios [[duracion, km, precio_sin_iva, precio_con_iva], ...]
    Para ofertas del scraper solo tenemos un precio y una duración/km.
    precio_desde es el precio final (con IVA normalmente en renting para empresas).
    Usamos 0.0 como precio sin IVA (no disponemos de él).
    """
    duracion = oferta.get("duracionNum") or 36
    km       = oferta.get("kmNum") or 10000
    precio   = oferta.get("precioNum") or oferta.get("precio_desde") or 0

    # Si ya tiene formato de HTML (precio_desde + precios), lo dejamos
    if "precios" in oferta and "precio_desde" in oferta:
        return oferta["precios"], oferta["precio_desde"]

    return [[duracion, km, 0.0, float(precio)]], float(precio)

def convertir_oferta(o):
    """Convierte una oferta del formato scraper al formato HTML."""
    
    # Si ya tiene el formato correcto del HTML, la dejamos tal cual
    if "fuente" in o and "make" in o and "precio_desde" in o:
        return o
    
    # Formato scraper: tiene gestora, marca, modeloLimpio, etc.
    fuente  = o.get("gestora") or o.get("fuente") or "Desconocida"
    tipo    = normalizar_tipo(o.get("tipoCliente") or o.get("tipo") or "empresa")
    
    # Separar marca y modelo
    make    = o.get("marca") or ""
    model   = o.get("modeloLimpio") or o.get("modelo") or ""
    
    # Si 'marca' contiene espacio (ej: "SEAT ARONA"), intentar separar
    if not model and " " in make:
        partes = make.split(" ", 1)
        make   = partes[0]
        model  = partes[1]
    
    version = o.get("version") or ""
    
    # Combustible
    fuel    = normalizar_combustible(o.get("combustible") or o.get("fuel") or "")
    
    # Imagen y URL
    image      = o.get("imagen") or o.get("image") or ""
    link_oferta = o.get("url") or o.get("link_oferta") or ""
    
    # Precios
    precios, precio_desde = construir_precios(o)
    
    return {
        "fuente":       fuente,
        "tipo":         tipo,
        "make":         make.upper() if make else make,
        "model":        model.upper() if model else model,
        "version":      version,
        "category":     o.get("category") or "",
        "fuel":         fuel,
        "transmission": o.get("transmission") or "",
        "image":        image,
        "precio_desde": precio_desde,
        "precios":      precios,
        "link_oferta":  link_oferta,
    }

def main():
    print(f"Leyendo {ENTRADA}...")
    with open(ENTRADA, "r", encoding="utf-8") as f:
        ofertas = json.load(f)
    
    print(f"  → {len(ofertas)} ofertas leídas")
    
    convertidas = []
    errores = 0
    for i, o in enumerate(ofertas):
        try:
            convertidas.append(convertir_oferta(o))
        except Exception as e:
            errores += 1
            print(f"  ERROR en oferta {i}: {e}")
    
    print(f"  → {len(convertidas)} convertidas ({errores} errores)")
    
    # Estadísticas
    fuentes = {}
    for o in convertidas:
        f = o["fuente"]
        fuentes[f] = fuentes.get(f, 0) + 1
    print("\nOfertas por gestora:")
    for f, n in sorted(fuentes.items()):
        print(f"  {f}: {n}")
    
    # Guardar
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(convertidas, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Guardado en: {SALIDA}")
    print(f"\nPróximo paso: copiar el contenido de este JSON")
    print("y reemplazar el array _OFERTAS en el index.html")

if __name__ == "__main__":
    main()
