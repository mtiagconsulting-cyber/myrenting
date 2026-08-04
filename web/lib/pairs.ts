import { vehicles } from "./data";
const s = (t: string) => vehicles.find(v => v.title === t)?.slug;
const raw = [
  ["Renault Captur","Toyota Yaris"],["Hyundai Tucson","Opel Frontera"],
  ["Peugeot 208","Opel Corsa"],["Mazda 3","Toyota Yaris"],
];
export const pairs = raw.map(([a,b]) => [s(a), s(b)]).filter(p => p[0] && p[1]) as [string,string][];
export function pairSlug(a: string, b: string) { return `${a}-vs-${b}`; }
export function parsePair(slug: string): [string,string] | null {
  const i = slug.indexOf("-vs-"); if (i < 0) return null;
  return [slug.slice(0,i), slug.slice(i+4)];
}
