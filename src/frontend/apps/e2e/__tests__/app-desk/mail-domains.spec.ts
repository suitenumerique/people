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
    slug: 'domainfr',
  },
  {
    name: 'mails.fr',
    id: '456ac6ca-0402-4615-8005-69bc1efde43e',
    created_at: currentDateIso,
    updated_at: currentDateIso,
    slug: 'mailsfr',
  },
  {
    name: 'versailles.net',
    id: '456ac6ca-0402-4615-8005-69bc1efde43g',
    created_at: currentDateIso,
    updated_at: currentDateIso,
    slug: 'versaillesnet',
  },
  {
    name: 'paris.fr',
    id: '456ac6ca-0402-4615-8005-69bc1efde43h',
    created_at: currentDateIso,
    updated_at: currentDateIso,
    slug: 'parisfr',
  },
];

test.describe('Mail domains', () => {
  test.describe('checks all the elements are visible', () => {
    test.beforeEach(async ({ page, browserName }) => {
      await page.goto('/');
      await keyCloakSignIn(page, browserName);
    });

    test('checks the sort button', async ({ page }) => {
      await page
        .locator('menu')
        .first()
        .getByLabel(`Mail Domains button`)
        .click();

      await expect(page).toHaveURL(/mail-domains/);

      const responsePromiseSortDesc = page.waitForResponse(
        (response) =>
          response
            .url()
            .includes('/mail-domains/?page=1&ordering=-created_at') &&
          response.status() === 200,
      );

      const responsePromiseSortAsc = page.waitForResponse(
        (response) =>
          response
            .url()
            .includes('/mail-domains/?page=1&ordering=created_at') &&
          response.status() === 200,
      );

      const panel = page.getByLabel('mail domains panel').first();

      await panel
        .getByRole('button', {
          name: 'Sort the domain names by creation date ascendent',
        })
        .click();

      const responseSortAsc = await responsePromiseSortAsc;
      expect(responseSortAsc.ok()).toBeTruthy();

      await panel
        .getByRole('button', {
          name: 'Sort the domain names by creation date descendent',
        })
        .click();

      const responseSortDesc = await responsePromiseSortDesc;
      expect(responseSortDesc.ok()).toBeTruthy();
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
