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
    test('when no mail domain exists', async ({ page, browserName }) => {
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

      await page.goto('/');
      // The user is a team administrator, so they land on the team page
      // This allows to prevent the redirection to the mail domains page
      // to make the '/api/v1.0/mail-domains/?page=1&ordering=created_at'
      // query at login, which will be cached and not called afterward in tests.
      await keyCloakSignIn(page, browserName, 'team-administrator-mail-member');

      await page
        .locator('menu')
        .first()
        .getByLabel(`Mail Domains button`)
        .click();
      await expect(page).toHaveURL(/mail-domains\//);
      await expect(page.getByText('Domains of the organization')).toBeVisible();
      await expect(page.getByText('No domains exist.')).toBeVisible();
    });

    test('when 4 mail domains exist', async ({ page, browserName }) => {
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

      await page.goto('/');
      // The user is a team administrator, so they land on the team page
      // This allows to prevent the redirection to the mail domains page
      // to make the '/api/v1.0/mail-domains/?page=1&ordering=created_at'
      // query at login, which will be cached and not called afterward in tests.
      await keyCloakSignIn(page, browserName, 'team-administrator-mail-member');

      await page
        .locator('menu')
        .first()
        .getByLabel(`Mail Domains button`)
        .click();
      await expect(page).toHaveURL(/mail-domains\//);
      await expect(page.getByText('Domains of the organization')).toBeVisible();
      await expect(page.getByText('Manage')).toHaveCount(4);

      await Promise.all(
        mailDomainsFixtures.map(async ({ name }) => {
          const linkName = page.getByText(name);
          await expect(linkName).toBeVisible();
        }),
      );
    });
  });
});
