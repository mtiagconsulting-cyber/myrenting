import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import Breadcrumbs from "@/components/seo/Breadcrumbs";
import { guias } from "@/data/guias";

export const metadata: Metadata = {
  title: "Guías y consejos de renting",
  description:
    "Guías prácticas de renting: qué incluye la cuota, renting vs compra, renting para autónomos y etiquetas DGT.",
  alternates: { canonical: "/guias" },
};

export default function Guias() {
  return (
    <div className="mx-auto max-w-[1200px] px-6 pb-16">
      <Breadcrumbs items={[{ name: "Guías y consejos" }]} />
      <h1 className="text-[clamp(28px,3.4vw,38px)] font-extrabold tracking-tight text-ink">
        Guías y consejos de renting
      </h1>
      <p className="mt-3 max-w-[76ch] text-[15.5px] leading-relaxed text-body">
        Todo lo que necesitas saber antes de contratar un renting, explicado sin letra pequeña.
      </p>
      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {guias.map((g) => (
          <Link
            key={g.slug}
            href={`/guias/${g.slug}`}
            className="group flex flex-col rounded-xl2 border border-line bg-white p-5 transition hover:border-orange hover:shadow-card"
          >
            <div className="text-[11px] font-bold uppercase tracking-wide text-orange">Guía</div>
            <h2 className="mt-1.5 text-[17px] font-extrabold leading-snug text-ink">{g.title}</h2>
            <p className="mt-2 flex-1 text-[13.5px] leading-relaxed text-muted">{g.description}</p>
            <span className="mt-3 inline-flex items-center gap-1 text-[13.5px] font-bold text-orange">
              Leer guía <ArrowRight size={15} className="transition-transform group-hover:translate-x-0.5" />
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
