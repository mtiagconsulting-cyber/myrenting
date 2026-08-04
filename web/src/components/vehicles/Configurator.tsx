"use client";
import { useMemo, useState } from "react";
import { Mail, MessageCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { VehicleMatrices } from "@/types";

export default function Configurator({ name, matrices }: { name: string; matrices: VehicleMatrices }) {
  const hasCon = !!matrices["particular"];
  const hasSin = !!(matrices["empresa"] || matrices["autonomo"]);
  const [iva, setIva] = useState<"con" | "sin">(hasCon ? "con" : "sin");
  const mat = (iva === "con" ? matrices["particular"] : matrices["empresa"] || matrices["autonomo"]) || {};
  const kms = useMemo(() => [...new Set(Object.keys(mat).map((k) => +k.split("|")[0]))].sort((a, b) => a - b), [mat]);
  const mss = useMemo(() => [...new Set(Object.keys(mat).map((k) => +k.split("|")[1]))].sort((a, b) => a - b), [mat]);
  const [km, setKm] = useState(15000);
  const [ms, setMs] = useState(60);
  const kmV = kms.includes(km) ? km : kms.includes(15000) ? 15000 : kms[0];
  const msV = mss.includes(ms) ? ms : mss.includes(60) ? 60 : mss[mss.length - 1];
  const precio = mat[`${kmV}|${msV}`];
  const ivaTxt = iva === "con" ? "IVA incluido" : "+ IVA · deducible";
  const msg = `Hola, me interesa el renting del ${name}: ${kmV / 1000}.000 km/año, ${msV} meses, ${precio} €/mes (${ivaTxt}).`;

  const chip = (on: boolean) =>
    cn(
      "mono flex flex-col items-center rounded-[10px] border px-3 py-2 text-[13px] font-extrabold transition-colors",
      on ? "border-orange bg-orange text-white" : "border-line bg-paper text-ink hover:border-orange",
    );

  return (
    <div className="rounded-xl2 border border-line bg-white p-5">
      <div className="mb-2 text-[11px] font-bold uppercase tracking-wider text-muted">Kilómetros / año</div>
      <div className="mb-3 flex flex-wrap gap-1.5">
        {kms.map((k) => (
          <button key={k} onClick={() => setKm(k)} className={chip(k === kmV)}>
            {k / 1000}k<small className="text-[9px] font-normal opacity-70">km</small>
          </button>
        ))}
      </div>
      <div className="mb-2 text-[11px] font-bold uppercase tracking-wider text-muted">Plazo</div>
      <div className="mb-3 flex flex-wrap gap-1.5">
        {mss.map((m) => (
          <button key={m} onClick={() => setMs(m)} className={chip(m === msV)}>
            {m}<small className="text-[9px] font-normal opacity-70">meses</small>
          </button>
        ))}
      </div>
      {hasCon && hasSin && (
        <Tabs value={iva} onValueChange={(v) => setIva(v as "con" | "sin")} className="mb-3 block">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="con">Con IVA</TabsTrigger>
            <TabsTrigger value="sin">Sin IVA</TabsTrigger>
          </TabsList>
        </Tabs>
      )}
      <div className="text-xs text-muted">Cuota desde</div>
      <div className="mono text-[46px] font-extrabold leading-none text-ink">
        {precio ?? "—"}
        <small className="text-base text-muted"> €/mes</small>
      </div>
      <div className="mb-3.5 mt-1 text-[12.5px] text-muted">Sin entrada · {ivaTxt}</div>
      <Button asChild size="lg" className="w-full">
        <a href={`mailto:mtiagconsulting@gmail.com?subject=${encodeURIComponent("Renting " + name)}&body=${encodeURIComponent(msg)}`}>
          <Mail size={17} /> Recibir esta oferta
        </a>
      </Button>
      <Button asChild variant="outline" size="lg" className="mt-2 w-full">
        <a href={`https://wa.me/34691766768?text=${encodeURIComponent(msg)}`} target="_blank" rel="noopener">
          <MessageCircle size={17} /> Pedir por WhatsApp
        </a>
      </Button>
    </div>
  );
}
