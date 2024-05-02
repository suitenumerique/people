import { expect, test } from '@playwright/test';
import { MailDomain } from 'app-desk/src/features/mail-domains';

import { keyCloakSignIn } from './common';

const currentDateIso = new Date().toISOString();
const mailDomainsFixtures: MailDomain[] = [
  {
    name: 'domain.fr',
    id: '456ac6ca-0402-4615-8005-69bc1efde43f',
    created_at: currentDateIso,
    updated_at: currentDateIso,
  },
  {
    name: 'mails.fr',
    id: '456ac6ca-0402-4615-8005-69bc1efde43e',
    created_at: currentDateIso,
    updated_at: currentDateIso,
  },
  {
    name: 'versailles.net',
    id: '456ac6ca-0402-4615-8005-69bc1efde43g',
    created_at: currentDateIso,
    updated_at: currentDateIso,
  },
  {
    name: 'paris.fr',
    id: '456ac6ca-0402-4615-8005-69bc1efde43h',
    created_at: currentDateIso,
    updated_at: currentDateIso,
  },
];

test.describe('Mail domain', () => {
  test.describe('checks all the elements are visible', () => {
    test.beforeEach(async ({ page, browserName }) => {
      await page.goto('/');
      await keyCloakSignIn(page, browserName);
    });

    test('when no mail domain exists', async ({ page }) => {
      await page.route('**/api/v1.0/mail-domains/?page=*', async (route) => {
        await route.fulfill({
          json: {
            count: 0,
            next: null,
            previous: null,
            results: [],
          },
        });
      });

      await page
        .locator('menu')
        .first()
        .getByLabel(`Mail Domains button`)
        .click();
      await expect(page).toHaveURL(/mail-domains/);
      await expect(
        page.getByLabel('mail domains panel', { exact: true }),
      ).toBeVisible();
      await expect(page.getByText('0 mail domain to display.')).toBeVisible();
    });

    test('when 4 mail domains exist', async ({ page }) => {
      await page.route('**/api/v1.0/mail-domains/?page=*', async (route) => {
        await route.fulfill({
          json: {
            count: mailDomainsFixtures.length,
            next: null,
            previous: null,
            results: mailDomainsFixtures,
          },
        });
      });

      await page
        .locator('menu')
        .first()
        .getByLabel(`Mail Domains button`)
        .click();
      await expect(page).toHaveURL(/mail-domains/);
      await expect(
        page.getByLabel('mail domains panel', { exact: true }),
      ).toBeVisible();
      await expect(page.getByText('0 mail domain to display.')).toHaveCount(0);
      await expect(page.getByText('domain.fr')).toBeVisible();
      await expect(page.getByText('mails.fr')).toBeVisible();
      await expect(page.getByText('versailles.net')).toBeVisible();
      await expect(page.getByText('paris.fr')).toBeVisible();
    });
  });
});
