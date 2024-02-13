import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await keyCloakSignIn(page);
});

test.describe('Header', () => {
  test('checks all the elements are visible', async ({ page }) => {
    const header = page.locator('header').first();

    await expect(header.getByAltText('Marianne Logo')).toBeVisible();

    await expect(
      header.getByAltText('Freedom Equality Fraternity Logo'),
    ).toBeVisible();

    await expect(header.getByAltText('Desk Logo')).toBeVisible();
    await expect(header.locator('h2').getByText('Desk')).toHaveCSS(
      'color',
      'rgb(0, 0, 145)',
    );
    await expect(header.locator('h2').getByText('Desk')).toHaveCSS(
      'font-family',
      /Marianne/i,
    );

    await expect(
      header.getByRole('button', { name: 'Access to FAQ' }),
    ).toBeVisible();
    await expect(header.getByAltText('FAQ Icon')).toBeVisible();
    await expect(header.getByText('FAQ')).toBeVisible();

    await expect(header.getByAltText('Cells icon')).toBeVisible();

    await expect(header.getByAltText('Language Icon')).toBeVisible();

    await expect(header.getByText('John Doe')).toBeVisible();
    await expect(
      header.getByRole('img', {
        name: 'profile picture',
      }),
    ).toBeVisible();
  });
});
