import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Header', () => {
  test('checks all the elements are visible', async ({ page }) => {
    const header = page.locator('header').first();

    await expect(
      header.getByRole('button', {
        name: /open the menu|close the menu|ouvrir le menu|fermer le menu/i,
      }),
    ).toBeVisible();
    await expect(
      header.getByRole('button', { name: 'Les services de LaSuite' }),
    ).toBeVisible();
  });
});
