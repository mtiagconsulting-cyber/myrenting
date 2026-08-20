import { ImageResponse } from "next/og";

export const alt = "MyRenting — compara renting con datos claros";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpenGraphImage() {
  return new ImageResponse(<div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column", justifyContent: "space-between", background: "#101828", color: "white", padding: "72px", fontFamily: "sans-serif" }}><div style={{ display: "flex", alignItems: "center", gap: "22px", fontSize: 42, fontWeight: 700 }}><div style={{ width: 72, height: 72, borderRadius: 18, display: "flex", alignItems: "center", justifyContent: "center", background: "#ff6a00" }}>M</div><span style={{ display: "flex" }}>My<span style={{ color: "#ff6a00" }}>Renting</span></span></div><div style={{ display: "flex", flexDirection: "column" }}><div style={{ maxWidth: 940, fontSize: 72, lineHeight: 1.02, letterSpacing: "-3px", fontWeight: 700 }}>Compara renting con cuotas y condiciones claras.</div><div style={{ marginTop: 28, color: "#cbd5e1", fontSize: 28 }}>Particulares · Autónomos · Empresas</div></div></div>, size);
}
