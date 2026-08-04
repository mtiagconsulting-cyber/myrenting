import type { Metadata } from "next";
import Link from "next/link";
import Breadcrumbs from "@/components/seo/Breadcrumbs";
import { brands } from "@/data/brands";

const MIN_MODELS = 3;
const eligible = brands.filter((b) => b.count >= MIN_MODELS);

export const metadata: Metadata = {
  title: "Renting por marca — compara todas las marcas",
  description: "Explora el renting de coches por marca. Cuota real por km y plazo, seguro y mantenimiento incluidos, sin entrada.",
  alternates: { canonical: "/marcas" },
};

export default function MarcasIndex() {
  return (
    <div className="mx-auto max-w-[1200px] px-6 pb-16">
      <Breadcrumbs items={[{ name: "Marcas" }]} />
      <h1 className="text-[clamp(28px,3.4vw,38px)] font-extrabold tracking-tight text-ink">
        Renting por marca
      </h1>
      <p className="mt-3 max-w-[76ch] text-[15.5px] leading-relaxed text-body">
        Compara el renting de coches por marca, con cuotas reales de gestoras oficiales.
      </p>
      <div className="mt-8 grid grid-cols-2 gap-3.5 md:grid-cols-4">
        {eligible.map((b) => (
          <Link
            key={b.slug}
            href={`/marcas/${b.slug}`}
            className="rounded-xl2 border border-line bg-white p-5 transition hover:border-orange hover:shadow-card"
          >
            <div className="text-[17px] font-extrabold text-ink">{b.name}</div>
            <div className="mt-1 text-[13px] text-muted">{b.count} modelos</div>
            <div className="mono mt-2 text-[15px] font-bold text-ink">
              desde {b.desde}<small className="text-xs font-bold text-muted"> €/mes</small>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
