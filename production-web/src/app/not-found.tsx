import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Página no encontrada",
  robots: { index: false, follow: false },
};

export default function NotFound() {
  return (
    <main id="contenido-principal" className="mx-auto max-w-3xl px-5 py-20 text-center sm:px-8">
      <p className="text-xs font-bold tracking-[0.12em] text-brand uppercase">Error 404</p>
      <h1 className="font-display mt-4 text-4xl font-semibold tracking-[-0.05em] text-ink sm:text-6xl">Esta página ya no está disponible</h1>
      <p className="mt-5 text-base leading-7 text-muted">Puedes consultar las ofertas y modelos que siguen activos en el catálogo actual.</p>
      <Link href="/coches" className="mt-8 inline-flex rounded-lg bg-ink px-6 py-3 text-sm font-bold text-white">Ver coches disponibles</Link>
    </main>
  );
}
