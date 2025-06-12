import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName, 'team-owner-mail-member');
});

test.describe('Menu', () => {
  const menuItems = [
    {
      name: 'Teams',
      expectedUrl: '/teams/',
      expectedText: 'Teams',
    },
    {
      name: 'Mail Domains',
      expectedUrl: '/mail-domains/',
      expectedText: 'Mail Domains',
    },
  ];
  for (const { name, expectedUrl, expectedText } of menuItems) {
    test(`checks that ${name} menu item is displaying correctly`, async ({
      page,
    }) => {
      const menu = page.locator('menu').first();

      const buttonMenu = menu.getByLabel(`${name} button`);
      await expect(buttonMenu).toBeVisible();
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
});
