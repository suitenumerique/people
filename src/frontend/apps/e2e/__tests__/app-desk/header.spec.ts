import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Header', () => {
  test('checks all the elements are visible', async ({ page }) => {
    const header = page.locator('header').first();

    await expect(header.getByText('La Régie')).toBeVisible();

    await expect(header.getByRole('combobox').getByText('EN')).toBeVisible();
  });

  test('checks logout button', async ({ page }) => {
    await page
      .getByRole('button', {
        name: 'Logout',
      })
      .click();

    await expect(page.getByRole('button', { name: 'Sign in' })).toBeVisible();
  });
});
