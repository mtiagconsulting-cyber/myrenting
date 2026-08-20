import { inventoryUpdatedAt, offers } from "@/data/offers";
import { vehicles } from "@/data/vehicles";
import { contentSlug } from "@/lib/content-slug";
import { canonicalVehicles, vehicleGroupKey, vehiclesInSameGroup } from "@/lib/vehicle-groups";
import type { Offer, OfferAudience } from "@/types/offer";
import type { BodyType, DgtLabel, FuelType, Vehicle } from "@/types/vehicle";

export const SEO_MIN_OFFERS = Number(process.env.SEO_MIN_OFFERS ?? 3);
export const SEO_MIN_VEHICLES = Number(process.env.SEO_MIN_VEHICLES ?? 1);

export const cityWhitelist = ["madrid", "barcelona", "valencia", "sevilla", "malaga", "zaragoza", "bilbao", "alicante"] as const;
const cityNames: Record<(typeof cityWhitelist)[number], string> = { madrid: "Madrid", barcelona: "Barcelona", valencia: "Valencia", sevilla: "Sevilla", malaga: "Málaga", zaragoza: "Zaragoza", bilbao: "Bilbao", alicante: "Alicante" };
const audienceNames: Record<OfferAudience, string> = { particular: "particulares", autonomo: "autónomos", empresa: "empresas" };
const audienceSlugs: Record<OfferAudience, string> = { particular: "particulares", autonomo: "autonomos", empresa: "empresas" };
const priceThresholds = [200, 250, 300, 350, 400, 500] as const;

export type SeoLandingFamily = "renting" | "brands" | "models" | "categories" | "prices" | "cities";
export type SeoLandingType =
  | "root" | "audience" | "brand" | "model" | "price" | "cheap" | "no_entry" | "immediate"
  | "body" | "fuel" | "label" | "automatic" | "duration" | "city"
  | "brand_intent" | "model_intent" | "body_intent" | "fuel_intent" | "audience_intent";

export interface SeoLandingFilters {
  brand?: string;
  model?: string;
  audience?: OfferAudience;
  maxPrice?: number;
  noEntry?: boolean;
  immediate?: boolean;
  bodyTypes?: BodyType[];
  fuels?: FuelType[];
  label?: DgtLabel;
  automatic?: boolean;
  duration?: number;
  minimumSeats?: number;
  fourWheelDrive?: boolean;
}

export interface SeoLandingStats {
  offerCount: number;
  vehicleCount: number;
  modelCount: number;
  brandCount: number;
  minimumPrice: number;
  maximumPrice: number;
  cheapestVehicle: string;
  durations: number[];
  kilometers: number[];
  fuels: string[];
  transmissions: string[];
}

export interface SeoLanding {
  slug: string;
  family: SeoLandingFamily;
  type: SeoLandingType;
  dimensions: Record<string, string | number | boolean>;
  filters: SeoLandingFilters;
  title: string;
  h1: string;
  description: string;
  summary: string;
  idealFor: string;
  canonical: string;
  indexable: boolean;
  inventoryCount: number;
  minimumPrice: number | null;
  updatedAt: string;
  stats: SeoLandingStats | null;
}

type VehicleOffer = { vehicle: Vehicle; offer: Offer };
const vehicleById = new Map(vehicles.map((vehicle) => [vehicle.id, vehicle]));
const inventoryPairs: VehicleOffer[] = offers.flatMap((offer) => {
  const vehicle = vehicleById.get(offer.vehicleId);
  return vehicle ? [{ vehicle, offer }] : [];
});

const bodyTaxonomies = [
  { slug: "suv", label: "SUV", bodies: ["SUV"] as BodyType[] },
  { slug: "furgonetas", label: "furgonetas", bodies: ["Furgoneta"] as BodyType[] },
  { slug: "coches-pequenos", label: "coches pequeños", bodies: ["Compacto"] as BodyType[] },
  { slug: "familiares", label: "coches familiares", bodies: ["Familiar", "SUV", "Furgoneta"] as BodyType[] },
];
const fuelTaxonomies = [
  { slug: "electricos", label: "coches eléctricos", fuels: ["Eléctrico"] as FuelType[] },
  { slug: "hibridos", label: "coches híbridos", fuels: ["Híbrido"] as FuelType[] },
  { slug: "hibridos-enchufables", label: "híbridos enchufables", fuels: ["Híbrido enchufable"] as FuelType[] },
  { slug: "gasolina", label: "coches de gasolina", fuels: ["Gasolina"] as FuelType[] },
  { slug: "diesel", label: "coches diésel", fuels: ["Diésel"] as FuelType[] },
];

