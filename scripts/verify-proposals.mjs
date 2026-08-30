import { createServer } from "node:http";
import { mkdir, readFile, readdir, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const playwrightEntry = process.env.CODEX_PLAYWRIGHT_PATH
  ? pathToFileURL(path.join(process.env.CODEX_PLAYWRIGHT_PATH, "index.mjs"))
      .href
  : "@playwright/test";
const { chromium } = await import(playwrightEntry);

const root = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
  "proposal doc",
);
const expected = [
  "00_提案書一覧.html",
  "01_ゼネコン向け提案書.html",
  "02_サブコン向け提案書.html",
  "03_専門工事会社向け提案書.html",
  "04_現場作業員向け提案書.html",
  "05_現場監督向け提案書.html",
  "06_協力会社向け提案書.html",
  "07_経営層向け提案書.html",
  "08_管理部門向け提案書.html",
  "09_発注者・監理者向け提案書.html",
];

const actual = (await readdir(root))
  .filter((name) => name.endsWith(".html"))
  .sort();
if (JSON.stringify(actual) !== JSON.stringify(expected)) {
  throw new Error(
    `HTML file set mismatch\nexpected=${expected.join(",")}\nactual=${actual.join(",")}`,
  );
}

for (const name of expected) {
  const html = await readFile(path.join(root, name), "utf8");
  if (!html.startsWith("<!doctype html>"))
    throw new Error(`${name}: missing doctype`);
  if (!html.includes('<html lang="ja">'))
    throw new Error(`${name}: missing Japanese lang`);
  if ((html.match(/<h1[ >]/g) ?? []).length !== 1)
    throw new Error(`${name}: h1 must be unique`);
  for (const href of html.matchAll(/href="([^"]+\.html)"/g)) {
    const target = decodeURI(href[1]);
    await stat(path.join(root, target));
  }
}

const server = createServer(async (req, res) => {
  try {
    const requested = decodeURIComponent((req.url ?? "/").split("?")[0]);
    const file = requested === "/" ? expected[0] : requested.replace(/^\//, "");
    if (!expected.includes(file)) {
      res.writeHead(404).end("Not found");
      return;
    }
    const body = await readFile(path.join(root, file));
    res
      .writeHead(200, { "content-type": "text/html; charset=utf-8" })
      .end(body);
  } catch (error) {
    res.writeHead(500).end(String(error));
  }
});

await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const { port } = server.address();
const browser = await chromium.launch({ headless: true });
const failures = [];

try {
  for (const viewport of [
    { name: "desktop", width: 1440, height: 900 },
    { name: "mobile", width: 390, height: 844 },
  ]) {
    const context = await browser.newContext({ viewport });
    const page = await context.newPage();
    page.on("pageerror", (error) =>
      failures.push(`${viewport.name}: pageerror: ${error.message}`),
    );
    page.on("console", (message) => {
      if (message.type() === "error")
        failures.push(`${viewport.name}: console: ${message.text()}`);
    });

    for (const name of expected) {
      const response = await page.goto(
        `http://127.0.0.1:${port}/${encodeURIComponent(name)}`,
      );
      if (!response?.ok())
        failures.push(`${viewport.name}/${name}: HTTP ${response?.status()}`);
      if ((await page.locator("h1").count()) !== 1)
        failures.push(`${viewport.name}/${name}: visible h1 count mismatch`);
      if (!(await page.locator("h1").isVisible()))
        failures.push(`${viewport.name}/${name}: h1 not visible`);
      const overflow = await page.evaluate(
        () =>
          document.documentElement.scrollWidth -
          document.documentElement.clientWidth,
      );
      if (overflow > 1)
        failures.push(
          `${viewport.name}/${name}: horizontal overflow ${overflow}px`,
        );
      if (
        name !== expected[0] &&
        (await page.locator("footer .role-links a").count()) !== 9
      ) {
        failures.push(
          `${viewport.name}/${name}: role navigation must contain 9 links`,
        );
      }
    }
    if (process.env.PROPOSAL_SCREENSHOT_DIR) {
      await mkdir(process.env.PROPOSAL_SCREENSHOT_DIR, { recursive: true });
      const previewName =
        viewport.name === "desktop" ? expected[0] : expected[4];
      await page.goto(
        `http://127.0.0.1:${port}/${encodeURIComponent(previewName)}`,
      );
      await page.screenshot({
        path: path.join(
          process.env.PROPOSAL_SCREENSHOT_DIR,
          `${viewport.name}.png`,
        ),
        fullPage: true,
      });
    }
    await context.close();
  }
} finally {
  await browser.close();
  server.close();
}

if (failures.length) throw new Error(failures.join("\n"));
console.log(
  `PASS: ${expected.length} HTML files × desktop/mobile; structure, links, rendering, overflow, and console checks`,
);
