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
    const menu = page.locator('menu').first();

    await menu.getByLabel(`Mail Domains button`)
      .click();
    await expect(page).toHaveURL(/mail-domains\//);
    await expect(
      page.getByLabel('Areas of the organization', { exact: true }),
    ).toBeVisible();
    await expect(page.getByText('merlaut.test.collectivite.fr')).toHaveCount(1);
    await expect(page.getByText('No domains exist.')).toHaveCount(0);
  });
});
