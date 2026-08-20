import type { Metadata } from "next";
import type { ReactNode } from "react";
import Script from "next/script";
import { Footer } from "@/components/layout/Footer";
import { Header } from "@/components/layout/Header";
import { MobileNav } from "@/components/layout/MobileNav";
import { OrganizationSchema } from "@/components/seo/Schema";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "https://myrenting.es"),
  title: {
    default: "Renting de coches para particulares, autónomos y empresas | MyRenting",
    template: "%s | MyRenting",
  },
  description: "Compara ofertas reales de renting por cuota, plazo, kilómetros, IVA y coberturas. Vehículos para particulares, autónomos y empresas en España.",
  applicationName: "MyRenting",
  alternates: { canonical: "/" },
  robots: { index: true, follow: true, googleBot: { index: true, follow: true, "max-image-preview": "large", "max-snippet": -1, "max-video-preview": -1 } },
  openGraph: { type: "website", locale: "es_ES", url: "/", siteName: "MyRenting", title: "Renting de coches con cuotas y condiciones claras | MyRenting", description: "Compara renting para particulares, autónomos y empresas por precio, plazo, kilómetros, IVA y servicios incluidos." },
  twitter: { card: "summary_large_image", title: "MyRenting — compara renting con datos claros", description: "Ofertas de renting separadas por perfil, cuota, plazo, kilómetros e IVA." },
  icons: { icon: [{ url: "/icon.svg", type: "image/svg+xml" }], shortcut: "/icon.svg", apple: "/apple-icon.svg" },
  manifest: "/manifest.webmanifest",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="es">
      <head>
        <Script
          src="https://analytics.ahrefs.com/analytics.js"
          data-key="KCyPMjxyHSaiZ+zV3HZzqA"
          strategy="afterInteractive"
        />
        <Script id="ai-attribution" strategy="beforeInteractive">{`(function(w,d){try{var p=new URLSearchParams(w.location.search),u=p.get('utm_source')||'',r=d.referrer||'',h=r?new URL(r).hostname.toLowerCase():'';var sources=[['chatgpt','ChatGPT'],['openai','ChatGPT'],['perplexity','Perplexity'],['gemini','Gemini'],['bard.google','Gemini'],['copilot','Microsoft Copilot'],['bing','Microsoft Copilot'],['claude','Claude']];var found=sources.find(function(x){return h.indexOf(x[0])>-1||u.toLowerCase().indexOf(x[0])>-1});var data={traffic_channel:found?'AI Assistants':'Other',ai_source:found?found[1]:'',landing_page_path:w.location.pathname,referring_domain:h,campaign_source:u};w.dataLayer=w.dataLayer||[];w.dataLayer.push(Object.assign({event:'traffic_attribution'},data));try{w.sessionStorage.setItem('myrenting_attribution',JSON.stringify(data));}catch(storageError){}}catch(e){}})(window,document);`}</Script>
        <Script id="gtm" strategy="afterInteractive">{`(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','GTM-NHXGQF97');`}</Script>
      </head>
      <body>
        <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-NHXGQF97" height="0" width="0" style={{ display: "none", visibility: "hidden" }} title="Google Tag Manager" /></noscript>
        <OrganizationSchema />
        <a
          href="#contenido-principal"
          className="fixed top-3 left-3 z-[100] -translate-y-20 rounded-lg bg-ink px-4 py-3 text-sm font-bold text-white transition-transform focus:translate-y-0"
        >
          Saltar al contenido
        </a>
        <Header />
        <MobileNav />
        {children}
        <Footer />
      </body>
    </html>
  );
}
