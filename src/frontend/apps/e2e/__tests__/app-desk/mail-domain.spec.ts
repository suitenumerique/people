import { Page, expect, test } from '@playwright/test';
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

const mailDomainDomainFrFixture = mailDomainsFixtures[0];

const clickOnMailDomainsNavButton = async (page: Page): Promise<void> =>
  await page.locator('menu').first().getByLabel(`Mail Domains button`).click();

test.describe('Mail domain', () => {
  test.beforeEach(async ({ page, browserName }) => {
    await page.goto('/');
    await keyCloakSignIn(page, browserName);
  });

  test('redirects to 404 page when the mail domain requested does not exist', async ({
    page,
  }) => {
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

    await page.goto('/mail-domains/unknown-domain.fr');
    await expect(
      page.getByText(
        'It seems that the page you are looking for does not exist or cannot be displayed correctly.',
      ),
    ).toBeVisible({
      timeout: 15000,
    });
  });

  test('checks all the elements are visible when domain exist but contains no mailboxes', async ({
    page,
  }) => {
    const interceptApiCalls = async () => {
      await page.route(
        '**/api/v1.0/mail-domains/domainfr/mailboxes/?page=1',
        async (route) => {
          await route.fulfill({
            json: {
              count: 0,
              next: null,
              previous: null,
              results: [],
            },
          });
        },
      );

      await page.route('**/api/v1.0/mail-domains/domainfr**', async (route) => {
        await route.fulfill({
          json: mailDomainDomainFrFixture,
        });
      });
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
    };

    await interceptApiCalls();

    await clickOnMailDomainsNavButton(page);

    await expect(page).toHaveURL(/mail-domains\//);

    await page.getByRole('listbox').first().getByText('domain.fr').click();
    await expect(page).toHaveURL(/mail-domains\/domainfr\//);

    await expect(
      page.getByRole('heading', { name: /domain\.fr/ }).first(),
    ).toBeVisible();

    await expect(page.getByText('This table is empty')).toBeVisible();
  });

  test('checks all the elements are visible when domain exists and contains 2 pages of mailboxes', async ({
    page,
  }) => {
    const mailboxesFixtures = {
      domainFr: {
        page1: Array.from({ length: 20 }, (_, i) => ({
          id: `456ac6ca-0402-4615-8005-69bc1efde${i}f`,
          local_part: `local_part-${i}`,
          secondary_email: `secondary_email-${i}`,
        })),
        page2: Array.from({ length: 2 }, (_, i) => ({
          id: `456ac6ca-0402-4615-8005-69bc1efde${i}d`,
          local_part: `local_part-${i}`,
          secondary_email: `secondary_email-${i}`,
        })),
      },
    };
    const interceptApiCalls = async () => {
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
      await page.route('**/api/v1.0/mail-domains/domainfr', async (route) => {
        await route.fulfill({
          json: mailDomainDomainFrFixture,
        });
      });
      await page.route(
        '**/api/v1.0/mail-domains/domainfr/mailboxes/?page=1**',
        async (route) => {
          await route.fulfill({
            json: {
              count:
                mailboxesFixtures.domainFr.page1.length +
                mailboxesFixtures.domainFr.page2.length,
              next: 'http://localhost:8071/api/v1.0/mail-domains/domainfr/mailboxes/?page=2',
              previous: null,
              results: mailboxesFixtures.domainFr.page1,
            },
          });
        },
      );
      await page.route(
        '**/api/v1.0/mail-domains/domainfr/mailboxes/?page=2**',
        async (route) => {
          await route.fulfill({
            json: {
              count:
                mailboxesFixtures.domainFr.page1.length +
                mailboxesFixtures.domainFr.page2.length,
              next: null,
              previous:
                'http://localhost:8071/api/v1.0/mail-domains/domainfr/mailboxes/?page=1',
              results: mailboxesFixtures.domainFr.page2,
            },
          });
        },
      );
    };

    await interceptApiCalls();

    await clickOnMailDomainsNavButton(page);

    await expect(page).toHaveURL(/mail-domains\//);

    await page.getByRole('listbox').first().getByText('domain.fr').click();
    await expect(page).toHaveURL(/mail-domains\/domainfr\//);

    await expect(
      page.getByRole('heading', { name: 'domain.fr' }),
    ).toBeVisible();

    await expect(
      page.getByRole('button', { name: /Emails/ }).first(),
    ).toBeVisible();

    await Promise.all(
      mailboxesFixtures.domainFr.page1.map((mailbox) =>
        expect(
          page.getByText(
            `${mailbox.local_part}@${mailDomainDomainFrFixture.name}`,
          ),
        ).toBeVisible(),
      ),
    );

    await expect(
      page.locator('.c__pagination__list').getByRole('button', { name: '1' }),
    ).toBeVisible();

    await expect(
      page.locator('.c__pagination__list').getByText('navigate_next'),
    ).toBeVisible();

    await page
      .locator('.c__pagination__list')
      .getByRole('button', { name: '2' })
      .click();

    await expect(
      page.locator('.c__pagination__list').getByText('navigate_next'),
    ).toBeHidden();

    await expect(
      page.locator('.c__pagination__list').getByText('navigate_before'),
    ).toBeVisible();

    await Promise.all(
      mailboxesFixtures.domainFr.page2.map((mailbox) =>
        expect(
          page.getByText(
            `${mailbox.local_part}@${mailDomainDomainFrFixture.name}`,
          ),
        ).toBeVisible(),
      ),
    );
  });
});
