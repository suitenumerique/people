import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Menu', () => {
  const menuItems = [
    {
      name: 'Teams',
      isDefault: true,
      expectedUrl: '',
      expectedText: 'Create a new team',
    },
    {
      name: 'Mails',
      isDefault: false,
      expectedUrl: '/mails',
      expectedText: 'Emails',
    },
  ];
  for (const { name, isDefault, expectedUrl, expectedText } of menuItems) {
    test(`checks that ${name} menu item is displaying correctly`, async ({
      page,
    }) => {
      const menu = page.locator('menu').first();

      const buttonMenu = menu.getByLabel(`${name} button`);
      await expect(buttonMenu).toBeVisible();
      await buttonMenu.hover();
      await expect(menu.getByLabel('tooltip')).toHaveText(name);

      // Checks the tooltip is with inactive color
      await expect(menu.getByLabel('tooltip')).toHaveCSS(
        'background-color',
        isDefault ? 'rgb(255, 255, 255)' : 'rgb(22, 22, 22)',
      );

      await buttonMenu.click();

      // Checks the tooltip has active color
      await buttonMenu.hover();
      await expect(menu.getByLabel('tooltip')).toHaveCSS(
        'background-color',
        'rgb(255, 255, 255)',
      );
    });

    test(`checks that ${name} menu item is routing correctly`, async ({
      page,
    }) => {
      const menu = page.locator('menu').first();

      const buttonMenu = menu.getByLabel(`${name} button`);
      await buttonMenu.click();

      await expect(page.getByText(expectedText).first()).toBeVisible();
      await expect(page).toHaveURL(expectedUrl);
    });
  }
});
