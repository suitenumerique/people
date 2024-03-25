import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Header', () => {
  test('checks all the elements are visible', async ({ page }) => {
    const header = page.locator('header').first();

    await expect(header.getByAltText('Marianne Logo')).toBeVisible();

    await expect(
      header.getByAltText('Freedom Equality Fraternity Logo'),
    ).toBeVisible();

    await expect(header.getByAltText('Equipes Logo')).toBeVisible();
    await expect(header.locator('h2').getByText('Equipes')).toHaveCSS(
      'color',
      'rgb(0, 0, 145)',
    );
    await expect(header.locator('h2').getByText('Equipes')).toHaveCSS(
      'font-family',
      /Marianne/i,
    );

    await expect(
      header.getByText('Les applications de La Suite numérique'),
    ).toBeVisible();

    await expect(header.getByAltText('Language Icon')).toBeVisible();
    await expect(header.getByText('My account')).toBeVisible();
  });

  test('checks logout button', async ({ page }) => {
    await page
      .getByRole('button', {
        name: 'My account',
      })
      .click();

    await page
      .getByRole('button', {
        name: 'Logout',
      })
      .click();

    // FIXME - assert the session has been killed in Keycloak

    await expect(page.getByRole('button', { name: 'Sign in' })).toBeVisible();
  });
});
