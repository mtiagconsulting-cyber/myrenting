import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

export const metadata: Metadata = {
  metadataBase: new URL("https://myrenting.es"),
  title: { default: "myrenting · El comparador de renting de coches de España", template: "%s | myrenting" },
  description: "Comparamos ofertas reales de renting de coches de varias gestoras. Cuota exacta por km y plazo, con o sin IVA, sin entrada y sin registro.",
  openGraph: { type: "website", locale: "es_ES", siteName: "myrenting" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="font-sans antialiased">
        <Header />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}
