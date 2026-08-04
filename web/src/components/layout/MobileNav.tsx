import Link from "next/link";
import { Home, Car, Columns3, Heart, Menu } from "lucide-react";

const items = [
  { href: "/", label: "Inicio", Icon: Home },
  { href: "/coches", label: "Coches", Icon: Car },
  { href: "/comparar", label: "Comparar", Icon: Columns3 },
  { href: "/coches", label: "Favoritos", Icon: Heart },
  { href: "/guias", label: "Más", Icon: Menu },
];

export default function MobileNav() {
  return (
    <nav className="md:hidden fixed bottom-0 inset-x-0 z-50 bg-white border-t border-line grid grid-cols-5 pb-[env(safe-area-inset-bottom)]">
      {items.map(({ href, label, Icon }, i) => (
        <Link key={i} href={href} className="flex flex-col items-center gap-0.5 py-2 text-[10.5px] font-medium text-body hover:text-orange">
          <Icon size={20} strokeWidth={2} />
          {label}
        </Link>
      ))}
    </nav>
  );
}
