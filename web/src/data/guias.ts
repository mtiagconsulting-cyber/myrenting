export type GuiaSection = { h: string; body: string };
export type Guia = {
  slug: string;
  title: string;
  description: string;
  intro: string;
  updated: string;
  sections: GuiaSection[];
  faq: { q: string; a: string }[];
};

export const guias: Guia[] = [
  {
    slug: "que-incluye-el-renting",
    title: "¿Qué incluye la cuota de renting?",
    description:
      "Qué cubre exactamente la cuota mensual de un renting de coche: seguro, mantenimiento, neumáticos, impuestos y qué NO está incluido.",
    intro:
      "El renting es un alquiler a largo plazo con todo incluido: pagas una cuota fija al mes y la gestora se encarga de casi todo. Pero conviene saber con precisión qué cubre esa cuota y qué queda fuera.",
    updated: "2026-08-01",
    sections: [
      {
        h: "Qué incluye la cuota",
        body: "La cuota mensual suele incluir: seguro a todo riesgo, mantenimiento y averías, cambio de neumáticos, impuestos (matriculación e IVTM), asistencia en carretera 24 h y gestión de multas. Todo ello sin entrada inicial en la mayoría de ofertas.",
      },
      {
        h: "Qué NO incluye",
        body: "No incluye el combustible ni la recarga eléctrica, las sanciones de tráfico (se gestionan pero las paga el conductor), ni los daños no cubiertos por el seguro (por ejemplo, negligencia grave). El coche tampoco es tuyo al final: se devuelve.",
      },
      {
        h: "Kilómetros y plazo",
        body: "La cuota depende de dos variables clave: los kilómetros contratados al año (habitualmente de 10.000 a 30.000) y el plazo en meses (36, 48 o 60). A más kilómetros o menos meses, mayor cuota. Si te pasas de los km pactados, se cobra un exceso por kilómetro.",
      },
    ],
    faq: [
      { q: "¿El seguro está incluido?", a: "Sí, la cuota incluye seguro a todo riesgo en la práctica totalidad de las ofertas de renting." },
      { q: "¿Puedo quedarme el coche al final?", a: "En el renting el coche se devuelve al terminar el contrato. Si quieres comprarlo, existe el renting con opción de compra, pero no es lo habitual." },
    ],
  },
  {
    slug: "renting-vs-compra",
    title: "Renting vs comprar un coche: ¿qué compensa?",
    description:
      "Comparativa honesta entre renting, financiación y compra al contado: costes, flexibilidad, propiedad y para quién compensa cada opción.",
    intro:
      "No hay una respuesta universal: depende de cuánto conduzcas, cuántos años quieras el coche y si valoras la propiedad o la comodidad de tener todo incluido. Vamos por partes.",
    updated: "2026-08-01",
    sections: [
      {
        h: "Cuándo compensa el renting",
        body: "El renting encaja si prefieres una cuota fija con todo incluido, cambiar de coche cada 3-5 años y no preocuparte por seguro, mantenimiento ni valor de reventa. Es especialmente eficiente para autónomos y empresas por la deducción fiscal.",
      },
      {
        h: "Cuándo compensa comprar",
        body: "Comprar (al contado o financiado) compensa si vas a tener el coche muchos años, haces muchos kilómetros o valoras que el vehículo sea tuyo. A largo plazo, un coche amortizado puede salir más barato por mes que renovarlo constantemente.",
      },
      {
        h: "El factor propiedad",
        body: "En el renting nunca eres propietario: al final devuelves el coche. En la compra el coche es un activo tuyo, pero asumes su depreciación, que es el mayor coste oculto de tener coche.",
      },
    ],
    faq: [
      { q: "¿El renting es más caro que comprar?", a: "Depende del horizonte. A 3-4 años el renting suele ser competitivo con todo incluido; a 8-10 años un coche comprado y amortizado tiende a salir más barato por mes." },
      { q: "¿El renting deja historial de propiedad?", a: "No. Al no ser propietario, el coche no figura como un activo tuyo ni genera valor de reventa a tu favor." },
    ],
  },
  {
    slug: "renting-para-autonomos",
    title: "Renting para autónomos y empresas: IVA y deducción",
    description:
      "Cómo funciona el renting para autónomos y empresas: deducción del IVA, gasto deducible en IRPF/Sociedades y por qué la cuota se muestra sin IVA.",
    intro:
      "Para autónomos y empresas el renting tiene ventajas fiscales claras. Por eso en myrenting mostramos la cuota con IVA (particular) y sin IVA (empresa o autónomo): son bases distintas.",
    updated: "2026-08-01",
    sections: [
      {
        h: "Deducción del IVA",
        body: "Un autónomo puede deducir con carácter general el 50 % del IVA de la cuota si el vehículo tiene uso mixto (profesional y personal), y hasta el 100 % si acredita uso exclusivamente profesional. Las empresas siguen reglas equivalentes.",
      },
      {
        h: "Gasto deducible",
        body: "La cuota de renting es gasto deducible en el IRPF (estimación directa) o en el Impuesto de Sociedades, en el porcentaje de afectación a la actividad. Esto reduce la base imponible y, por tanto, los impuestos a pagar.",
      },
      {
        h: "Por qué mostramos cuota sin IVA",
        body: "Cuando eliges el perfil empresa o autónomo, la cuota se muestra sin IVA porque esa es la referencia relevante para tu contabilidad. El particular ve la cuota con IVA incluido, que es lo que realmente paga.",
      },
    ],
    faq: [
      { q: "¿Cuánto IVA puede deducir un autónomo?", a: "Con carácter general el 50 % en uso mixto, y hasta el 100 % si se acredita uso exclusivamente profesional. Conviene consultarlo con tu asesor." },
      { q: "¿La cuota de renting desgrava?", a: "Sí, es gasto deducible en IRPF o Sociedades según el porcentaje de afectación a la actividad económica." },
    ],
  },
  {
    slug: "etiquetas-dgt",
    title: "Etiquetas DGT: 0, ECO, C y B explicadas",
    description:
      "Qué significan las etiquetas medioambientales de la DGT (CERO, ECO, C, B), qué coches las tienen y cómo afectan a las zonas de bajas emisiones.",
    intro:
      "La etiqueta ambiental de la DGT clasifica los coches por sus emisiones y determina el acceso a las zonas de bajas emisiones (ZBE) de las grandes ciudades. Elegir bien la etiqueta evita restricciones.",
    updated: "2026-08-01",
    sections: [
      {
        h: "Etiqueta CERO (azul)",
        body: "La más favorable. Para eléctricos puros, híbridos enchufables con más de 40 km de autonomía eléctrica y de pila de combustible. Acceso libre a las ZBE y máximas ventajas de aparcamiento.",
      },
      {
        h: "Etiqueta ECO (verde/azul)",
        body: "Para híbridos, híbridos enchufables de menor autonomía, gas (GLP/GNC) y algunos micro-híbridos. Acceso a las ZBE con pocas restricciones. Es el punto dulce entre coste y libertad de circulación.",
      },
      {
        h: "Etiquetas C y B",
        body: "La C es para gasolina desde 2006 y diésel desde 2015 (Euro 6). La B para gasolina desde 2001 y diésel desde 2006. Ambas pueden tener restricciones crecientes en las ZBE según la ciudad y el año.",
      },
    ],
    faq: [
      { q: "¿Qué etiqueta necesito para entrar en una ZBE?", a: "Depende de la ciudad, pero las etiquetas CERO y ECO tienen acceso garantizado o con mínimas restricciones. Las C y B afrontan limitaciones crecientes." },
      { q: "¿Los híbridos tienen etiqueta ECO?", a: "La mayoría sí. Los eléctricos puros tienen CERO, y muchos micro-híbridos obtienen ECO o C según el modelo." },
    ],
  },
];

export function getGuia(slug: string) {
  return guias.find((g) => g.slug === slug);
}
