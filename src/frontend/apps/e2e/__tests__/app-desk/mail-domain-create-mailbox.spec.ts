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
    name: 'paris.fr',
    id: '456ac6ca-0402-4615-8005-69bc1efde43h',
    created_at: currentDateIso,
    updated_at: currentDateIso,
    slug: 'parisfr',
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

const interceptCommonApiRequests = (page: Page) => {
  void page.route('**/api/v1.0/mail-domains/?page=*', (route) => {
    void route.fulfill({
      json: {
        count: mailDomainsFixtures.length,
        next: null,
        previous: null,
        results: mailDomainsFixtures,
      },
    });
  });

  void page.route('**/api/v1.0/mail-domains/domainfr/', (route) => {
    void route.fulfill({
      json: mailDomainDomainFrFixture,
    });
  });

  void page.route(
    '**/api/v1.0/mail-domains/domainfr/mailboxes/?page=1**',
    (route) => {
      void route.fulfill({
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

const navigateToMailboxCreationFormForMailDomainFr = async (
  page: Page,
): Promise<void> => {
  await page.locator('menu').first().getByLabel(`Mail Domains button`).click();
  await page.getByRole('listbox').first().getByText('domain.fr').click();
  await page.getByRole('button', { name: 'Create a mailbox' }).click();
};

test.describe('Mail domain create mailbox', () => {
  test.beforeEach(async ({ page, browserName }) => {
    await page.goto('/');
    await keyCloakSignIn(page, browserName);
  });

  test('checks user can create a mailbox when he has post ability', async ({
    page,
  }) => {
    const newMailbox = {
      id: '04433733-c9b7-453a-8122-755ac115bb00',
      local_part: 'john.doe',
      secondary_email: 'john.doe-complex2024@mail.com',
    };

    const interceptRequests = (page: Page) => {
      void interceptCommonApiRequests(page);

      void page.route(
        '**/api/v1.0/mail-domains/domainfr/mailboxes/?page=1**',
        (route) => {
          void route.fulfill({
            json: {
              count: [...mailboxesFixtures.domainFr.page1, newMailbox].length,
              next: null,
              previous: null,
              results: [...mailboxesFixtures.domainFr.page1, newMailbox],
            },
          });
        },
      );

      void page.route(
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

    void interceptRequests(page);

    await navigateToMailboxCreationFormForMailDomainFr(page);

    await page.getByRole('button', { name: 'Cancel' }).click();

    await expect(page.getByTitle('Create a mailbox')).toBeHidden();

    await page.getByRole('button', { name: 'Create a mailbox' }).click();

    await expect(page.getByTitle('Create a mailbox')).toBeVisible();
    await expect(
      page.getByRole('heading', { name: 'Create a mailbox' }),
    ).toBeVisible();

    const inputFirstName = page.getByLabel('First name');
    const inputLastName = page.getByLabel('Last name');
    const inputLocalPart = page.getByLabel('Email address prefix');
    const instructionInputLocalPart = page.getByText(
      'It must not contain spaces, accents or special characters (except "." or "-"). E.g.: jean.dupont',
    );
    const inputSecondaryEmailAddress = page.getByLabel(
      'Secondary email address',
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

    await expect(instructionInputLocalPart).toBeVisible();
    await expect(page.locator('span').getByText('@domain.fr')).toBeVisible();
    await inputSecondaryEmailAddress.fill('john.doe@mail.com');

    await page.getByRole('button', { name: 'Create the mailbox' }).click();

    expect(isCreateMailboxRequestSentWithExpectedPayload).toBeTruthy();
    await expect(page.getByTitle('Create a mailbox')).toBeHidden();
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

  test('checks user is not allowed to create a mailbox when he is missing post ability', async ({
    page,
  }) => {
    const localMailDomainsFixtures = [...mailDomainsFixtures];
    localMailDomainsFixtures[0].abilities.post = false;
    const localMailDomainDomainFr = localMailDomainsFixtures[0];
    const localMailboxFixtures = { ...mailboxesFixtures };

    const interceptRequests = (page: Page) => {
      void page.route('**/api/v1.0/mail-domains/?page=*', (route) => {
        void route.fulfill({
          json: {
            count: localMailDomainsFixtures.length,
            next: null,
            previous: null,
            results: localMailDomainsFixtures,
          },
        });
      });

      void page.route('**/api/v1.0/mail-domains/domainfr/', (route) => {
        void route.fulfill({
          json: localMailDomainDomainFr,
        });
      });

      void page.route(
        '**/api/v1.0/mail-domains/domainfr/mailboxes/?page=1**',
        (route) => {
          void route.fulfill({
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

    void interceptRequests(page);

    await page
      .locator('menu')
      .first()
      .getByLabel(`Mail Domains button`)
      .click();
    await page.getByRole('listbox').first().getByText('domain.fr').click();

    await expect(
      page.getByRole('button', { name: 'Create a mailbox' }),
    ).not.toBeInViewport();
  });
});
