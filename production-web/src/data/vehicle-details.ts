export interface VehicleEditorial {
  summary: string;
  idealFor: string;
  strengths: string[];
  consider: string;
  faqs: Array<{ question: string; answer: string }>;
}

interface EditorialContext {
  bodyType: string;
  power: number;
  transmission?: string | null;
  trunk: number | null;
  label: string;
}

const defaultFaqs = (name: string) => [
  { question: `¿Qué incluye el renting del ${name}?`, answer: "La oferta mostrada incluye seguro y mantenimiento. La cobertura de neumáticos depende del proveedor y aparece indicada en las condiciones." },
  { question: "¿La cuota requiere entrada?", answer: "La entrada se muestra junto a la cuota. Conviene comparar el coste total del contrato, no solo el importe mensual." },
  { question: "¿Puedo cambiar los kilómetros anuales?", answer: "Los proveedores suelen ofrecer varios tramos de kilometraje. Cambiar los kilómetros puede modificar la cuota mensual." },
];

export const vehicleEditorial: Record<string, VehicleEditorial> = {
  "toyota-corolla": { summary: "Un familiar híbrido eficiente, con espacio útil y una conducción orientada al confort diario.", idealFor: "Familias y conductores que recorren ciudad y carretera, valoran un consumo contenido y necesitan un maletero amplio.", strengths: ["Consumo contenido", "Maletero de 596 litros", "Etiqueta ECO"], consider: "Su carrocería familiar ocupa más que un compacto en ciudad.", faqs: defaultFaqs("Toyota Corolla") },
  "kia-niro": { summary: "SUV híbrido compacto que combina una posición de conducción elevada con buen aprovechamiento interior.", idealFor: "Quien busca un SUV manejable para uso mixto, buen maletero y acceso a zonas de bajas emisiones.", strengths: ["Formato SUV compacto", "Maletero de 451 litros", "Etiqueta ECO"], consider: "Ofrece menos maletero que un familiar grande como el Corolla Touring Sports.", faqs: defaultFaqs("Kia Niro") },
  "bmw-serie-1": { summary: "Compacto premium de enfoque dinámico, con tamaño contenido y motor de gasolina microhíbrido.", idealFor: "Conductores que priorizan tacto de conducción, acabados y facilidad de uso urbano.", strengths: ["170 CV", "Tamaño compacto", "Etiqueta ECO"], consider: "La cuota es más alta que la de compactos generalistas equivalentes.", faqs: defaultFaqs("BMW Serie 1") },
  "audi-a3": { summary: "Compacto premium equilibrado, con una presentación cuidada y buen comportamiento en carretera.", idealFor: "Quien busca un compacto refinado para trayectos diarios y viajes, sin pasar a una berlina más grande.", strengths: ["Motor de 150 CV", "Formato versátil", "Acabado S line"], consider: "Esta versión de gasolina tiene etiqueta C y requiere entrada en la oferta mostrada.", faqs: defaultFaqs("Audi A3") },
  "tesla-model-3": { summary: "Berlina eléctrica eficiente, potente y especialmente adecuada para quien puede cargar con regularidad.", idealFor: "Conductores con punto de carga disponible que realizan recorridos frecuentes y quieren pasar a un eléctrico.", strengths: ["Consumo eléctrico contenido", "Gran capacidad de carga", "Etiqueta 0"], consider: "Antes de contratar conviene comprobar la infraestructura de carga habitual y las condiciones de entrega.", faqs: defaultFaqs("Tesla Model 3") },
  "bmw-i4": { summary: "Berlina eléctrica premium con prestaciones elevadas, buena autonomía de uso y portón trasero práctico.", idealFor: "Quien busca un eléctrico premium para viajar y valora potencia, confort y acabado por encima de la cuota mínima.", strengths: ["286 CV", "Maletero de 470 litros", "Etiqueta 0"], consider: "Es la cuota más alta del inventario actual y la oferta requiere entrada.", faqs: defaultFaqs("BMW i4") },
};

export function getVehicleEditorial(slug: string, name: string, fuel: string, context?: EditorialContext): VehicleEditorial {
  if (vehicleEditorial[slug]) return vehicleEditorial[slug];
  const bodyUse: Record<string, string> = {
    SUV: "una posición de conducción elevada y un habitáculo versátil para combinar ciudad y desplazamientos largos",
    Compacto: "un tamaño manejable para el uso diario sin renunciar a viajar con comodidad",
    Berlina: "confort y estabilidad para quien realiza trayectos frecuentes por carretera",
    Furgoneta: "capacidad de carga y una configuración práctica para actividad profesional",
    Familiar: "espacio de carga y comodidad para viajes o necesidades familiares",
  };
  const fuelUse: Record<string, string> = {
    Eléctrico: "dispone de carga habitual y quiere conducir con etiqueta CERO",
    Híbrido: "alterna ciudad y carretera y valora la etiqueta ECO sin depender de un enchufe",
    "Híbrido enchufable": "puede cargar con frecuencia y quiere cubrir parte de sus trayectos cotidianos en modo eléctrico",
    Gasolina: "busca una mecánica conocida para recorridos variados y un coste de acceso contenido",
    "Diésel": "realiza kilometraje frecuente, especialmente por carretera",
  };
  const body = context?.bodyType ?? "vehículo";
  const transmission = context?.transmission?.toLowerCase().includes("auto") ? "Cambio automático" : "Cambio manual";
  const strengths = [
    context?.power ? `${context.power} CV de potencia` : `Motorización ${fuel.toLowerCase()}`,
    body === "Furgoneta" ? "Configuración orientada a carga" : `${body} para uso diario`,
    context?.trunk ? `Maletero de ${context.trunk} litros` : context?.label ? `Etiqueta ${context.label}` : transmission,
  ];
  return {
    summary: `${name} es un ${body.toLowerCase()} ${fuel.toLowerCase()} disponible con distintas combinaciones de plazo y kilometraje verificadas.`,
    idealFor: `Encaja con quien busca ${bodyUse[body] ?? "un vehículo para uso cotidiano"} y ${fuelUse[fuel] ?? `prefiere una motorización ${fuel.toLowerCase()}`}.`,
    strengths,
    consider: body === "Furgoneta" ? "Comprueba que la longitud, altura y carga útil se ajusten al uso profesional previsto." : fuel === "Eléctrico" ? "Antes de contratar, confirma dónde cargarás habitualmente y qué autonomía necesitas en tus recorridos reales." : fuel === "Híbrido enchufable" ? "Su ventaja depende de poder cargarlo con regularidad; sin carga frecuente aumenta el consumo de combustible." : `Compara el espacio disponible, el consumo y el coste total con otros ${body.toLowerCase()} de potencia similar.`,
    faqs: defaultFaqs(name),
  };
}
