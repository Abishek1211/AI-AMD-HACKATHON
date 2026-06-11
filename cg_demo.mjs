import { chromium } from 'playwright';
import { writeFileSync } from 'fs';

const CHANGE = "Upgrade payment-service from v4.0 to v4.2";
const SCREENSHOT_DIR = "C:\\Users\\Abi\\AppData\\Local\\Temp";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
await page.setViewportSize({ width: 1400, height: 900 });

// ── Screen 1: Change Submission ──────────────────────────────
await page.goto('http://localhost:5173');
await page.waitForLoadState('networkidle');
await page.screenshot({ path: `${SCREENSHOT_DIR}\\cg_1_submit.png` });
console.log('Screenshot 1: Submit page');

// Type the change request
await page.fill('textarea', CHANGE);
await page.screenshot({ path: `${SCREENSHOT_DIR}\\cg_2_typed.png` });
console.log('Screenshot 2: Typed request');

// Click Analyze — this calls Ollama (may take 30-90s)
console.log('Calling Ollama via API...');
await Promise.all([
  page.waitForURL('**/dependencies', { timeout: 120_000 }),
  page.click('button:has-text("Analyze Change")')
]);
console.log('Analysis complete, navigated to dependencies');

// ── Screen 2: Dependency Graph ───────────────────────────────
await page.waitForLoadState('networkidle');
await page.screenshot({ path: `${SCREENSHOT_DIR}\\cg_3_deps.png` });
console.log('Screenshot 3: Dependency graph');

// ── Screen 3: Risk Analysis ───────────────────────────────────
await page.click('text=Risk Analysis');
await page.waitForLoadState('networkidle');
await page.screenshot({ path: `${SCREENSHOT_DIR}\\cg_4_risk.png` });
console.log('Screenshot 4: Risk analysis');

// ── Screen 4: Recommendation ──────────────────────────────────
await page.click('text=Recommendation');
await page.waitForLoadState('networkidle');
await page.screenshot({ path: `${SCREENSHOT_DIR}\\cg_5_rec.png` });
console.log('Screenshot 5: Recommendation');

await browser.close();
console.log('Done.');
