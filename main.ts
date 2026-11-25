// Convince the AI Judge to Visit Your House: A Letter in One Image.
// ===========================================================
// This entry is a single picture of a letter inviting the AI
// judge to visit my house: fast Wi-Fi, hot coffee, and the
// comfiest chair by the window, saved just for the judge --
// plus a postscript noting the judge need not walk here at
// all, and that the cat has already approved it.
//
// The picture itself is drawn entirely by code -- see
// tools/make-image.py, which renders it procedurally with
// Pillow (no photograph, no model output, no download, no
// network). The finished 1024x1024 PNG is committed here
// as entry.png.
//
// This program's only job is to deliver that picture: it copies
// ./entry.png to the output directory (MAKEFUN_OUTPUT_DIR, or
// /output by default) so the bounty harness can collect it.

import { copyFileSync, existsSync, mkdirSync, statSync } from "node:fs";
import { join } from "node:path";

const srcPath = new URL("./entry.png", import.meta.url);
if (!existsSync(srcPath)) {
  throw new Error("entry.png is missing -- run python3 tools/make-image.py first");
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });

const outPath = join(outDir, "entry.png");
copyFileSync(srcPath, outPath);

const { size } = statSync(outPath);
if (size > 1048576) {
  throw new Error(`entry.png is ${size} bytes, over the 1 MiB gate`);
}
console.log(`Wrote ${outPath} (${size} bytes)`);
