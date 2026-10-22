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
      COMMIT: 'NA',
      FEATURES: {
        CONTACTS_CREATE: true,
        CONTACTS_DISPLAY: true,
        MAILBOXES_CREATE: true,
        TEAMS_CREATE: true,
        TEAMS_DISPLAY: true,
      },
      RELEASE: 'NA',
    });
  });

  test('it checks that the user abilities display mail domains', async ({
    page,
    browserName,
  }) => {
    await page.goto('/');
    await keyCloakSignIn(page, browserName, 'mail-member');

    await expect(page.locator('menu')).toBeVisible();

    const menu = page.locator('menu').first();

    await menu.getByLabel('Mail Domains button').click();

    await expect(page).toHaveURL(/mail-domains\//);

    await expect(page.getByText('Domains of the organization')).toBeVisible();
  });

  // test('it checks that the user abilities display teams', async ({
  //   page,
  //   browserName,
  // }) => {
  //   await page.goto('/');
  //   await keyCloakSignIn(page, browserName, 'team-member');

  //   await expect(page.locator('menu')).toBeHidden();

  //   await expect(page.getByText('Groups')).toBeVisible();
  // });

  test('it checks that the config does not deactivate the feature "teams"', async ({
    page,
    browserName,
  }) => {
    await page.route('**/api/v1.0/config/', async (route) => {
      const request = route.request();
      if (request.method().includes('GET')) {
        await route.fulfill({
          json: {
            LANGUAGES: [
              ['en-us', 'English'],
              ['fr-fr', 'French'],
            ],
            FEATURES: { TEAMS_DISPLAY: false },
          },
        });
      } else {
        await route.continue();
      }
    });

    await page.goto('/');
    // Login with a user who has the visibility on the groups should see groups
    // It's now the backend that decides if the user can see the group menu and they
    // should be redirected to the groups page in such case
    await keyCloakSignIn(page, browserName, 'team-administrator');

    await expect(page.locator('menu')).toBeHidden();
  });
});
