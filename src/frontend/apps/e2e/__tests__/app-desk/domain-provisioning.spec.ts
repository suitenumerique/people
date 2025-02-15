import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName, 'marie');
});

test.describe('When a commune, domain is created on first login via ProConnect', () => {
  test('it checks the domain has been created and is operational', async ({
    page,
  }) => {
    const header = page.locator('header').first();
    await expect(header.getByAltText('Marianne Logo')).toBeVisible();

    await page
      .locator('menu')
      .first()
      .getByLabel(`Mail Domains button`)
      .click();
    await expect(page).toHaveURL(/mail-domains\//);
    await expect(
      page.getByLabel('Mail domains panel', { exact: true }),
    ).toBeVisible();
    await expect(page.getByText('merlaut.collectivite.fr')).toHaveCount(1);
    await expect(page.getByText('No domains exist.')).toHaveCount(0);
  });
});