function matchesFilters({ vehicle, offer }: VehicleOffer, filters: SeoLandingFilters) {
  return (!filters.brand || vehicle.brand === filters.brand)
    && (!filters.model || vehicle.model === filters.model)
    && (!filters.audience || offer.audience === filters.audience)
    && (!filters.maxPrice || offer.monthlyPrice <= filters.maxPrice)
    && (!filters.noEntry || offer.initialPayment === 0)
    && (!filters.immediate || offer.availability === "Disponible")
    && (!filters.bodyTypes || filters.bodyTypes.includes(vehicle.bodyType))
    && (!filters.fuels || filters.fuels.includes(vehicle.fuel))
    && (!filters.label || vehicle.label === filters.label)
    && (!filters.automatic || /auto|dsg|cvt|dct|stronic|automatic/i.test(vehicle.transmission ?? vehicle.version))
    && (!filters.duration || offer.duration === filters.duration)
    && (!filters.minimumSeats || (vehicle.seats ?? 0) >= filters.minimumSeats)
    && (!filters.fourWheelDrive || /4x4|awd|4wd/i.test(vehicle.version));
}

export function getLandingPairs(landing: Pick<SeoLanding, "filters">) {
  return inventoryPairs.filter((pair) => matchesFilters(pair, landing.filters));
}

export function offerMatchesLanding(offer: Offer, filters: SeoLandingFilters) {
  return (!filters.audience || offer.audience === filters.audience)
    && (!filters.maxPrice || offer.monthlyPrice <= filters.maxPrice)
    && (!filters.noEntry || offer.initialPayment === 0)
    && (!filters.immediate || offer.availability === "Disponible")
    && (!filters.duration || offer.duration === filters.duration);
}

function getStats(filters: SeoLandingFilters): SeoLandingStats | null {
  const pairs = inventoryPairs.filter((pair) => matchesFilters(pair, filters));
  if (!pairs.length) return null;
  const sorted = [...pairs].sort((first, second) => first.offer.monthlyPrice - second.offer.monthlyPrice);
  return {
    offerCount: pairs.length,
    vehicleCount: new Set(pairs.map(({ vehicle }) => vehicleGroupKey(vehicle))).size,
    modelCount: new Set(pairs.map(({ vehicle }) => `${vehicle.brand}|${vehicle.model}`)).size,
    brandCount: new Set(pairs.map(({ vehicle }) => vehicle.brand)).size,
    minimumPrice: sorted[0].offer.monthlyPrice,
    maximumPrice: sorted.at(-1)!.offer.monthlyPrice,
    cheapestVehicle: `${sorted[0].vehicle.brand} ${sorted[0].vehicle.model}`,
    durations: [...new Set(pairs.map(({ offer }) => offer.duration))].sort((a, b) => a - b),
    kilometers: [...new Set(pairs.map(({ offer }) => offer.kilometers))].sort((a, b) => a - b),
    fuels: [...new Set(pairs.map(({ vehicle }) => vehicle.fuel))].sort((a, b) => a.localeCompare(b, "es")),
    transmissions: [...new Set(pairs.map(({ vehicle }) => vehicle.transmission).filter((value): value is string => Boolean(value)))].sort((a, b) => a.localeCompare(b, "es")),
  };
}

function makeLanding(input: Omit<SeoLanding, "canonical" | "indexable" | "inventoryCount" | "minimumPrice" | "updatedAt" | "stats"> & { authorized?: boolean; minVehicles?: number }): SeoLanding {
  const stats = getStats(input.filters);
  const authorized = input.authorized ?? true;
  const indexable = authorized && Boolean(stats && stats.offerCount >= SEO_MIN_OFFERS && stats.vehicleCount >= (input.minVehicles ?? SEO_MIN_VEHICLES));
  return { ...input, canonical: input.slug, indexable, inventoryCount: stats?.offerCount ?? 0, minimumPrice: stats?.minimumPrice ?? null, updatedAt: inventoryUpdatedAt, stats };
}

function price(value: number | null) { return value === null ? "—" : value.toLocaleString("es-ES", { maximumFractionDigits: 2 }); }

