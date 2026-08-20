"use client";

import Link from "next/link";
import { useSyncExternalStore } from "react";
import { ArrowRight, Heart } from "lucide-react";
import { offers } from "@/data/offers";
import { vehicles } from "@/data/vehicles";
import { emptyFavorites, getFavorites, subscribeFavorites } from "@/lib/favorites";
import { vehiclePublicPath } from "@/lib/vehicle-groups";

export function FavoritesList() {
  const favoriteIds = useSyncExternalStore(subscribeFavorites, getFavorites, () => emptyFavorites);
  const favorites = vehicles.filter((vehicle) => favoriteIds.includes(vehicle.id));

  if (!favorites.length) return <div className="text-center"><span className="mx-auto grid size-14 place-items-center rounded-full bg-orange-50 text-brand"><Heart size={24} aria-hidden="true" /></span><h1 className="font-display mt-5 text-3xl font-semibold tracking-[-0.04em] text-ink">Aún no has guardado coches</h1><p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-muted">Explora el catálogo y utiliza el corazón de cada vehículo para preparar tu selección.</p><Link href="/coches" className="mt-6 inline-flex min-h-12 items-center rounded-lg bg-brand px-5 text-sm font-bold text-white hover:bg-brand-hover">Explorar coches</Link></div>;

  return <div className="w-full"><h1 className="font-display text-4xl font-semibold tracking-[-0.05em] text-ink">Tus coches favoritos</h1><p className="mt-3 text-sm text-muted">{favorites.length} {favorites.length === 1 ? "coche guardado" : "coches guardados"} en este dispositivo.</p><div className="mt-8 grid gap-4 sm:grid-cols-2">{favorites.map((vehicle) => { const offer = offers.find((item) => item.vehicleId === vehicle.id); return <Link key={vehicle.id} href={vehiclePublicPath(vehicle)} className="group rounded-xl border border-line bg-surface p-5"><p className="text-xs font-bold text-muted">{vehicle.brand}</p><h2 className="font-display mt-1 text-2xl font-semibold text-ink">{vehicle.model}</h2><div className="mt-5 flex items-end justify-between"><p className="font-data text-2xl font-semibold text-ink">{offer?.monthlyPrice} €<span className="font-sans text-xs text-muted">/mes</span></p><ArrowRight size={17} className="transition-transform group-hover:translate-x-1" aria-hidden="true" /></div></Link>; })}</div></div>;
}
