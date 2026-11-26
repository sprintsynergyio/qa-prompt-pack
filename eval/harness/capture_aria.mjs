import { chromium } from '@playwright/test';
const b = await chromium.launch(); const p = await b.newPage();
await p.goto('https://demo.playwright.dev/todomvc/#/');
for (const t of ['buy milk','walk dog']) { await p.getByPlaceholder('What needs to be done?').fill(t); await p.keyboard.press('Enter'); }
await p.getByTestId('todo-item').nth(1).getByRole('checkbox').check();
console.log(await p.locator('section.todoapp').ariaSnapshot());
const ids = await p.$$eval('[data-testid]', els => [...new Set(els.map(e => e.getAttribute('data-testid')))]);
console.log('# data-testid values: ' + ids.join(', '));
await b.close();
