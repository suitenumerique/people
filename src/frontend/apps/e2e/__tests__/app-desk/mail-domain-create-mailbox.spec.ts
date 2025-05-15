import { Page, expect, test } from '@playwright/test';
import { MailDomain } from 'app-desk/src/features/mail-domains/domains';
import { CreateMailboxParams } from 'app-desk/src/features/mail-domains/mailboxes';

import { keyCloakSignIn } from './common';

const currentDateIso = new Date().toISOString();

const mailDomainsFixtures: MailDomain[] = [
  {
    name: 'domain.fr',
    id: '456ac6ca-0402-4615-8005-69bc1efde43f',
    created_at: currentDateIso,
    updated_at: currentDateIso,
    slug: 'domainfr',
    status: 'enabled',
    support_email: 'support@domain.fr',
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
    support_email: 'support@mails.fr',
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
    status: 'enabled',
    support_email: 'support@versailles.net',
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
    status: 'enabled',
    support_email: 'support@paris.fr',
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

const mailDomainDomainFrFixture = mailDomainsFixtures[0];

const mailboxesFixtures = {
  domainFr: {
    page1: Array.from({ length: 1 }, (_, i) => ({
      id: `456ac6ca-0402-4615-8005-69bc1efde${i}f`,
      local_part: `local_part-${i}`,
      secondary_email: `secondary_email-${i}`,
    })),
  },
};

const interceptCommonApiRequests = async (
  page: Page,
  mailDomains?: MailDomain[],
) => {
  const mailDomainsToUse = mailDomains ?? mailDomainsFixtures;
  await page.route('**/api/v1.0/mail-domains/?page=*', async (route) => {
    await route.fulfill({
      json: {
        count: mailDomainsToUse.length,
        next: null,
        previous: null,
        results: mailDomainsToUse,
      },
    });
  });

  await Promise.all(
    mailDomainsToUse.map(async (mailDomain) => {
      await page.route(
        `**/api/v1.0/mail-domains/${mailDomain.slug}/`,
        async (route) => {
          await route.fulfill({
            json: mailDomain,
          });
        },
      );
    }),
  );

  await Promise.all(
    mailDomainsToUse.map(async (mailDomain) => {
      await page.route(
        `**/api/v1.0/mail-domains/${mailDomain.slug}/mailboxes/?page=1**`,
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
    }),
  );
};

test.describe('Mail domain create mailbox', () => {
  test('checks user can New mail address when he has post ability', async ({
    page,
    browserName,
  }) => {
    const newMailbox = {
      id: '04433733-c9b7-453a-8122-755ac115bb00',
      local_part: 'john.doe',
      secondary_email: 'john.doe-complex2024@mail.com',
    };

    const interceptRequests = async (page: Page) => {
      await interceptCommonApiRequests(page);

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
        async (route) => {
          if (route.request().method() === 'POST') {
            await route.fulfill({
              json: newMailbox,
            });
          } else {
            await route.continue();
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
        const payload = request.postDataJSON() as Omit<
          CreateMailboxParams,
          'mailDomainId'
        >;

        if (payload) {
          isCreateMailboxRequestSentWithExpectedPayload =
            payload.first_name === 'John' &&
            payload.last_name === 'Doe' &&
            payload.local_part === 'john.doe' &&
            payload.secondary_email === 'john.doe@mail.com';
        }
      }
    });

    await interceptRequests(page);

    await page.goto('/');
    // Login with a user who has the visibility on the mail domains
    await keyCloakSignIn(page, browserName, 'mail-member');

    await page.goto('/mail-domains/');

    await page.getByLabel(`domain.fr listboxDomains button`).click();

    await page.getByTestId('button-new-mailbox').click();

    await expect(page.getByText('New email account')).toBeVisible();

    const inputFirstName = page.getByLabel('First name');
    const inputLastName = page.getByLabel('Last name');
    const inputLocalPart = page.getByLabel('Name of the new address');
    const inputSecondaryEmailAddress = page.getByLabel(
      'Personal email address',
    );

    await expect(inputFirstName).toHaveAttribute('aria-required', 'true');
    await expect(inputFirstName).toHaveAttribute('required', '');
    await expect(inputLastName).toHaveAttribute('aria-required', 'true');
    await expect(inputLastName).toHaveAttribute('required', '');
    await expect(inputLocalPart).toHaveAttribute('aria-required', 'true');
    await expect(inputLocalPart).toHaveAttribute('required', '');
    await expect(inputSecondaryEmailAddress).toHaveAttribute(
      'aria-required',
      'true',
    );
    await expect(inputSecondaryEmailAddress).toHaveAttribute('required', '');

    await inputFirstName.fill('John');
    await inputLastName.fill('Doe');
    await inputLocalPart.fill('john.doe');

    await expect(page.locator('span').getByText('@domain.fr')).toBeVisible();
    await inputSecondaryEmailAddress.fill('john.doe@mail.com');

    await page.getByRole('button', { name: 'Create' }).click();

    expect(isCreateMailboxRequestSentWithExpectedPayload).toBeTruthy();
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

  test('checks user is not allowed to New mail address when he is missing post ability', async ({
    page,
    browserName,
  }) => {
    const localMailDomainsFixtures = [...mailDomainsFixtures];
    localMailDomainsFixtures[0].abilities.post = false;
    const localMailDomainDomainFr = localMailDomainsFixtures[0];
    const localMailboxFixtures = { ...mailboxesFixtures };

    const interceptRequests = async (page: Page) => {
      await page.route('**/api/v1.0/mail-domains/?page=*', async (route) => {
        await route.fulfill({
          json: {
            count: localMailDomainsFixtures.length,
            next: null,
            previous: null,
            results: localMailDomainsFixtures,
          },
        });
      });

      await page.route('**/api/v1.0/mail-domains/domainfr/', async (route) => {
        await route.fulfill({
          json: localMailDomainDomainFr,
        });
      });

      await page.route(
        '**/api/v1.0/mail-domains/domainfr/mailboxes/?page=1**',
        async (route) => {
          await route.fulfill({
            json: {
              count: localMailboxFixtures.domainFr.page1.length,
              next: null,
              previous: null,
              results: localMailboxFixtures.domainFr.page1,
            },
          });
        },
        { times: 1 },
      );
    };

    await interceptRequests(page);

    await page.goto('/');
    // Login with a user who has the visibility on the mail domains
    await keyCloakSignIn(page, browserName, 'mail-member');

    await page.goto('/mail-domains');

    await page.getByLabel(`domain.fr listboxDomains button`).click();

    await expect(page.getByTestId('button-new-mailbox')).toBeDisabled();
  });
});
