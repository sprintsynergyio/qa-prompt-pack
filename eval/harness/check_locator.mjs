// Usage: node check_locator.mjs '<expr>'  -> JSON {count, correct, error}
import { chromium } from '@playwright/test';
const expr = process.argv[2].trim();
const SAFE = /^page(\.(getByRole|getByTestId|getByPlaceholder|getByLabel|getByText|locator|filter|first|last|nth)\((?:[^;`$\\]|\\.)*?\))+$/;
const out = { expr };
const b = await chromium.launch(); const page = await b.newPage();
try {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  for (const t of ['buy milk', 'walk dog']) { await page.getByPlaceholder('What needs to be done?').fill(t); await page.keyboard.press('Enter'); }
  let loc;
  if (expr.startsWith('page.')) { if (!SAFE.test(expr)) throw new Error('unsafe/unsupported expression'); loc = new Function('page', `return ${expr};`)(page); }
  else loc = page.locator(expr);
  out.count = await loc.count();
  out.correct = out.count === 1 && await loc.evaluate(el => el === document.querySelectorAll('[data-testid=todo-item]')[0].querySelector('input.toggle'));
} catch (e) { out.error = String(e.message).slice(0, 200); out.correct = false; }
console.log(JSON.stringify(out)); await b.close();
