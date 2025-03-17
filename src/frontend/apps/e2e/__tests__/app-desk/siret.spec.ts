import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName, 'marie');
});

test.describe('OIDC interop with SIRET', () => {
  test('it checks the SIRET is displayed in /me endpoint', async ({ page }) => {
    const response = await page.request.get(
      'http://localhost:8071/api/v1.0/users/me/',
    );
    expect(response.ok()).toBeTruthy();
    expect(await response.json()).toMatchObject({
      organization: { registration_id_list: ['21510339100011'] },
    });
  });
});

test.describe('When a commune, display commune name below user name', () => {
  test('it checks the name is added below the user name', async ({ page }) => {
    const logout = page.getByRole('button', {
      name: 'Marie Delamairie',
    });

    await expect(logout.getByText('Merlaut')).toBeVisible();
  });
});
