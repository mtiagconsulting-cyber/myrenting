"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import { trackJourneyPageView } from "@/lib/analytics";

function pageType(path: string) {
  if (path === "/") return "home";
  if (path === "/coches") return "vehicle_catalogue";
  if (path.startsWith("/coches/")) return "vehicle_detail";
  if (path.startsWith("/modelos/")) return "model_landing";
  if (path.startsWith("/marcas/")) return "brand_landing";
  if (path === "/renting" || path.startsWith("/renting/")) return "renting_landing";
  if (path.startsWith("/blog/")) return "blog_article";
  if (path.startsWith("/comparar/")) return "comparison";
  return "content_page";
}

export function JourneyTracker() {
  const pathname = usePathname();

  useEffect(() => {
    trackJourneyPageView(pathname, pageType(pathname));
  }, [pathname]);

  return null;
}
