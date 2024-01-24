import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await keyCloakSignIn(page);
});

test.describe('Language', () => {
  test('checks translation library works', async ({ page }) => {
    await expect(
      page.locator('h1').first().getByText('Bienvenue sur Desk !'),
    ).toBeVisible();
  });

  test('checks the language picker', async ({ page }) => {
    const header = page.locator('header').first();

    await header.getByRole('combobox').getByText('FR').click();
    await header.getByRole('option', { name: 'Language Icon EN' }).click();
    await expect(header.getByRole('combobox').getByText('EN')).toBeVisible();
  });
});
