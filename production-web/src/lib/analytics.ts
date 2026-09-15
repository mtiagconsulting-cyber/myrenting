"use client";

export function trackAnalyticsEvent(event: string, details: Record<string, unknown> = {}) {
  if (typeof window === "undefined") return;
  const analyticsWindow = window as typeof window & {
    dataLayer?: Array<Record<string, unknown>>;
    gtag?: (command: "event", eventName: string, parameters: Record<string, unknown>) => void;
  };
  const dataLayer = analyticsWindow.dataLayer ?? [];
  let attribution: Record<string, unknown> = {};
  try { attribution = JSON.parse(window.sessionStorage.getItem("myrenting_attribution") ?? "{}"); } catch {}
  const parameters = { ...details, ...attribution, page_path: window.location.pathname };
  dataLayer.push({ event, ...parameters });
  analyticsWindow.dataLayer = dataLayer;
  analyticsWindow.gtag?.("event", event, parameters);
}
