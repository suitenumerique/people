import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Teams Panel', () => {
  test('checks all the elements are visible', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Groups' })).toBeVisible();

    await expect(page.getByTestId('button-new-team')).toBeVisible();
  });
});
