import Link from "next/link";
import SearchBox from "./SearchBox";
import { vehicles, sortedByPrice, getVehicle } from "@/data/vehicles";

const trust: [string, string][] = [
  ["Ofertas reales", "de gestoras oficiales"],
  ["Cuotas con y sin IVA", "particular o empresa"],
  ["Sin compromiso", "ni registro"],
  ["Datos actualizados", "cada semana"],
];

export default function Hero() {
  const withImg = sortedByPrice.filter((v) => v.img);
  const pick = (title: string) => getVehicle(vehicles.find((v) => v.title === title)?.slug ?? "");
  const heroPref = [pick("Hyundai Tucson"), pick("Seat Leon"), pick("Opel Corsa")].filter(Boolean);
  const heroImgs = heroPref.length === 3 ? heroPref : withImg.slice(0, 3);
  const quickPref = [pick("Renault Captur"), pick("Hyundai Tucson"), pick("Peugeot 208")].filter(Boolean);
  const quick = quickPref.length === 3 ? quickPref : withImg.slice(0, 3);

  return (
    <section className="grid items-center gap-9 py-12 md:grid-cols-[1fr_1.12fr]">
      <div>
        <h1 className="text-[clamp(38px,4.6vw,60px)] font-extrabold leading-[1.05] tracking-tight text-ink">
          Encuentra tu <span className="text-orange">renting ideal</span>
        </h1>
        <p className="mt-5 max-w-[46ch] text-lg leading-relaxed text-muted">
          Comparamos ofertas reales, condiciones y vehículos para ayudarte a elegir mejor. Sin letra
          pequeña. Sin sorpresas.
        </p>
        <SearchBox />
        <div className="mt-6 flex flex-wrap gap-6">
          {trust.map(([a, b], i) => (
            <div key={i} className="flex max-w-[180px] items-start gap-2.5 text-[13px] text-muted">
              <span className="grid h-6 w-6 flex-none place-items-center rounded-lg bg-orange-soft text-xs font-black text-orange">
                ✓
              </span>
              <span>
                <b className="block font-semibold text-ink">{a}</b>
                {b}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="relative">
        <div className="flex items-center justify-center px-2.5">
          {heroImgs.map((v, i) => (
            <img
              key={i}
              src={v!.img}
              alt={v!.title}
              className={`object-contain drop-shadow-[0_24px_26px_rgba(16,24,40,.20)] ${
                i === 1 ? "z-20 w-[48%]" : "z-10 w-[40%]"
              } ${i === 0 ? "mr-[-9%]" : ""} ${i === 2 ? "ml-[-9%]" : ""}`}
            />
          ))}
        </div>
        <div className="relative z-30 mx-auto -mt-7 max-w-[560px] rounded-xl2 border border-line bg-white p-5 shadow-pop">
          <div className="mb-1.5 flex items-center justify-between">
            <b className="text-[15.5px] text-ink">Comparativa rápida</b>
            <Link href="/comparar" className="text-[12.5px] font-semibold text-orange">
              Ver todas ›
            </Link>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {quick.map((v, i) => (
              <div key={i} className={`pt-2 text-center ${i > 0 ? "border-l border-line" : ""}`}>
                {v!.img && <img src={v!.img} alt={v!.title} className="mx-auto h-[52px] w-[88%] object-contain" />}
                <div className="mt-1 text-[13px] font-semibold text-ink">{v!.title}</div>
                <div className="text-[11px] text-muted">{v!.fuel}</div>
                <div className="mt-1.5 text-[10.5px] text-muted">Desde</div>
                <div className="mono text-base font-extrabold text-ink">
                  {v!.precio}
                  <small className="text-[10px] text-muted">€/mes</small>
                </div>
                <Link href={`/coches/${v!.slug}`} className="mt-1 block text-[11.5px] font-semibold text-orange">
                  Ver oferta ›
                </Link>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
