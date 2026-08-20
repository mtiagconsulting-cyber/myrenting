import fs from "node:fs";

const input = process.argv.find((value) => value.startsWith("--input="))?.split("=")[1] ?? "docs/seo-geo/plantilla-medicion.csv";
const output = process.argv.find((value) => value.startsWith("--output="))?.split("=")[1];

function parseCsv(text) {
  const rows = []; let row = []; let field = ""; let quoted = false;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index]; const next = text[index + 1];
    if (char === '"' && quoted && next === '"') { field += '"'; index += 1; }
    else if (char === '"') quoted = !quoted;
    else if (char === "," && !quoted) { row.push(field); field = ""; }
    else if ((char === "\n" || char === "\r") && !quoted) { if (char === "\r" && next === "\n") index += 1; row.push(field); if (row.some(Boolean)) rows.push(row); row = []; field = ""; }
    else field += char;
  }
  if (field || row.length) { row.push(field); rows.push(row); }
  const [headers, ...values] = rows; return values.map((valuesRow) => Object.fromEntries(headers.map((header, index) => [header, valuesRow[index] ?? ""])));
}
const truthy = (value) => ["1", "true", "si", "sí", "yes"].includes(String(value).trim().toLowerCase());
const rows = parseCsv(fs.readFileSync(input, "utf8")).filter((row) => row.query_id && row.motor);
const summarize = (list) => ({ observations: list.length, mentions: list.filter((row) => truthy(row.menciona_myrenting)).length, citations: list.filter((row) => truthy(row.cita_myrenting)).length, correctAnswers: list.filter((row) => truthy(row.respuesta_correcta)).length, mentionShare: list.length ? Number((100 * list.filter((row) => truthy(row.menciona_myrenting)).length / list.length).toFixed(2)) : 0, citationShare: list.length ? Number((100 * list.filter((row) => truthy(row.cita_myrenting)).length / list.length).toFixed(2)) : 0 });
const engines = [...new Set(rows.map((row) => row.motor))];
const queryCounts = new Map(); for (const row of rows) queryCounts.set(row.query_id, (queryCounts.get(row.query_id) ?? 0) + 1);
const result = { generatedAt: new Date().toISOString(), targetObservations: 300, completeQueries: [...queryCounts.values()].filter((count) => count >= 3).length, incompleteQueries: [...queryCounts.values()].filter((count) => count < 3).length, total: summarize(rows), byEngine: Object.fromEntries(engines.map((engine) => [engine, summarize(rows.filter((row) => row.motor === engine))])) };
const rendered = `${JSON.stringify(result, null, 2)}\n`;
if (output) fs.writeFileSync(output, rendered); else process.stdout.write(rendered);
if (rows.length < 300) console.error(`AVISO: faltan ${300 - rows.length} observaciones para el benchmark mensual completo.`);
