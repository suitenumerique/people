import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await keyCloakSignIn(page);
});

test.describe('Language', () => {
  test('checks the language picker', async ({ page }) => {
    await expect(
      page.locator('h1').first().getByText('Hello Desk !'),
    ).toBeVisible();

    const header = page.locator('header').first();
    await header.getByRole('combobox').getByText('EN').click();
    await header.getByRole('option', { name: 'FR' }).click();
    await expect(header.getByRole('combobox').getByText('FR')).toBeVisible();

    await expect(
      page.locator('h1').first().getByText('Bonjour Desk !'),
    ).toBeVisible();
  });
});
