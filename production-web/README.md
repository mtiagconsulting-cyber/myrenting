# MyRenting

Comparador de renting de coches para España, construido con Next.js 15, TypeScript y Tailwind CSS.

## Requisitos

- Node.js 20.9 o superior
- npm 10 o superior

## Desarrollo local

1. Copia `.env.example` como `.env.local`.
2. Completa las variables de Supabase cuando el backend esté disponible.
3. Instala dependencias con `npm install`.
4. Ejecuta `npm run dev`.

La página inicial no requiere credenciales de Supabase. La validación solo se activa al crear el cliente.

## Comandos

- `npm run dev`: servidor local.
- `npm run build`: compilación de producción.
- `npm run lint`: análisis estático.
- `npm run typecheck`: comprobación estricta de TypeScript.
