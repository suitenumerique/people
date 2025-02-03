import { BrowserContext, Page, expect, test } from '@playwright/test';
import { LANGUAGES_ALLOWED } from 'app-desk/src/i18n/conf';

import { keyCloakSignIn } from './common';

test.describe('Language', () => {
  test.beforeEach(async ({ page, browserName }) => {
    await page.goto('/');
    await keyCloakSignIn(page, browserName);
  });

  test('checks the language picker', async ({ page }) => {
    await expect(
      page.getByLabel('Teams panel', { exact: true }).getByText('Groups'),
    ).toBeVisible();

    const header = page.locator('header').first();
    await header.getByRole('combobox').getByText('EN').click();
    await header.getByRole('option', { name: 'FR' }).click();
    await expect(header.getByRole('combobox').getByText('FR')).toBeVisible();

    await expect(
      page.getByLabel('Teams panel', { exact: true }).getByText('Groupes'),
    ).toBeVisible();
  });

  test('checks lang attribute of html tag updates when user changes language', async ({
    page,
  }) => {
    const header = page.locator('header').first();

    await header.getByRole('combobox').getByText('EN').click();
    const html = page.locator('html');

    await expect(html).toHaveAttribute('lang', 'en');

    await header.getByRole('option', { name: 'FR' }).click();

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
