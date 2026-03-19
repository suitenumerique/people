import { BrowserContext, Page, expect, test } from '@playwright/test';
import { LANGUAGES_ALLOWED } from 'app-desk/src/i18n/conf';

import { keyCloakSignIn } from './common';

test.describe('Language', () => {
  test.beforeEach(async ({ page, browserName }) => {
    await page.goto('/');
    await keyCloakSignIn(page, browserName);
    await page.goto('/teams');
  });

  test('checks the language picker', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Groups' })).toBeVisible();

    await page.getByRole('button', { name: 'Open user menu' }).click();
    await page.getByRole('button', { name: /EN/ }).click();
    await page.getByRole('menuitem', { name: 'FR' }).click();
    await expect(page.getByRole('button', { name: /FR/ })).toBeVisible();

    await expect(page.getByRole('heading', { name: 'Groupes' })).toBeVisible();
  });

  test('checks lang attribute of html tag updates when user changes language', async ({
    page,
  }) => {
    await page.getByRole('button', { name: 'Open user menu' }).click();
    await page.getByRole('button', { name: /EN/ }).click();
    const html = page.locator('html');

    await expect(html).toHaveAttribute('lang', 'en');

    await page.getByRole('menuitem', { name: 'FR' }).click();

    await expect(html).toHaveAttribute('lang', 'fr');
  });
});

test.describe('Default language', () => {
  Object.keys(LANGUAGES_ALLOWED).forEach((language) => {
    test(`checks lang attribute of html tag has right value by default for ${language} language`, async ({
      browser,
      browserName,
    }) => {
      const context: BrowserContext = await browser.newContext({
        locale: language,
      });

      const page: Page = await context.newPage();

      await page.goto('/');
      await keyCloakSignIn(page, browserName);

      await expect(page.locator('html')).toHaveAttribute('lang', language);
    });
  });
});
