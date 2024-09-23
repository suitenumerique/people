import { expect, test } from '@playwright/test';
import { MailDomain } from 'app-desk/src/features/mail-domains/domains';

import { keyCloakSignIn } from './common';

const currentDateIso = new Date().toISOString();
const mailDomainsFixtures: MailDomain[] = [
  {
    name: 'domain.fr',
    id: '456ac6ca-0402-4615-8005-69bc1efde43f',
    created_at: currentDateIso,
    updated_at: currentDateIso,
    slug: 'domainfr',
    status: 'pending',
    abilities: {
      get: true,
      patch: true,
      put: true,
      post: true,
      delete: true,
      manage_accesses: true,
    },
  },
  {
    name: 'mails.fr',
    id: '456ac6ca-0402-4615-8005-69bc1efde43e',
    created_at: currentDateIso,
    updated_at: currentDateIso,
    slug: 'mailsfr',
    status: 'enabled',
    abilities: {
      get: true,
      patch: true,
      put: true,
      post: true,
      delete: true,
      manage_accesses: true,
    },
  },
  {
    name: 'versailles.net',
    id: '456ac6ca-0402-4615-8005-69bc1efde43g',
    created_at: currentDateIso,
    updated_at: currentDateIso,
    slug: 'versaillesnet',
    status: 'disabled',
    abilities: {
      get: true,
      patch: true,
      put: true,
      post: true,
      delete: true,
      manage_accesses: true,
    },
  },
  {
    name: 'paris.fr',
    id: '456ac6ca-0402-4615-8005-69bc1efde43h',
    created_at: currentDateIso,
    updated_at: currentDateIso,
    slug: 'parisfr',
    status: 'failed',
    abilities: {
      get: true,
      patch: true,
      put: true,
      post: true,
      delete: true,
      manage_accesses: true,
    },
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

      await expect(page).toHaveURL(/mail-domains\//);

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

      const panel = page.getByLabel('Mail domains panel').first();

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
      await expect(page).toHaveURL(/mail-domains\//);
      await expect(
        page.getByLabel('Mail domains panel', { exact: true }),
      ).toBeVisible();
      await expect(page.getByText('No domains exist.')).toBeVisible();
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
      await expect(page).toHaveURL(/mail-domains\//);
      await expect(
        page.getByLabel('Mail domains panel', { exact: true }),
      ).toBeVisible();
      await expect(page.getByText('No domains exist.')).toHaveCount(0);

      await Promise.all(
        mailDomainsFixtures.map(async ({ name, status }) => {
          const linkName = page.getByRole('link', { name });
          await expect(linkName).toBeVisible();
          await expect(linkName.getByText(`[${status}]`)).toBeVisible();
        }),
      );
    });
  });
});
