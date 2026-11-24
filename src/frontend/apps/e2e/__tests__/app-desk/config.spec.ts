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
        MAILBOXES_CREATE: true,
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

    await expect(page).toHaveURL(/mail-domains\//);

    await expect(page.getByText('Domains of the organization')).toBeVisible();
  });
});
