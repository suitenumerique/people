import { Page, expect, test } from '@playwright/test';
import {
  CreateMailboxParams,
  MailDomain,
} from 'app-desk/src/features/mail-domains';

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

test.describe('Mail domain create mailbox', () => {
  test.beforeEach(async ({ page, browserName }) => {
    await page.goto('/');
    await keyCloakSignIn(page, browserName);
  });

  // user should have administrator or owner role on this domain to be able perform this action
  test('checks user can create a mailbox for a mail domain', async ({
    page,
  }) => {
    const mailboxesFixtures = {
      domainFr: {
        page1: Array.from({ length: 1 }, (_, i) => ({
          id: `456ac6ca-0402-4615-8005-69bc1efde${i}f`,
          local_part: `local_part-${i}`,
          secondary_email: `secondary_email-${i}`,
        })),
      },
    };

    const newMailbox = {
      id: '04433733-c9b7-453a-8122-755ac115bb00',
      local_part: 'john.doe',
      secondary_email: 'john.doe@mail.com',
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
              count: mailboxesFixtures.domainFr.page1.length,
              next: null,
              previous: null,
              results: mailboxesFixtures.domainFr.page1,
            },
          });
        },
        { times: 1 },
      );

      await page.route(
        '**/api/v1.0/mail-domains/domainfr/mailboxes/?page=1**',
        async (route) => {
          await route.fulfill({
            json: {
              count: [...mailboxesFixtures.domainFr.page1, newMailbox].length,
              next: null,
              previous: null,
              results: [...mailboxesFixtures.domainFr.page1, newMailbox],
            },
          });
        },
      );

      await page.route(
        '**/api/v1.0/mail-domains/domainfr/mailboxes/',
        (route) => {
          if (route.request().method() === 'POST') {
            void route.fulfill({
              json: newMailbox,
            });
          } else {
            void route.continue();
          }
        },
      );
    };

    let isCreateMailboxRequestSentWithExpectedPayload = false;
    page.on('request', (request) => {
      if (
        request.url().includes('/mail-domains/domainfr/mailboxes/') &&
        request.method() === 'POST'
      ) {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        const payload: Omit<CreateMailboxParams, 'mailDomainId'> =
          request.postDataJSON();

        if (payload) {
          isCreateMailboxRequestSentWithExpectedPayload =
            payload.first_name === 'John' &&
            payload.last_name === 'Doe' &&
            payload.local_part === 'john.doe' &&
            payload.secondary_email === 'john.doe@mail.com' &&
            payload.phone_number === '003371020304050';
        }
      }
    });

    await interceptApiCalls();

    await clickOnMailDomainsNavButton(page);

    await page.getByRole('listbox').first().getByText('domain.fr').click();

    await page.getByRole('button', { name: 'Create a mailbox' }).click();
    await page.getByRole('button', { name: 'Cancel' }).click();

    await expect(page.getByTitle('Mailbox creation form')).toBeHidden();

    await page.getByRole('button', { name: 'Create a mailbox' }).click();

    await expect(page.getByTitle('Mailbox creation form')).toBeVisible();
    await expect(
      page.getByRole('heading', { name: 'Create a mailbox' }),
    ).toBeVisible();

    await page.getByLabel('First name').fill('John');
    await page.getByLabel('Last name').fill('Doe');
    await page.getByLabel('Main email address').fill('john.doe');
    await expect(page.locator('span').getByText('@domain.fr')).toBeVisible();
    await page.getByLabel('Secondary email address').fill('john.doe@mail.com');
    await page.getByLabel('Phone number').fill('003371020304050');

    await page.getByRole('button', { name: 'Submit' }).click();

    expect(isCreateMailboxRequestSentWithExpectedPayload).toBeTruthy();
    await expect(page.getByAltText('Mailbox creation form')).toBeHidden();
    await expect(page.getByText('Mailbox created!')).toBeVisible({
      timeout: 1500,
    });

    await Promise.all(
      [...mailboxesFixtures.domainFr.page1, newMailbox].map((mailbox) =>
        expect(
          page.getByText(
            `${mailbox.local_part}@${mailDomainDomainFrFixture.name}`,
          ),
        ).toBeVisible(),
      ),
    );
  });

  test('checks client invalidation messages are displayed when fields are not properly filled', async ({
    page,
  }) => {
    const mailboxesFixtures = {
      domainFr: {
        page1: Array.from({ length: 1 }, (_, i) => ({
          id: `456ac6ca-0402-4615-8005-69bc1efde${i}f`,
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
              count: mailboxesFixtures.domainFr.page1.length,
              next: null,
              previous: null,
              results: mailboxesFixtures.domainFr.page1,
            },
          });
        },
        { times: 1 },
      );
    };

    let isCreateMailboxRequestSent = false;
    page.on('request', (request) => {
      if (
        request.url().includes('/mail-domains/domainfr/mailboxes/') &&
        request.method() === 'POST'
      ) {
        isCreateMailboxRequestSent = true;
      }
    });

    await interceptApiCalls();

    await clickOnMailDomainsNavButton(page);

    await page.getByRole('listbox').first().getByText('domain.fr').click();

    await page.getByRole('button', { name: 'Create a mailbox' }).click();

    await page.getByRole('button', { name: 'Submit' }).click();

    await expect(page.getByText('Please enter your first name')).toBeVisible();
    await expect(page.getByText('Please enter your last name')).toBeVisible();
    await expect(
      page.getByText(
        'Please enter the first part of the email address, without including "@" in it',
      ),
    ).toBeVisible();
    await expect(
      page.getByText('Please enter your secondary email address'),
    ).toBeVisible();
    await expect(
      page.getByText('Please enter your phone number'),
    ).toBeVisible();

    expect(isCreateMailboxRequestSent).toBeFalsy();
  });
});
