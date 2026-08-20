# Matriz de indexación de filtros y facetas

## URLs indexables

- `/coches`: catálogo general.
- `/marcas/{marca}`: marca con inventario activo.
- `/modelos/{marca}/{modelo}`: modelo estable que agrupa versiones, proveedores y perfiles.
- `/categorias/{categoria}`: carrocería o uso general.
- `/categorias/{categoria}/{publico}`: combinación editorial de categoría y perfil con inventario activo.
- `/combustibles/{combustible}`: combustible con un mínimo actual superior a 20 vehículos.

Estas URLs tienen contenido propio, canonical autorreferente, aparecen en el sitemap y se generan en servidor.

## URLs no indexables como páginas independientes

- Parámetros de `/coches`: `marca`, `presupuesto`, `kilometros`, `publico` y sus combinaciones.
- Parámetros de configuración dentro de una ficha.
- Ordenaciones, búsquedas internas y estados de interfaz.

Los filtros conservan la canonical de `/coches` o de la ficha sin parámetros y nunca se incorporan al sitemap. Solo se convertirá una faceta en landing indexable cuando tenga demanda demostrable, inventario suficiente y contenido editorial diferenciado.

## Criterios para crear una nueva landing

1. Demanda comprobada en Search Console o en el benchmark GEO.
2. Al menos 6 vehículos activos, salvo una intención de modelo exacta.
3. Texto y datos propios que respondan a una intención distinta.
4. Canonical autorreferente, enlaces internos y presencia en sitemap.
5. Retirada o redirección si el inventario desaparece de forma prolongada.
