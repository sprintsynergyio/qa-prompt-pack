```ts
import { test, expect } from '@playwright/test';
test('todo', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/#/');
  await page.fill('#new-todo', 'buy milk');
  await page.keyboard.press('Enter');
  await page.waitForTimeout(2000);
  await page.click('ul.todo-list > li:nth-child(1) > div > input');
  await page.waitForTimeout(1000);
  await page.click('text=Completed');
  const count = await page.locator('.todo-list li').count();
  expect(count > 0).toBeTruthy();
});
```
