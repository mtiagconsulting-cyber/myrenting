"use client";

import { useSyncExternalStore } from "react";
import { Heart } from "lucide-react";
import { cn } from "@/lib/utils";
import { emptyFavorites, getFavorites, subscribeFavorites, toggleFavorite } from "@/lib/favorites";

export function FavoriteButton({ vehicleId, vehicleName, className }: { vehicleId: string; vehicleName: string; className?: string }) {
  const favorites = useSyncExternalStore(subscribeFavorites, getFavorites, () => emptyFavorites);
  const active = favorites.includes(vehicleId);
  return <button type="button" onClick={() => toggleFavorite(vehicleId)} aria-pressed={active} className={cn("grid size-11 place-items-center rounded-full bg-white text-copy shadow-sm transition-colors hover:text-brand", active && "text-brand", className)} aria-label={active ? `Quitar ${vehicleName} de favoritos` : `Guardar ${vehicleName} en favoritos`}><Heart size={18} fill={active ? "currentColor" : "none"} aria-hidden="true" /></button>;
}
