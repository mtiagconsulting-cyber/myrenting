import Image from "next/image";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

const categories = [
  { label: "SUV", href: "/renting/suv", image: "/images/home/suv.webp", position: "center 64%" },
  { label: "Familiares", href: "/categorias/familiares", image: "/images/home/familiares.webp", position: "center 54%" },
  { label: "Urbanos", href: "/categorias/urbanos", image: "/images/home/urbanos.webp", position: "center 58%" },
  { label: "Eléctricos", href: "/renting/electricos", image: "/images/home/electricos.webp", position: "center 55%" },
  { label: "Híbridos", href: "/renting/hibridos", image: "/images/home/hibridos.webp", position: "center 55%" },
  { label: "Empresas", href: "/categorias/empresas", image: "/images/home/empresas.webp", position: "center 55%" },
];

export function CategoryGrid() {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
      {categories.map((category) => (
        <Link key={category.label} href={category.href} className="group relative aspect-[4/5] overflow-hidden rounded-xl bg-ink">
          <Image
            src={category.image}
            alt=""
            fill
            quality={60}
            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 17vw"
            className="object-cover opacity-80 transition duration-500 group-hover:scale-[1.03] group-hover:opacity-70"
            style={{ objectPosition: category.position }}
          />
          <span className="absolute inset-x-2 bottom-2 flex items-center justify-between rounded-lg bg-ink/90 p-3 text-white">
            <span className="font-display text-lg font-semibold tracking-[-0.03em]">{category.label}</span>
            <ArrowUpRight size={17} aria-hidden="true" />
          </span>
        </Link>
      ))}
    </div>
  );
}
