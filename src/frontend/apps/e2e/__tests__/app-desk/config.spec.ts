import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.describe('Config', () => {
  test('it checks the config api is called', async ({ page, browserName }) => {
    await page.goto('/');
    await keyCloakSignIn(page, browserName);

    const responsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/config/') && response.status() === 200,
    );

    const response = await responsePromise;
    expect(response.ok()).toBeTruthy();

    expect(await response.json()).toStrictEqual({
      LANGUAGES: [
        ['en-us', 'English'],
        ['fr-fr', 'French'],
      ],
      FEATURES: {
        CONTACTS_CREATE: true,
        CONTACTS_DISPLAY: true,
        MAILBOXES_CREATE: true,
        TEAMS_CREATE: true,
        TEAMS: true,
      },
      RELEASE: 'NA',
    });
  });

  test('it checks that the config can deactivate the feature "teams"', async ({
    page,
    browserName,
  }) => {
    await page.goto('/');
    // Login with a user who has the visibility on the groups
    await keyCloakSignIn(page, browserName, 'team-member');

    await page.route('**/api/v1.0/config/', async (route) => {
      const request = route.request();
      if (request.method().includes('GET')) {
        await route.fulfill({
          json: {
            LANGUAGES: [
              ['en-us', 'English'],
              ['fr-fr', 'French'],
            ],
            FEATURES: { TEAMS: false },
          },
        });
      } else {
        await route.continue();
      }
    });

    await expect(page.locator('menu')).toBeHidden();

    await expect(
      page.getByRole('button', {
        name: 'Create a new team',
      }),
    ).toBeHidden();

    await expect(page.getByText('Mail Domains')).toBeVisible();
  });
});
