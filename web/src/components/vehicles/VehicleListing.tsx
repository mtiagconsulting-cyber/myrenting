"use client";
import { useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { SlidersHorizontal, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { vehicles, sortedByPrice } from "@/data/vehicles";
import { getMatrices } from "@/data/offers";
import type { Vehicle } from "@/types";

/* ---------- facetas ---------- */
type Bucket = { label: string; match: (v: Vehicle) => boolean };

function fuelBucket(v: Vehicle): string {
  const f = v.fuel.toLowerCase();
  if (f.includes("eléctr")) return "Eléctrico";
  if (f.includes("híbr") || f.includes("hibr")) return "Híbrido";
  if (f.includes("diés") || f.includes("dies")) return "Diésel";
  if (f.includes("gasolina")) return "Gasolina";
  return "Otro";
}

const CARROCERIA: Record<string, string[]> = {
  SUV: ["SUV", "Crossover"],
  Urbano: ["Urbano", "Hatchback"],
  Familiar: ["Familiar", "Berlina con portón", "Sedán"],
  Furgoneta: ["Furgoneta", "Furgón", "LCV"],
};

function carroceriaBucket(v: Vehicle): string | null {
  for (const [b, cats] of Object.entries(CARROCERIA)) if (cats.includes(v.category)) return b;
  return null;
}

/** ¿el vehículo tiene alguna oferta para un perfil concreto? */
function hasPerfil(v: Vehicle, perfil: string): boolean {
  const m = getMatrices(v.slug);
  if (!m) return false;
  if (perfil === "empresa") return !!(m.empresa || m.autonomo);
  return !!m[perfil as keyof typeof m];
}

/** ¿tiene el vehículo una combinación con estos km? */
function hasKm(v: Vehicle, km: number): boolean {
  const m = getMatrices(v.slug);
  if (!m) return false;
  return Object.values(m).some((mat) => mat && Object.keys(mat).some((k) => +k.split("|")[0] === km));
}

/* facetas con conteo (>0) derivadas de los datos */
function facet(count: (v: Vehicle) => string | null, order?: string[]): { label: string; n: number }[] {
  const m = new Map<string, number>();
  for (const v of vehicles) {
    const k = count(v);
    if (k && k !== "Otro") m.set(k, (m.get(k) ?? 0) + 1);
  }
  let entries = [...m.entries()];
  if (order) entries.sort((a, b) => order.indexOf(a[0]) - order.indexOf(b[0]));
  else entries.sort((a, b) => b[1] - a[1]);
  return entries.map(([label, n]) => ({ label, n }));
}

const FUELS = facet(fuelBucket, ["Eléctrico", "Híbrido", "Gasolina", "Diésel"]);
const ETIQUETAS = facet((v) => (v.dgt && v.dgt !== "—" ? v.dgt : null), ["CERO", "ECO", "C", "B"]);
const CARROCERIAS = facet(carroceriaBucket, ["SUV", "Urbano", "Familiar", "Furgoneta"]);

/* ---------- componente ---------- */
type Sort = "precio-asc" | "precio-desc";

export default function VehicleListing() {
  const sp = useSearchParams();
  const initFuel = sp.get("fuel");
  const initCat = sp.get("cat");
  const perfil = sp.get("perfil") ?? "";
  const km = sp.get("km") ? Number(sp.get("km")) : 0;

  const [query, setQuery] = useState(sp.get("q") ?? "");
  const [fuels, setFuels] = useState<Set<string>>(new Set(labelFromSlug(initFuel, FUELS)));
  const [etiquetas, setEtiquetas] = useState<Set<string>>(new Set());
  const [carrocerias, setCarrocerias] = useState<Set<string>>(
    new Set(labelFromSlug(initCat, CARROCERIAS)),
  );
  const [maxPrice, setMaxPrice] = useState<number>(sp.get("max") ? Number(sp.get("max")) : 0);
  const [sort, setSort] = useState<Sort>("precio-asc");
  const [open, setOpen] = useState(false);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    let list = vehicles.filter((v) => {
      if (q && !`${v.title} ${v.version} ${v.make} ${v.model}`.toLowerCase().includes(q)) return false;
      if (fuels.size && !fuels.has(fuelBucket(v))) return false;
      if (etiquetas.size && !etiquetas.has(v.dgt)) return false;
      if (carrocerias.size) {
        const b = carroceriaBucket(v);
        if (!b || !carrocerias.has(b)) return false;
      }
      if (maxPrice && v.precio > maxPrice) return false;
      if (perfil && !hasPerfil(v, perfil)) return false;
      if (km && !hasKm(v, km)) return false;
      return true;
    });
    list = [...list].sort((a, b) => (sort === "precio-asc" ? a.precio - b.precio : b.precio - a.precio));
    return list;
  }, [query, fuels, etiquetas, carrocerias, maxPrice, perfil, km, sort]);

  const activeCount = fuels.size + etiquetas.size + carrocerias.size + (maxPrice ? 1 : 0);

  function toggle(set: Set<string>, setter: (s: Set<string>) => void, val: string) {
    const next = new Set(set);
    next.has(val) ? next.delete(val) : next.add(val);
    setter(next);
  }
  function clearAll() {
    setFuels(new Set());
    setEtiquetas(new Set());
    setCarrocerias(new Set());
    setMaxPrice(0);
    setQuery("");
  }

  const Controls = (
    <div className="text-[13.5px]">
      <FacetGroup title="Combustible">
        {FUELS.map((f) => (
          <CheckRow key={f.label} label={f.label} n={f.n} checked={fuels.has(f.label)} onChange={() => toggle(fuels, setFuels, f.label)} />
        ))}
      </FacetGroup>
      <FacetGroup title="Etiqueta DGT">
        {ETIQUETAS.map((e) => (
          <CheckRow key={e.label} label={e.label} n={e.n} checked={etiquetas.has(e.label)} onChange={() => toggle(etiquetas, setEtiquetas, e.label)} />
        ))}
      </FacetGroup>
      <FacetGroup title="Carrocería">
        {CARROCERIAS.map((c) => (
          <CheckRow key={c.label} label={c.label} n={c.n} checked={carrocerias.has(c.label)} onChange={() => toggle(carrocerias, setCarrocerias, c.label)} />
        ))}
      </FacetGroup>
      <FacetGroup title="Precio máximo">
        <div className="flex items-center gap-3 pt-1">
          <input
            type="range"
            min={250}
            max={1250}
            step={50}
            value={maxPrice || 1250}
            onChange={(e) => setMaxPrice(Number(e.target.value) >= 1250 ? 0 : Number(e.target.value))}
            className="w-full accent-orange"
          />
          <span className="mono w-[74px] shrink-0 text-right text-[13px] font-bold text-ink">
            {maxPrice ? `${maxPrice} €` : "Todos"}
          </span>
        </div>
      </FacetGroup>
      {activeCount > 0 && (
        <button onClick={clearAll} className="mt-4 flex items-center gap-1 text-[13px] font-semibold text-orange">
          <X size={14} /> Limpiar filtros
        </button>
      )}
    </div>
  );

  return (
    <div className="mt-5 grid items-start gap-6 md:grid-cols-[250px_1fr]">
      {/* sidebar desktop */}
      <aside className="sticky top-[84px] hidden rounded-xl2 border border-line bg-white p-[18px] md:block">
        {Controls}
      </aside>

      <div>
        {/* barra búsqueda + orden + filtros(móvil) */}
        <div className="mb-3.5 flex flex-wrap items-center gap-3">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar marca o modelo…"
            className="h-10 flex-1 rounded-lg border border-line bg-white px-3.5 text-[14px] font-semibold text-ink outline-none placeholder:font-medium placeholder:text-muted focus-visible:ring-2 focus-visible:ring-ring"
          />
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value as Sort)}
            className="h-10 rounded-lg border border-line bg-white px-3 text-[13.5px] font-semibold text-ink"
          >
            <option value="precio-asc">Precio ↑</option>
            <option value="precio-desc">Precio ↓</option>
          </select>
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <Button variant="outline" size="sm" className="md:hidden">
                <SlidersHorizontal size={15} /> Filtros{activeCount ? ` (${activeCount})` : ""}
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-[85%] overflow-y-auto sm:max-w-sm">
              <SheetHeader>
                <SheetTitle>Filtros</SheetTitle>
              </SheetHeader>
              <div className="p-5">{Controls}</div>
              <div className="sticky bottom-0 border-t border-line bg-white p-4">
                <Button className="w-full" onClick={() => setOpen(false)}>
                  Ver {results.length} coches
                </Button>
              </div>
            </SheetContent>
          </Sheet>
        </div>

        <div className="mb-3.5 text-sm text-muted">
          <b className="text-ink">{results.length}</b> {results.length === 1 ? "coche" : "coches"}
        </div>

        {results.length === 0 && (
          <div className="rounded-xl2 border border-line bg-white p-8 text-center text-muted">
            No hay coches con estos filtros.{" "}
            <button onClick={clearAll} className="font-semibold text-orange">Limpiar</button>
          </div>
        )}

        {results.map((v) => (
          <Link
            key={v.slug}
            href={`/coches/${v.slug}`}
            className="mb-3.5 grid items-center gap-5 rounded-xl2 border border-line bg-white p-4 transition hover:border-orange hover:shadow-card md:grid-cols-[190px_1fr_210px]"
          >
            <div className="grid aspect-[16/11] place-items-center rounded-[10px] bg-paper">
              {v.img && <img src={v.img} alt={v.title} className="h-[90%] w-[94%] object-contain" />}
            </div>
            <div>
              <div className="text-lg font-semibold text-ink">{v.title}</div>
              <div className="mb-2 mt-0.5 text-[13px] text-muted">{v.fuel}</div>
              <div className="flex flex-wrap gap-1.5">
                {[v.cv, v.seats, v.cons, v.dgt && v.dgt !== "—" ? "Etiqueta " + v.dgt : ""]
                  .filter((x) => x && x !== "—")
                  .map((x, i) => (
                    <Badge key={i} variant="neutral">{x}</Badge>
                  ))}
              </div>
            </div>
            <div className="text-right">
              <div className="text-[11px] text-muted">desde</div>
              <div className="mono text-[26px] font-extrabold text-ink">
                {v.precio}
                <small className="text-xs font-bold text-muted"> €/mes</small>
              </div>
              <div className="mb-3 text-[11px] text-muted">sin entrada</div>
              <span className="inline-block rounded-[11px] bg-orange px-[18px] py-3 text-sm font-bold text-white">
                Ver ofertas
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

/* ---------- subcomponentes UI ---------- */
function FacetGroup({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mt-4 first:mt-0">
      <h4 className="mb-2 text-[11px] uppercase tracking-wide text-muted">{title}</h4>
      {children}
    </div>
  );
}

function CheckRow({ label, n, checked, onChange }: { label: string; n: number; checked: boolean; onChange: () => void }) {
  return (
    <label className="flex cursor-pointer items-center gap-2 py-1 text-ink">
      <Checkbox checked={checked} onCheckedChange={onChange} />
      <span className="flex-1">{label}</span>
      <span className="text-[12px] text-muted">{n}</span>
    </label>
  );
}

const norm = (s: string) =>
  s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");

/** Casa un slug de URL (sin acentos) con la etiqueta real de una faceta. */
function labelFromSlug(slug: string | null, facetLabels: { label: string }[]): string[] {
  if (!slug) return [];
  const match = facetLabels.find((f) => norm(f.label) === norm(slug));
  return match ? [match.label] : [];
}
