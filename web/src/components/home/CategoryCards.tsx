import Link from "next/link";
import { vehicles, byFuel } from "@/data/vehicles";

const pickImg = (title: string) => vehicles.find((v) => v.title === title)?.img;

type Cat = { name: string; sub: string; href: string; img?: string };

const cats: Cat[] = [
  { name: "SUV", sub: "Espacio y versatilidad", href: "/categorias/suv", img: pickImg("Hyundai Tucson") },
  { name: "Familiares", sub: "Comodidad para todos", href: "/categorias/familiar", img: pickImg("Seat Leon") },
  { name: "Urbanos", sub: "Ágiles y eficientes", href: "/categorias/urbano", img: pickImg("Peugeot 208") },
  { name: "Eléctricos", sub: "Cero emisiones", href: "/renting-electricos", img: byFuel("electricos").find((v) => v.img)?.img },
  { name: "Empresas y autónomos", sub: "Deducible y flexible", href: "/coches?perfil=empresa", img: pickImg("Citroen Berlingo") },
];

export default function CategoryCards() {
  return (
    <section className="py-7">
      <h2 className="mb-[18px] text-[clamp(23px,2.4vw,30px)] font-extrabold text-ink">
        Explora por lo que necesitas
      </h2>
      <div className="grid grid-cols-2 gap-3.5 md:grid-cols-6">
        {cats.map((c, i) => (
          <Link
            key={i}
            href={c.href}
            className="flex min-h-[158px] flex-col overflow-hidden rounded-xl2 border border-line bg-white px-4 pb-0 pt-[18px] transition hover:border-orange hover:shadow-card"
          >
            <b className="text-[15px] text-ink">{c.name}</b>
            <span className="text-xs text-muted">{c.sub}</span>
            {c.img && <img src={c.img} alt={c.name} className="mt-auto h-[70px] w-full object-contain" />}
          </Link>
        ))}
        <div className="flex flex-col rounded-xl2 border border-[#ffdcc2] bg-orange-soft p-[18px]">
          <b className="text-[15px] text-ink">¿No sabes qué elegir?</b>
          <p className="my-1.5 text-[12.5px] leading-snug text-body">
            Te ayudamos a encontrar el coche ideal según tu caso en menos de 1 minuto.
          </p>
          <Link
            href="/coches"
            className="mt-auto rounded-[10px] bg-orange py-2.5 text-center text-[13px] font-bold text-white hover:bg-orange-dark"
          >
            Ayúdame a elegir ›
          </Link>
        </div>
      </div>
    </section>
  );
}
