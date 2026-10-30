// Usage: node render.mjs <out_dir> <scene1.json> [scene2.json ...]
// Serves this folder over HTTP, opens viewer.html in headless Chromium for each scene and saves a PNG.
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { basename, extname, join, resolve } from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const here = resolve(new URL(".", import.meta.url).pathname);
const [outDir, ...scenes] = process.argv.slice(2);
const files = new Map(scenes.map((p) => ["/scenes/" + basename(p), resolve(p)]));
const types = { ".html": "text/html", ".js": "text/javascript", ".json": "application/json" };

const server = createServer(async (req, res) => {
  const url = decodeURIComponent(req.url.split("?")[0]);
  const path = files.get(url) ?? join(here, url);
  if (!path.startsWith(here) && !files.has(url)) { res.writeHead(403).end(); return; }
  try {
    const body = await readFile(path);
    res.writeHead(200, { "Content-Type": types[extname(path)] ?? "application/octet-stream" }).end(body);
  } catch { res.writeHead(404).end(); }
});
await new Promise((ok) => server.listen(0, "127.0.0.1", ok));
const port = server.address().port;

const browser = await chromium.launch({ args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
for (const scene of scenes) {
  const spec = JSON.parse(await readFile(scene, "utf8"));
  const page = await browser.newPage({ viewport: { width: spec.width, height: spec.height } });
  page.on("pageerror", (e) => console.error("page error:", e.message));
  await page.goto(`http://127.0.0.1:${port}/viewer.html?scene=/scenes/${basename(scene)}`);
  await page.waitForFunction(() => window.done === true, null, { timeout: 300000 });
  const out = join(outDir, basename(scene, ".json") + ".png");
  await page.screenshot({ path: out });
  console.log("wrote", out);
  await page.close();
}
await browser.close();
server.close();
