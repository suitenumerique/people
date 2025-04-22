import { expect, test } from '@playwright/test';

import { createTeam, keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName, 'team-owner-mail-member');
});

test.describe('Menu', () => {
  const menuItems = [
    {
      name: 'Teams',
      isDefault: true,
      expectedUrl: '/teams/',
      expectedText: 'Teams',
    },
    {
      name: 'Mail Domains',
      isDefault: false,
      expectedUrl: '/mail-domains/',
      expectedText: 'Mail Domains',
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

  test(`it checks that the menu is not displaying when no abilities`, async ({
    page,
  }) => {
    await page.route('**/api/v1.0/users/me/', async (route) => {
      await route.fulfill({
        json: {
          id: '52de4dcf-5ca0-4b7f-9841-3a18e8cb6a95',
          email: 'user-e2e-chromium@example.com',
          language: 'en-us',
          name: 'E2E Chromium',
          timezone: 'UTC',
          is_device: false,
          is_staff: false,
          abilities: {
            contacts: {
              can_view: true,
              can_create: true,
            },
            teams: {
              can_view: true,
              can_create: false,
            },
            mailboxes: {
              can_view: true,
              can_create: false,
            },
          },
        },
      });
    });

    const menu = page.locator('menu').first();

    let buttonMenu = menu.getByLabel(`Teams button`);
    await buttonMenu.click();
    await expect(
      page.getByText('Click on team to view details').first(),
    ).toBeVisible();

    buttonMenu = menu.getByLabel(`Mail Domains`);
    await buttonMenu.click();
    await expect(
      page.getByText('Click on mailbox to view details').first(),
    ).toBeVisible();
  });

  test(`it checks that the menu is not displaying when all abilities`, async ({
    page,
  }) => {
    await page.route('**/api/v1.0/users/me/', async (route) => {
      await route.fulfill({
        json: {
          id: '52de4dcf-5ca0-4b7f-9841-3a18e8cb6a95',
          email: 'user-e2e-chromium@example.com',
          language: 'en-us',
          name: 'E2E ChromiumMM',
          timezone: 'UTC',
          is_device: false,
          is_staff: false,
          abilities: {
            contacts: {
              can_view: true,
              can_create: true,
            },
            teams: {
              can_view: true,
              can_create: true,
            },
            mailboxes: {
              can_view: true,
              can_create: true,
            },
          },
        },
      });
    });

    const menu = page.locator('menu').first();

    let buttonMenu = menu.getByLabel(`Teams button`);
    await buttonMenu.click();
    await expect(page.getByText('Create a new team').first()).toBeVisible();

    buttonMenu = menu.getByLabel(`Mail Domains`);
    await buttonMenu.click();
    await expect(page.getByText('Add a mail domain').first()).toBeVisible();
  });

  test(`it checks that the sub menu is still highlighted`, async ({
    page,
    browserName,
  }) => {
    await createTeam(page, 'team-sub-menu', browserName, 1);

    const menu = page.locator('menu').first();
    const buttonMenu = menu.locator('li').first();
    await expect(buttonMenu).toHaveCSS(
      'background-color',
      'rgb(227, 227, 253)',
    );
  });
});
