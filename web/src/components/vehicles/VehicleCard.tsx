import Link from "next/link";
import type { Vehicle } from "@/lib/types";
export default function VehicleCard({ v }: { v: Vehicle }) {
  const badges = [v.fuel, v.dgt && v.dgt !== "—" ? "Etiqueta " + v.dgt : ""].filter(Boolean).slice(0, 2);
  return (
    <Link href={`/coches/${v.slug}`} className="bg-white border border-line rounded-xl2 overflow-hidden flex flex-col hover:border-orange hover:shadow-card transition">
      <div className="aspect-[16/10] bg-paper flex items-center justify-center border-b border-line">
        {v.img && <img src={v.img} alt={v.title} className="w-[88%] h-[84%] object-contain" />}
      </div>
      <div className="p-4">
        <div className="flex gap-1.5 flex-wrap mb-2">
          {badges.map((b, i) => <span key={i} className="text-[10.5px] font-bold text-muted bg-paper border border-line rounded-full px-2 py-0.5">{b}</span>)}
        </div>
        <div className="font-extrabold text-ink text-[17px] tracking-tight">{v.title}</div>
        <div className="text-xs text-muted truncate mt-0.5">{v.version}</div>
        <div className="mt-3 flex items-baseline gap-1">
          <span className="mono text-[26px] font-extrabold text-ink">{v.precio}</span>
          <small className="text-muted font-bold">€/mes</small>
          <span className="ml-auto text-[11px] text-muted self-center">desde</span>
        </div>
        <span className="inline-block mt-2.5 text-orange font-bold text-[13.5px]">Ver oferta →</span>
      </div>
    </Link>
  );
}
