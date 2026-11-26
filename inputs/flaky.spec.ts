import { test, expect } from '@playwright/test';
let created = false;
test('adds a todo', async ({ page }) => {
  await page.goto('/todomvc/#/');
  await page.getByPlaceholder('What needs to be done?').fill('buy milk');
  await page.getByPlaceholder('What needs to be done?').press('Enter');
  created = true;
  await page.waitForTimeout(500);
});
test('completes the todo', async ({ page }) => {
  await page.goto('/todomvc/#/');
  await page.waitForTimeout(1000);
  await page.locator('.toggle').first().check();
  expect(await page.locator('.todo-count').textContent()).toBe('0 items left');
});