function basicLanding({ slug, family, type, dimensions = {}, filters = {}, title, h1, noun, idealFor, authorized, minVehicles }: { slug: string; family: SeoLandingFamily; type: SeoLandingType; dimensions?: Record<string, string | number | boolean>; filters?: SeoLandingFilters; title: string; h1: string; noun: string; idealFor: string; authorized?: boolean; minVehicles?: number }) {
  const stats = getStats(filters);
  const minimum = price(stats?.minimumPrice ?? null);
  return makeLanding({ slug, family, type, dimensions, filters, title: `${title} | Ofertas desde ${minimum} €/mes`, h1, description: `Compara ${stats?.offerCount ?? 0} ofertas de ${noun} desde ${minimum} €/mes. Consulta modelos, duración, kilometraje, entrada, IVA y disponibilidad.`, summary: `Compara ${stats?.offerCount ?? 0} configuraciones de ${noun} correspondientes a ${stats?.vehicleCount ?? 0} vehículos y ${stats?.modelCount ?? 0} modelos. La cuota publicada más baja parte de ${minimum} €/mes.`, idealFor, authorized, minVehicles });
}

const brandNames = [...new Map(vehicles.map((vehicle) => [contentSlug(vehicle.brand), vehicle.brand])).entries()];
const modelNames = [...new Map(vehicles.map((vehicle) => [`${contentSlug(vehicle.brand)}/${contentSlug(vehicle.model)}`, { brand: vehicle.brand, model: vehicle.model }])).entries()];

