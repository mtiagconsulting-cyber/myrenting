import type { Metadata } from "next";
import { FavoritesList } from "@/components/vehicles/FavoritesList";

export const metadata: Metadata = { title: "Coches favoritos", robots: { index: false, follow: true } };

export default function FavoritesPage() {
  return <main id="contenido-principal" className="mx-auto grid min-h-[60vh] max-w-3xl place-items-center px-5 py-12 sm:px-8"><FavoritesList /></main>;
}
