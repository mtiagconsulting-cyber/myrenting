import Link from "next/link";
import { vehicles, byFuel } from "@/data/vehicles";
import type { Vehicle } from "@/types";

const pick = (title: string) => vehicles.find((v) => v.title === title);

function buildPairs(): [Vehicle, Vehicle][] {
  const elec = byFuel("electricos").filter((v) => v.img);
  const raw: (Vehicle | undefined)[][] = [
    [pick("Renault Captur"), pick("Toyota Yaris")],
    [pick("Hyundai Tucson"), pick("Opel Frontera")],
    [pick("Peugeot 208"), pick("Opel Corsa")],
    [elec[0], elec[1]],
  ];
  return raw.filter((p): p is [Vehicle, Vehicle] => p[0] != null && p[1] != null);
}

const reasons = [
  "Información independiente y objetiva",
  "Todas las ofertas en un solo lugar",
  "Cuota real por km y plazo",
  "Ahorra tiempo y dinero",
];

export default function ComparisonCards() {
  const pairs = buildPairs();
  return (
    <section className="py-7">
      <div className="mb-[18px] flex items-center justify-between">
        <h2 className="text-[clamp(23px,2.4vw,30px)] font-extrabold text-ink">Comparativas populares</h2>
        <Link href="/comparar" className="text-[13.5px] font-semibold text-orange">
          Ver todas las comparativas ›
        </Link>
      </div>
      <div className="grid items-start gap-[18px] md:grid-cols-[2.4fr_1fr]">
        <div className="grid gap-3.5 md:grid-cols-2">
          {pairs.map((p, i) => (
            <Link
              key={i}
              href={`/comparar/${p[0].slug}-vs-${p[1].slug}`}
              className="rounded-xl2 border border-line bg-white p-4 transition hover:border-orange"
            >
              <div className="flex items-center gap-2">
                {p.map((v, j) => (
                  <div key={j} className="flex-1 text-center">
                    {v.img && <img src={v.img} alt={v.title} className="h-[52px] w-full object-contain" />}
                    <b className="mt-1 block text-[13px] text-ink">{v.title}</b>
                    <span className="text-[11px] text-muted">Desde</span>
                    <div className="text-[12.5px] font-bold text-ink">{v.precio}€/mes</div>
                  </div>
                ))}
                <div className="order-2 grid h-[30px] w-[30px] place-items-center rounded-full border border-line bg-paper text-xs font-black text-muted">
                  VS
                </div>
              </div>
            </Link>
          ))}
        </div>
        <div className="rounded-xl2 border border-line bg-white p-5">
          <b className="text-[15px] text-ink">¿Por qué comparar en myrenting?</b>
          <ul className="mb-4 mt-3 space-y-0 text-[13.5px] text-body">
            {reasons.map((t, i) => (
              <li
                key={i}
                className="relative py-1.5 pl-6 before:absolute before:left-0 before:font-black before:text-orange before:content-['✓']"
              >
                {t}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
