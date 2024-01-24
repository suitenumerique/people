import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await keyCloakSignIn(page);
});

test.describe('App', () => {
  test('should display the main elements', async ({ page }) => {
    await expect(page.locator('header').first()).toContainText('Desk');
    await expect(page.getByLabel('Team name')).toBeVisible();
  });

  test('creates 2 teams and displayed them', async ({ page }) => {
    await page.getByLabel('Team name').fill('My new team');
    await page.click('button:has-text("Create Team")');
    await page.getByLabel('Team name').fill('My second new team');
    await page.click('button:has-text("Create Team")');

    await expect(
      page.locator('li').getByText('My new team').first(),
    ).toBeVisible();
    await expect(
      page.locator('li').getByText('My second new team').first(),
    ).toBeVisible();
  });
});
