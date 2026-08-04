"use client";
import { useMemo, useState } from "react";
import type { VehicleMatrices } from "@/lib/types";

export default function Configurator({ name, matrices }: { name: string; matrices: VehicleMatrices }) {
  const hasCon = !!matrices["particular"];
  const hasSin = !!(matrices["empresa"] || matrices["autonomo"]);
  const [iva, setIva] = useState<"con" | "sin">(hasCon ? "con" : "sin");
  const mat = (iva === "con" ? matrices["particular"] : (matrices["empresa"] || matrices["autonomo"])) || {};
  const kms = useMemo(() => [...new Set(Object.keys(mat).map(k => +k.split("|")[0]))].sort((a,b)=>a-b), [mat]);
  const mss = useMemo(() => [...new Set(Object.keys(mat).map(k => +k.split("|")[1]))].sort((a,b)=>a-b), [mat]);
  const [km, setKm] = useState(15000);
  const [ms, setMs] = useState(60);
  const kmV = kms.includes(km) ? km : (kms.includes(15000) ? 15000 : kms[0]);
  const msV = mss.includes(ms) ? ms : (mss.includes(60) ? 60 : mss[mss.length-1]);
  const precio = mat[`${kmV}|${msV}`];
  const ivaTxt = iva === "con" ? "IVA incluido" : "+ IVA · deducible";
  const msg = `Hola, me interesa el renting del ${name}: ${kmV/1000}.000 km/año, ${msV} meses, ${precio} €/mes (${ivaTxt}).`;
  const chip = (on: boolean) => `cursor-pointer rounded-[10px] px-3 py-2 font-extrabold text-[13px] mono flex flex-col items-center border ${on ? "bg-orange border-orange text-white" : "bg-paper border-line text-ink"}`;

  return (
    <div className="bg-white border border-line rounded-xl2 p-5">
      <div className="text-[11px] uppercase tracking-wider text-muted font-bold mb-2">Kilómetros / año</div>
      <div className="flex gap-1.5 flex-wrap mb-3">
        {kms.map(k => <button key={k} onClick={()=>setKm(k)} className={chip(k===kmV)}>{k/1000}k<small className="text-[9px] font-normal opacity-70">km</small></button>)}
      </div>
      <div className="text-[11px] uppercase tracking-wider text-muted font-bold mb-2">Plazo</div>
      <div className="flex gap-1.5 flex-wrap mb-3">
        {mss.map(m => <button key={m} onClick={()=>setMs(m)} className={chip(m===msV)}>{m}<small className="text-[9px] font-normal opacity-70">meses</small></button>)}
      </div>
      {(hasCon && hasSin) && (
        <div className="flex bg-paper border border-line rounded-[10px] p-[3px] gap-[3px] mb-3">
          {(["con","sin"] as const).map(x => (
            <button key={x} onClick={()=>setIva(x)} className={`flex-1 rounded-[7px] py-2 text-[12px] font-bold ${iva===x?"bg-orange text-white":"text-muted"}`}>{x==="con"?"Con IVA":"Sin IVA"}</button>
          ))}
        </div>
      )}
      <div className="text-xs text-muted">Cuota desde</div>
      <div className="mono text-[46px] font-extrabold text-ink leading-none">{precio ?? "—"}<small className="text-base text-muted"> €/mes</small></div>
      <div className="text-[12.5px] text-muted mt-1 mb-3.5">Sin entrada · {ivaTxt}</div>
      <a href={`mailto:mtiagconsulting@gmail.com?subject=${encodeURIComponent("Renting "+name)}&body=${encodeURIComponent(msg)}`} className="block text-center font-bold text-white bg-orange rounded-[11px] py-3.5 hover:bg-orange-dark">Recibir esta oferta</a>
      <a href={`https://wa.me/34691766768?text=${encodeURIComponent(msg)}`} target="_blank" rel="noopener" className="block text-center font-bold text-ink border border-line rounded-[11px] py-3.5 mt-2">Pedir por WhatsApp</a>
    </div>
  );
}