const primary: SeoLanding[] = [
  basicLanding({ slug: "/renting", family: "renting", type: "root", title: "Renting de coches", h1: "Renting de coches", noun: "renting de coches", idealFor: "Quien quiere comparar en un único lugar las campañas activas para particulares, autónomos y empresas." }),
  ...(["particular", "autonomo", "empresa"] as OfferAudience[]).map((audience) => basicLanding({ slug: `/renting/${audienceSlugs[audience]}`, family: "renting", type: "audience", dimensions: { audience }, filters: { audience }, title: `Renting para ${audienceNames[audience]}`, h1: `Renting para ${audienceNames[audience]}`, noun: `renting para ${audienceNames[audience]}`, idealFor: `Clientes que necesitan consultar exclusivamente cuotas destinadas a ${audienceNames[audience]}.` })),
  ...brandNames.map(([, brand]) => basicLanding({ slug: `/renting/${contentSlug(brand)}`, family: "brands", type: "brand", dimensions: { brand }, filters: { brand }, title: `Renting ${brand}`, h1: `Ofertas de renting ${brand}`, noun: `renting ${brand}`, idealFor: `Quien quiere comparar todos los modelos y versiones ${brand} disponibles.`, minVehicles: 1 })),
  ...modelNames.map(([, { brand, model }]) => basicLanding({ slug: `/renting/${contentSlug(brand)}/${contentSlug(model)}`, family: "models", type: "model", dimensions: { brand, model }, filters: { brand, model }, title: `Renting ${brand} ${model}`, h1: `Renting ${brand} ${model}`, noun: `renting ${brand} ${model}`, idealFor: `Quien ya ha elegido el ${brand} ${model} y quiere comparar sus versiones y condiciones.` })),
  basicLanding({ slug: "/renting/baratos", family: "prices", type: "cheap", title: "Renting barato", h1: "Coches de renting baratos", noun: "renting barato", idealFor: "Quien prioriza encontrar las cuotas más bajas del inventario actual." }),
  ...priceThresholds.map((maxPrice) => basicLanding({ slug: `/renting/menos-de-${maxPrice}-euros`, family: "prices", type: "price", dimensions: { maxPrice }, filters: { maxPrice }, title: `Renting por menos de ${maxPrice} euros`, h1: `Renting por menos de ${maxPrice} €`, noun: `renting hasta ${maxPrice} euros`, idealFor: `Quien necesita mantener su cuota mensual por debajo de ${maxPrice} euros.` })),
  basicLanding({ slug: "/renting/sin-entrada", family: "prices", type: "no_entry", filters: { noEntry: true }, title: "Renting sin entrada", h1: "Renting sin entrada", noun: "renting sin entrada", idealFor: "Quien quiere contratar sin realizar un desembolso inicial." }),
  basicLanding({ slug: "/renting/entrega-inmediata", family: "prices", type: "immediate", filters: { immediate: true }, title: "Renting con entrega inmediata", h1: "Coches de renting con entrega inmediata", noun: "renting con disponibilidad", idealFor: "Quien necesita reducir el plazo de espera y puede adaptarse al stock disponible." }),
  ...bodyTaxonomies.map((item) => basicLanding({ slug: `/renting/${item.slug}`, family: "categories", type: "body", dimensions: { body: item.slug }, filters: { bodyTypes: item.bodies }, title: `Renting de ${item.label}`, h1: `Renting de ${item.label}`, noun: `renting de ${item.label}`, idealFor: `Quien busca específicamente ${item.label} y quiere comparar sus cuotas y condiciones.` })),
  ...fuelTaxonomies.map((item) => basicLanding({ slug: `/renting/${item.slug}`, family: "categories", type: "fuel", dimensions: { fuel: item.slug }, filters: { fuels: item.fuels }, title: `Renting de ${item.label}`, h1: `Renting de ${item.label}`, noun: `renting de ${item.label}`, idealFor: `Quien prioriza una motorización ${item.label} al elegir su próximo vehículo.` })),
  basicLanding({ slug: "/renting/etiqueta-eco", family: "categories", type: "label", dimensions: { label: "ECO" }, filters: { label: "ECO" }, title: "Renting con etiqueta ECO", h1: "Renting con etiqueta ECO", noun: "renting con distintivo ECO", idealFor: "Quien busca ventajas ambientales y de movilidad urbana sin pasar necesariamente a un eléctrico." }),
  basicLanding({ slug: "/renting/etiqueta-cero", family: "categories", type: "label", dimensions: { label: "0" }, filters: { label: "0" }, title: "Renting con etiqueta Cero", h1: "Renting con etiqueta Cero", noun: "renting con distintivo Cero", idealFor: "Quien busca un vehículo eléctrico o enchufable con distintivo Cero." }),
  basicLanding({ slug: "/renting/automaticos", family: "categories", type: "automatic", filters: { automatic: true }, title: "Renting de coches automáticos", h1: "Coches automáticos de renting", noun: "coches automáticos de renting", idealFor: "Quien prioriza comodidad de conducción y quiere excluir versiones manuales." }),
  basicLanding({ slug: "/renting/7-plazas", family: "categories", type: "body", filters: { minimumSeats: 7 }, title: "Renting de coches de 7 plazas", h1: "Coches de renting de 7 plazas", noun: "coches de 7 plazas", idealFor: "Familias y profesionales que necesitan siete plazas homologadas.", minVehicles: 2 }),
  basicLanding({ slug: "/renting/4x4", family: "categories", type: "body", filters: { fourWheelDrive: true }, title: "Renting de coches 4x4 y AWD", h1: "Coches 4x4 de renting", noun: "vehículos 4x4 y AWD", idealFor: "Quien necesita tracción total por uso, climatología o tipo de recorrido.", minVehicles: 2 }),
  ...[12, 24, 36, 48, 60].map((duration) => basicLanding({ slug: `/renting/${duration}-meses`, family: "categories", type: "duration", dimensions: { duration }, filters: { duration }, title: `Renting a ${duration} meses`, h1: `Renting de coches a ${duration} meses`, noun: `renting a ${duration} meses`, idealFor: `Quien quiere comparar exclusivamente contratos con una duración de ${duration} meses.` })),
  ...cityWhitelist.map((city) => ({ ...basicLanding({ slug: `/renting/${city}`, family: "cities", type: "city", dimensions: { city }, title: `Renting en ${cityNames[city]}`, h1: `Renting en ${cityNames[city]}`, noun: `renting en ${cityNames[city]}`, idealFor: `Usuarios de ${cityNames[city]} que necesitan confirmar cobertura y entrega con cada proveedor.`, authorized: false }), title: `Renting en ${cityNames[city]} | Cobertura en preparación`, description: `Página preparada para mostrar renting en ${cityNames[city]} cuando exista cobertura territorial verificable.`, summary: `Estamos preparando esta selección. No publicaremos ofertas como disponibles en ${cityNames[city]} hasta confirmar la cobertura y las condiciones de entrega de cada proveedor.`, stats: null, inventoryCount: 0, minimumPrice: null })),
];

