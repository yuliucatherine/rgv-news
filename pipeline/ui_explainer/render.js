// Steps an HTML animation (window.render(t)) frame by frame in headless Chromium and writes PNG frames.
// Usage: node pipeline/ui_explainer/render.js <page.html> <frames_dir> <seconds> [fps=60] [only_times_csv]
// Then: ffmpeg -framerate 60 -i <frames_dir>/%05d.png -i voice.wav ... (see make_sh4_test.sh)
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const [page_html, out, secs, fpsArg, only] = process.argv.slice(2);
  const fps = Number(fpsArg || 60); fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(page_html));
  await page.evaluate(() => document.fonts.ready);
  const times = only ? only.split(',').map(Number) : [...Array(Math.round(Number(secs) * fps)).keys()].map(i => i / fps);
  for (let i = 0; i < times.length; i++) {
    await page.evaluate(t => window.render(t), times[i]);
    await page.screenshot({ path: path.join(out, `${String(i).padStart(5, '0')}.png`) });
    if (i % 120 === 0) console.log('frame', i, '/', times.length);
  }
  await browser.close();
})();
