import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Mails', () => {
  test('checks all the elements are visible', async ({ page }) => {
    await page.locator('menu').first().getByLabel(`Mails button`).click();
    await expect(page.getByText('john@doe.com')).toBeVisible();
    await expect(page.getByText('jane@doe.com')).toBeVisible();
  });
});