const brandIntent: SeoLanding[] = brandNames.flatMap(([, brand]) => [
  basicLanding({ slug: `/renting/${contentSlug(brand)}/baratos`, family: "prices", type: "brand_intent", dimensions: { brand, intent: "cheap" }, filters: { brand }, title: `Renting ${brand} barato`, h1: `Ofertas baratas de renting ${brand}`, noun: `renting ${brand} barato`, idealFor: `Quien busca la cuota más baja disponible dentro de la gama ${brand}.`, minVehicles: 2 }),
  ...priceThresholds.map((maxPrice) => basicLanding({ slug: `/renting/${contentSlug(brand)}/menos-de-${maxPrice}-euros`, family: "prices", type: "brand_intent", dimensions: { brand, maxPrice }, filters: { brand, maxPrice }, title: `Renting ${brand} por menos de ${maxPrice} euros`, h1: `Renting ${brand} por menos de ${maxPrice} €`, noun: `renting ${brand} hasta ${maxPrice} euros`, idealFor: `Quien quiere un ${brand} sin superar ${maxPrice} euros mensuales.`, minVehicles: 2 })),
  basicLanding({ slug: `/renting/${contentSlug(brand)}/sin-entrada`, family: "prices", type: "brand_intent", dimensions: { brand, intent: "no_entry" }, filters: { brand, noEntry: true }, title: `Renting ${brand} sin entrada`, h1: `Renting ${brand} sin entrada`, noun: `renting ${brand} sin entrada`, idealFor: `Quien quiere contratar un ${brand} sin pago inicial.`, minVehicles: 2 }),
  basicLanding({ slug: `/renting/${contentSlug(brand)}/entrega-inmediata`, family: "prices", type: "brand_intent", dimensions: { brand, intent: "immediate" }, filters: { brand, immediate: true }, title: `Renting ${brand} con entrega inmediata`, h1: `${brand} de renting con entrega disponible`, noun: `renting ${brand} disponible`, idealFor: `Quien necesita un ${brand} con el menor plazo de entrega posible.`, minVehicles: 2 }),
]);

const modelIntent: SeoLanding[] = modelNames.flatMap(([, { brand, model }]) => [
  basicLanding({ slug: `/renting/${contentSlug(brand)}/${contentSlug(model)}/barato`, family: "prices", type: "model_intent", dimensions: { brand, model, intent: "cheap" }, filters: { brand, model }, title: `Renting ${brand} ${model} barato`, h1: `Renting ${brand} ${model} barato`, noun: `renting ${brand} ${model}`, idealFor: `Quien busca la configuración más económica disponible del ${brand} ${model}.` }),
  basicLanding({ slug: `/renting/${contentSlug(brand)}/${contentSlug(model)}/sin-entrada`, family: "prices", type: "model_intent", dimensions: { brand, model, intent: "no_entry" }, filters: { brand, model, noEntry: true }, title: `Renting ${brand} ${model} sin entrada`, h1: `${brand} ${model} de renting sin entrada`, noun: `renting ${brand} ${model} sin entrada`, idealFor: `Quien quiere un ${brand} ${model} sin desembolso inicial.` }),
  basicLanding({ slug: `/renting/${contentSlug(brand)}/${contentSlug(model)}/entrega-inmediata`, family: "prices", type: "model_intent", dimensions: { brand, model, intent: "immediate" }, filters: { brand, model, immediate: true }, title: `Renting ${brand} ${model} con entrega inmediata`, h1: `${brand} ${model} con entrega disponible`, noun: `renting ${brand} ${model} disponible`, idealFor: `Quien busca unidades disponibles del ${brand} ${model}.` }),
]);

