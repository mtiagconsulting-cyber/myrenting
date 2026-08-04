import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Vehicle } from "@/types";

export default function VehicleCard({ v }: { v: Vehicle }) {
  const badges = [v.fuel, v.dgt && v.dgt !== "—" ? "Etiqueta " + v.dgt : ""].filter(Boolean).slice(0, 2);
  return (
    <Link href={`/coches/${v.slug}`} className="group">
      <Card className="flex h-full flex-col overflow-hidden transition group-hover:border-orange group-hover:shadow-card">
        <div className="flex aspect-[16/10] items-center justify-center border-b border-line bg-paper">
          {v.img && (
            <img
              src={v.img}
              alt={v.title}
              className="h-[84%] w-[88%] object-contain transition-transform duration-300 group-hover:scale-[1.03]"
            />
          )}
        </div>
        <div className="p-4">
          <div className="mb-2 flex flex-wrap gap-1.5">
            {badges.map((b, i) => (
              <Badge key={i} variant="neutral">{b}</Badge>
            ))}
          </div>
          <div className="text-[17px] font-extrabold tracking-tight text-ink">{v.title}</div>
          <div className="mt-0.5 truncate text-xs text-muted">{v.version}</div>
          <div className="mt-3 flex items-baseline gap-1">
            <span className="mono text-[26px] font-extrabold text-ink">{v.precio}</span>
            <small className="font-bold text-muted">€/mes</small>
            <span className="ml-auto self-center text-[11px] text-muted">desde</span>
          </div>
          <span className="mt-2.5 inline-flex items-center gap-1 text-[13.5px] font-bold text-orange">
            Ver oferta <ArrowRight size={15} className="transition-transform group-hover:translate-x-0.5" />
          </span>
        </div>
      </Card>
    </Link>
  );
}
