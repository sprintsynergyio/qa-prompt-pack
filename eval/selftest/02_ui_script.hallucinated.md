```ts
import { test, expect } from '@playwright/test';
test('hallucinated API', async ({ page }) => {
  await page.goto('/todomvc/#/');
  await page.getByDataTestId('new-todo').typeText('buy milk');
  await expect(page.getByTestId('todo-title')).toHaveText('buy milk');
});
```
