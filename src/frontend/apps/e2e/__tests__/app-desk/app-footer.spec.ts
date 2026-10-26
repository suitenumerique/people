import { expect, test } from '@playwright/test';
import { LASUITE_SUPPORT_SCRIPT_URL } from 'app-desk/src/core/lasuite';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('App footer', () => {
  test('checks all the elements are visible', async ({ page }) => {
    await expect(
      page.getByRole('button', { name: 'Open user menu' }),
    ).toBeVisible();
    await expect(
      page.getByRole('button', { name: 'Digital LaSuite services' }),
    ).toBeVisible();
    await expect(
      page.getByRole('button', { name: 'Contact us' }),
    ).toBeVisible();
  });

  test('opens the support form on the accounts channel', async ({ page }) => {
    await page.route(LASUITE_SUPPORT_SCRIPT_URL, (route) =>
      route.fulfill({ contentType: 'text/javascript', body: '' }),
    );

    await page.getByRole('button', { name: 'Contact us' }).click();

    const supportCommand = await page.evaluate(() =>
      (
        window as unknown as { _lasuite_widget: unknown[][] }
      )._lasuite_widget.find(([widgetName]) => widgetName === 'support'),
    );
    expect(supportCommand).toEqual([
      'support',
      'init',
      expect.objectContaining({ channel: 'accounts' }),
    ]);
  });
});
