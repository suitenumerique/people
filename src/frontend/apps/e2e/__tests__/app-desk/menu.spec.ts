import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName, 'team-owner-mail-member');
});

test.describe('Menu', () => {
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

    await expect(page.getByText('Add a mail domain').first()).toBeVisible();
  });
});