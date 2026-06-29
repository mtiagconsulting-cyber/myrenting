# Script de imágenes de coches

Descarga PNGs sin fondo para todos los modelos de myrenting.es.

## Instalación (una vez)

```bash
pip install rembg pillow requests duckduckgo-search onnxruntime
```

## Uso

### Descargar solo los 49 modelos que faltan (recomendado primero)
```bash
python3 descargar_imagenes_coches.py --solo-faltantes
```

### Eliminar fondos de los 181 PNGs existentes
```bash
python3 descargar_imagenes_coches.py --solo-fondos
```

### Hacer todo a la vez (fondos + faltantes)
```bash
python3 descargar_imagenes_coches.py
```

### Un modelo concreto
```bash
python3 descargar_imagenes_coches.py --modelo "BMW iX1"
```

## Qué hace

1. **Busca** imágenes de prensa en DuckDuckGo con términos como "BMW iX1 PNG transparent background press photo"
2. **Descarga** la mejor imagen encontrada (mínimo 400px)
3. **Elimina el fondo** con `rembg` (IA local, sin API key)
4. **Centra el coche** en un canvas de 800×500px con fondo transparente
5. **Guarda** en `img/modelos/<make>-<model>.png`

## Resultado esperado

Las tarjetas quedarán con el coche flotando sobre el gradiente de color CSS,
igual que la tarjeta del Toyota Proace Max EV.

## Tiempo estimado

- 49 modelos faltantes: ~15-20 minutos
- 181 PNGs con eliminación de fondo: ~30-45 minutos
- Total: ~1 hora
