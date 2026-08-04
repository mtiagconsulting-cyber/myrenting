import Link from "next/link";
const nav = [
  { href: "/coches", label: "Coches" },
  { href: "/coches", label: "Ofertas" },
  { href: "/comparar", label: "Comparar" },
  { href: "/coches", label: "Por ciudad" },
  { href: "/guias", label: "Guías y consejos" },
];
export default function Header() {
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-line">
      <div className="mx-auto max-w-[1200px] px-6 h-[70px] flex items-center gap-8">
        <Link href="/" className="text-[23px] font-extrabold tracking-tight text-ink">
          my<span className="text-orange">renting</span>
        </Link>
        <nav className="flex gap-6">
          {nav.map((n, i) => (
            <Link key={i} href={n.href} className="text-[15px] font-medium text-body hover:text-ink">{n.label}</Link>
          ))}
        </nav>
        <div className="ml-auto flex items-center gap-5 text-[14.5px] font-semibold text-ink">
          <span>♡ Favoritos</span>
          <a href="tel:+34691766768" className="text-orange">☎ 691 766 768</a>
        </div>
      </div>
    </header>
  );
}