const taxonomyIntent: SeoLanding[] = [
  ...bodyTaxonomies.flatMap((item) => [
    basicLanding({ slug: `/renting/${item.slug}/baratos`, family: "prices", type: "body_intent", dimensions: { body: item.slug, intent: "cheap" }, filters: { bodyTypes: item.bodies }, title: `Renting de ${item.label} baratos`, h1: `${item.label} baratos de renting`, noun: `${item.label} baratos de renting`, idealFor: `Quien busca las cuotas más económicas dentro de ${item.label}.`, minVehicles: 2 }),
    ...priceThresholds.map((maxPrice) => basicLanding({ slug: `/renting/${item.slug}/menos-de-${maxPrice}-euros`, family: "prices", type: "body_intent", dimensions: { body: item.slug, maxPrice }, filters: { bodyTypes: item.bodies, maxPrice }, title: `Renting de ${item.label} por menos de ${maxPrice} euros`, h1: `${item.label} por menos de ${maxPrice} €`, noun: `${item.label} hasta ${maxPrice} euros`, idealFor: `Quien busca ${item.label} dentro de un presupuesto máximo de ${maxPrice} euros.`, minVehicles: 2 })),
    basicLanding({ slug: `/renting/${item.slug}/sin-entrada`, family: "prices", type: "body_intent", dimensions: { body: item.slug, intent: "no_entry" }, filters: { bodyTypes: item.bodies, noEntry: true }, title: `Renting de ${item.label} sin entrada`, h1: `${item.label} de renting sin entrada`, noun: `${item.label} sin entrada`, idealFor: `Quien necesita ${item.label} sin realizar un pago inicial.`, minVehicles: 2 }),
    basicLanding({ slug: `/renting/${item.slug}/entrega-inmediata`, family: "prices", type: "body_intent", dimensions: { body: item.slug, intent: "immediate" }, filters: { bodyTypes: item.bodies, immediate: true }, title: `Renting de ${item.label} con entrega inmediata`, h1: `${item.label} con entrega disponible`, noun: `${item.label} disponibles`, idealFor: `Quien necesita ${item.label} con el menor plazo posible.`, minVehicles: 2 }),
  ]),
  ...fuelTaxonomies.flatMap((item) => [
    basicLanding({ slug: `/renting/${item.slug}/baratos`, family: "prices", type: "fuel_intent", dimensions: { fuel: item.slug, intent: "cheap" }, filters: { fuels: item.fuels }, title: `Renting de ${item.label} baratos`, h1: `${item.label} baratos de renting`, noun: `${item.label} baratos`, idealFor: `Quien prioriza ${item.label} y busca la cuota más económica.`, minVehicles: 2 }),
    ...priceThresholds.map((maxPrice) => basicLanding({ slug: `/renting/${item.slug}/menos-de-${maxPrice}-euros`, family: "prices", type: "fuel_intent", dimensions: { fuel: item.slug, maxPrice }, filters: { fuels: item.fuels, maxPrice }, title: `Renting de ${item.label} por menos de ${maxPrice} euros`, h1: `${item.label} por menos de ${maxPrice} €`, noun: `${item.label} hasta ${maxPrice} euros`, idealFor: `Quien quiere ${item.label} sin superar ${maxPrice} euros mensuales.`, minVehicles: 2 })),
    basicLanding({ slug: `/renting/${item.slug}/sin-entrada`, family: "prices", type: "fuel_intent", dimensions: { fuel: item.slug, intent: "no_entry" }, filters: { fuels: item.fuels, noEntry: true }, title: `Renting de ${item.label} sin entrada`, h1: `${item.label} de renting sin entrada`, noun: `${item.label} sin entrada`, idealFor: `Quien busca ${item.label} sin desembolso inicial.`, minVehicles: 2 }),
  ]),
  ...(["particular", "autonomo", "empresa"] as OfferAudience[]).flatMap((audience) => [
    basicLanding({ slug: `/renting/${audienceSlugs[audience]}/baratos`, family: "prices", type: "audience_intent", dimensions: { audience, intent: "cheap" }, filters: { audience }, title: `Renting barato para ${audienceNames[audience]}`, h1: `Renting barato para ${audienceNames[audience]}`, noun: `renting barato para ${audienceNames[audience]}`, idealFor: `Quien busca la cuota más baja destinada específicamente a ${audienceNames[audience]}.`, minVehicles: 2 }),
    basicLanding({ slug: `/renting/${audienceSlugs[audience]}/sin-entrada`, family: "prices", type: "audience_intent", dimensions: { audience, intent: "no_entry" }, filters: { audience, noEntry: true }, title: `Renting sin entrada para ${audienceNames[audience]}`, h1: `Renting sin entrada para ${audienceNames[audience]}`, noun: `renting sin entrada para ${audienceNames[audience]}`, idealFor: `Quien necesita una tarifa para ${audienceNames[audience]} sin pago inicial.`, minVehicles: 2 }),
  ]),
];

const unique = new Map<string, SeoLanding>();
for (const landing of [...primary, ...brandIntent, ...modelIntent, ...taxonomyIntent]) if (!unique.has(landing.slug)) unique.set(landing.slug, landing);
export const seoLandings = [...unique.values()];
export const indexableSeoLandings = seoLandings.filter((landing) => landing.indexable);
export const preparedNoindexLandings = seoLandings.filter((landing) => !landing.indexable);

export function findSeoLanding(segments: string[] = []) {
  const slug = `/renting${segments.length ? `/${segments.join("/")}` : ""}`;
  return seoLandings.find((landing) => landing.slug === slug);
}

export function landingVehicles(landing: SeoLanding) {
  const pairs = getLandingPairs(landing);
  const ids = new Set(pairs.map(({ vehicle }) => vehicle.id));
  return canonicalVehicles(vehicles.filter((vehicle) => ids.has(vehicle.id) || vehiclesInSameGroup(vehicle, vehicles).some((candidate) => ids.has(candidate.id))));
}
