import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Footer', () => {
  test('checks all the elements are visible', async ({ page }) => {
    const footer = page.locator('footer').first();

    await expect(footer.getByAltText('Marianne Logo')).toBeVisible();

    await expect(footer.getByText(/République Française/i)).toBeVisible();

    await expect(
      footer.getByAltText('Freedom Equality Fraternity Logo'),
    ).toBeVisible();

    await expect(
      footer.getByRole('link', { name: 'legifrance.gouv.fr' }),
    ).toBeVisible();

    await expect(
      footer.getByRole('link', { name: 'info.gouv.fr' }),
    ).toBeVisible();

    await expect(
      footer.getByRole('link', { name: 'service-public.fr' }),
    ).toBeVisible();

    await expect(
      footer.getByRole('link', { name: 'data.gouv.fr' }),
    ).toBeVisible();

    await expect(
      footer.getByRole('link', { name: 'Legal Notice' }),
    ).toBeVisible();

    await expect(
      footer.getByRole('link', { name: 'Personal data and cookies' }),
    ).toBeVisible();

    await expect(
      footer.getByRole('link', { name: 'Accessibility' }),
    ).toBeVisible();

    await expect(
      footer.getByText(
        'Unless otherwise stated, all content on this site is under',
      ),
    ).toBeVisible();
  });

  const legalPages = [
    {
      linkName: 'Legal Notice',
      pageName: 'Legal Notice',
      url: '/legal-notice/',
    },
    {
      linkName: 'Personal data and cookies',
      pageName: 'Personal data and cookies',
      url: '/personal-data-cookies/',
    },
    {
      linkName: 'Accessibility: non-compliant',
      pageName: 'Accessibility statement',
      url: '/accessibility/',
    },
  ];
  for (const { linkName, url, pageName } of legalPages) {
    test(`checks ${linkName} page`, async ({ page }) => {
      const footer = page.locator('footer').first();
      await footer.getByRole('link', { name: linkName }).click();

      await expect(
        page
          .getByRole('heading', {
            name: pageName,
          })
          .first(),
      ).toBeVisible();

      await expect(page).toHaveURL(url);
    });
  }

  test('check if the app version is visible', async ({ page }) => {
    const footer = page.locator('footer').first();
    await expect(
      footer.getByText(
        'Version: NA • Unless otherwise stated, all content on this site is under',
      ),
    ).toBeVisible();
  });
});
