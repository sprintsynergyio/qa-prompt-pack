```ts
import { test, expect } from '@playwright/test';
test('complete, filter and clear todos', async ({ page }) => {
  await page.goto('/todomvc/#/');
  const input = page.getByPlaceholder('What needs to be done?');
  for (const t of ['buy milk', 'walk dog', 'pay rent']) await input.fill(t), await input.press('Enter');
  await expect(page.getByTestId('todo-title')).toHaveText(['buy milk', 'walk dog', 'pay rent']);
  await page.getByTestId('todo-item').filter({ hasText: 'walk dog' }).getByRole('checkbox', { name: 'Toggle Todo' }).check();
  await expect(page.getByTestId('todo-count')).toHaveText('2 items left');
  await page.getByRole('link', { name: 'Active' }).click();
  await expect(page).toHaveURL(/#\/active$/);
  await expect(page.getByTestId('todo-title')).toHaveText(['buy milk', 'pay rent']);
  await page.getByRole('link', { name: 'All' }).click();
  await page.getByRole('button', { name: 'Clear completed' }).click();
  await expect(page.getByTestId('todo-title')).toHaveText(['buy milk', 'pay rent']);
  await expect(page.getByTestId('todo-count')).toHaveText('2 items left');
});
```
