"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function SearchBox() {
  const router = useRouter();
  const [q, setQ] = useState("");
  const [max, setMax] = useState("");
  const [km, setKm] = useState("");

  function submit() {
    const p = new URLSearchParams();
    if (q.trim()) p.set("q", q.trim());
    if (max) p.set("max", max);
    if (km) p.set("km", km);
    router.push(`/coches${p.toString() ? `?${p}` : ""}`);
  }

  return (
    <div className="mt-7 grid gap-1 rounded-xl2 border border-line bg-white p-2.5 shadow-card md:grid-cols-[1.5fr_1fr_1fr_auto]">
      <label className="flex flex-col px-3.5 py-2.5">
        <span className="mb-0.5 text-[11.5px] font-semibold text-muted">¿Qué coche necesitas?</span>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="Marca, modelo o tipo…"
          className="w-full bg-transparent text-[14.5px] font-semibold text-ink outline-none placeholder:font-medium placeholder:text-muted"
        />
      </label>
      <div className="flex flex-col px-3.5 py-2.5">
        <span className="mb-0.5 text-[11.5px] font-semibold text-muted">Presupuesto</span>
        <Select value={max} onValueChange={setMax}>
          <SelectTrigger className="h-auto border-0 bg-transparent p-0 text-[14.5px] focus:ring-0">
            <SelectValue placeholder="Máx. €/mes" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="300">Hasta 300 €</SelectItem>
            <SelectItem value="400">Hasta 400 €</SelectItem>
            <SelectItem value="500">Hasta 500 €</SelectItem>
            <SelectItem value="700">Hasta 700 €</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="flex flex-col px-3.5 py-2.5">
        <span className="mb-0.5 text-[11.5px] font-semibold text-muted">Km al año</span>
        <Select value={km} onValueChange={setKm}>
          <SelectTrigger className="h-auto border-0 bg-transparent p-0 text-[14.5px] focus:ring-0">
            <SelectValue placeholder="Todos" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="10000">10.000 km</SelectItem>
            <SelectItem value="15000">15.000 km</SelectItem>
            <SelectItem value="20000">20.000 km</SelectItem>
            <SelectItem value="30000">30.000 km</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <Button onClick={submit} size="lg" className="md:h-full">
        <Search size={17} /> Buscar ofertas
      </Button>
    </div>
  );
}
