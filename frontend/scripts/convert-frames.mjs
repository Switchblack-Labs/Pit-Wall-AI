#!/usr/bin/env node
// Convert /vro PNG frames to WebP in-place. Idempotent + parallel.
// Usage:  node scripts/convert-frames.mjs

import { readdir, stat } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join, resolve } from "node:path";
import sharp from "sharp";

const SRC = resolve("public/vro");
const QUALITY = 78;          // good quality vs size sweet spot
const CONCURRENCY = 8;
const ALPHA_QUALITY = 90;    // keep alpha clean (we use transparency)

async function main() {
  const all = await readdir(SRC);
  const pngs = all.filter((f) => f.toLowerCase().endsWith(".png")).sort();
  if (!pngs.length) { console.log("No PNGs found in", SRC); return; }
  console.log(`Found ${pngs.length} PNGs. Converting to WebP @${QUALITY}…`);

  let done = 0, skipped = 0, totalIn = 0, totalOut = 0, t0 = Date.now();

  const queue = pngs.slice();
  const workers = Array.from({ length: CONCURRENCY }, () =>
    (async function loop() {
      while (queue.length) {
        const name = queue.shift();
        if (!name) return;
        const inPath = join(SRC, name);
        const outName = name.replace(/\.png$/i, ".webp");
        const outPath = join(SRC, outName);

        if (existsSync(outPath)) {
          // Only skip if WebP is newer than PNG
          const [ps, ws] = await Promise.all([stat(inPath), stat(outPath)]);
          if (ws.mtimeMs >= ps.mtimeMs) {
            skipped++;
            totalIn += ps.size; totalOut += ws.size;
            continue;
          }
        }

        const ps = await stat(inPath);
        await sharp(inPath)
          .webp({ quality: QUALITY, alphaQuality: ALPHA_QUALITY, effort: 4 })
          .toFile(outPath);
        const ws = await stat(outPath);

        done++;
        totalIn += ps.size; totalOut += ws.size;
        if (done % 20 === 0) {
          const pct = (((done + skipped) / pngs.length) * 100).toFixed(1);
          console.log(`  ${done + skipped}/${pngs.length} (${pct}%) · saved ${(1 - totalOut/totalIn).toLocaleString(undefined, {style:"percent"})}`);
        }
      }
    })()
  );
  await Promise.all(workers);

  const dt = (Date.now() - t0) / 1000;
  console.log(`\nDone in ${dt.toFixed(1)}s.`);
  console.log(`  converted: ${done}  · skipped: ${skipped}`);
  console.log(`  size in:   ${(totalIn / 1e6).toFixed(1)} MB`);
  console.log(`  size out:  ${(totalOut / 1e6).toFixed(1)} MB`);
  console.log(`  savings:   ${(1 - totalOut/totalIn).toLocaleString(undefined, {style:"percent"})}`);
}

main().catch((e) => { console.error(e); process.exit(1); });
