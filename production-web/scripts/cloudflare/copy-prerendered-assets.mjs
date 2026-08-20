import { link, mkdir, readFile, readdir, rm } from "node:fs/promises";
import { basename, dirname, join, relative } from "node:path";

const source = join(process.cwd(), ".next/server/app");
const destination = join(process.cwd(), ".open-next/assets");
const copied = [];

async function walk(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const absolute = join(directory, entry.name);
    if (entry.isDirectory()) {
      await walk(absolute);
      continue;
    }
    const sourceRelative = relative(source, absolute);
    const isPageAsset = /\.(html|rsc)$/.test(entry.name);
    const bodyRoute = entry.name.endsWith(".body") ? sourceRelative.replace(/\.body$/, "") : null;
    // Next writes metadata routes as `<route>.body`. Publish routes that have a
    // real extension (sitemap.xml, robots.txt, icon.svg, manifest.webmanifest)
    // under their public filename so crawlers never invoke the Worker.
    const isMetadataAsset = Boolean(bodyRoute && basename(bodyRoute).includes("."));
    if (!isPageAsset && !isMetadataAsset) continue;
    const target = join(destination, bodyRoute ?? sourceRelative);
    if (isPageAsset) {
      const metadataPath = absolute.replace(/\.(html|rsc)$/, ".meta");
      try {
        const metadata = JSON.parse(await readFile(metadataPath, "utf8"));
        if (metadata.status >= 300 && metadata.status < 400) {
          // Redirect prerenders need their status and Location header. If their
          // HTML/RSC is uploaded as a static asset, Cloudflare serves it as 200
          // before the Worker can apply the redirect metadata.
          await rm(target, { force: true });
          continue;
        }
      } catch {
        // A regular page may not have a metadata file; copy it normally.
      }
    }
    await mkdir(dirname(target), { recursive: true });
    // Both build directories live on the same disk. A hard link avoids storing
    // a second 50+ MB copy of the prerendered catalogue on space-constrained
    // machines while presenting a normal file to Wrangler.
    await rm(target, { force: true });
    await link(absolute, target);
    copied.push(target);
  }
}

await walk(source);
console.log(`Copied ${copied.length} prerendered HTML/RSC assets for static-first delivery.`);
