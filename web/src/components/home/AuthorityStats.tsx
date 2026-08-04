import { vehicles } from "@/data/vehicles";
import { offers } from "@/data/offers";

// Cifras HONESTAS derivadas de los datos reales (nada inventado).
const modelos = vehicles.length;
const gestoras = new Set(vehicles.flatMap((v) => v.fuentes)).size;
const precios = offers.reduce((n, o) => n + Object.keys(o.matrix).length, 0);

const stats: [string, string][] = [
  [String(modelos), "Modelos comparados"],
  [precios.toLocaleString("es-ES"), "Precios reales"],
  [String(gestoras), "Gestoras oficiales"],
  ["Semanal", "Actualización"],
  ["0€", "De entrada"],
];

export default function AuthorityStats() {
  return (
    <section className="py-7">
      <div className="grid grid-cols-2 overflow-hidden rounded-xl2 border border-line bg-white md:grid-cols-5">
        {stats.map(([n, l], i) => (
          <div key={i} className="border-r border-line p-6 text-center last:border-0">
            <div className="text-[26px] font-extrabold tracking-tight text-orange">{n}</div>
            <div className="mt-1 text-[12.5px] text-muted">{l}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
