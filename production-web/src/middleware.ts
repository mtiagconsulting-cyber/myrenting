import { NextResponse, type NextRequest } from "next/server";

const legacyLandings: Record<string, string> = {
  "/renting-suv": "/renting/suv",
  "/renting-hibridos": "/renting/hibridos",
  "/renting-electricos": "/renting/electricos",
  "/renting-barato": "/renting/baratos",
  "/renting-sin-entrada": "/renting/sin-entrada",
  "/renting-entrega-inmediata": "/renting/entrega-inmediata",
  "/renting-autonomos": "/renting/autonomos",
  "/renting-automaticos": "/renting/automaticos",
  "/renting-etiqueta-eco": "/renting/etiqueta-eco",
  "/renting-etiqueta-cero": "/renting/etiqueta-cero",
  "/renting-furgonetas": "/renting/furgonetas",
  "/renting-menos-300-euros": "/renting/menos-de-300-euros",
  "/renting-menos-350-euros": "/renting/menos-de-400-euros",
  "/renting-menos-450-euros": "/renting/menos-de-500-euros",
  "/renting-menos-500-euros": "/renting/menos-de-500-euros",
  "/renting-menos-600-euros": "/renting/menos-de-500-euros",
  "/renting-menos-700-euros": "/renting/menos-de-500-euros",
};

function legacyDestination(pathname: string) {
  if (legacyLandings[pathname]) return legacyLandings[pathname];
  const segments = pathname.split("/").filter(Boolean);
  if (segments[0] === "marcas" && segments[1]) return `/renting/${segments[1]}`;
  if (segments[0] === "modelos" && segments[1] && segments[2]) return `/renting/${segments[1]}/${segments[2]}`;
  if (segments[0] === "categorias" && segments[2]) {
    return segments[2] === "particular" ? "/renting/particulares" : segments[2] === "autonomo" ? "/renting/autonomos" : "/renting/empresas";
  }
  if (segments[0] === "categorias" && segments[1]) {
    const categories: Record<string, string> = { suv: "/renting/suv", familiares: "/renting/familiares", urbanos: "/renting/coches-pequenos", berlinas: "/renting", empresas: "/renting/empresas" };
    return categories[segments[1]] ?? "/renting";
  }
  if (segments[0] === "combustibles" && segments[1]) return `/renting/${segments[1]}`;
  if (segments[0] === "renting" && segments.length >= 3) {
    const intent = segments.at(-1)!;
    if (["barato", "baratos", "sin-entrada", "entrega-inmediata"].includes(intent) || intent.startsWith("menos-de-")) {
      return `/${segments.slice(0, -1).join("/")}`;
    }
  }
  return null;
}

export function middleware(request: NextRequest) {
  const destination = legacyDestination(request.nextUrl.pathname);
  if (!destination || destination === request.nextUrl.pathname) return NextResponse.next();
  return NextResponse.redirect(new URL(destination, request.url), 308);
}

export const config = {
  matcher: ["/marcas/:path*", "/modelos/:path*", "/categorias/:path*", "/combustibles/:path*", "/renting-:path*", "/renting/:entity/:intent", "/renting/:brand/:model/:intent"],
};
