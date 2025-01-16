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

const navigateToMailboxCreationFormForMailDomainFr = async (
  page: Page,
): Promise<void> => {
  await page.locator('menu').first().getByLabel(`Mail Domains button`).click();
  await page.getByRole('listbox').first().getByText('domain.fr').click();
  await page.getByRole('button', { name: 'Create a mailbox' }).click();
};

test.describe('Mail domain create mailbox', () => {
  test('checks create mailbox button is visible or not', async ({
    page,
    browserName,
  }) => {
    const domains = [...mailDomainsFixtures];
    domains[0].status = 'enabled';
    domains[1].status = 'pending';
    domains[2].status = 'disabled';
    domains[3].status = 'failed';
    await interceptCommonApiRequests(page, domains);

    await page.goto('/');
    // Login with a user who has the visibility on the mail domains
    await keyCloakSignIn(page, browserName, 'mail-member');

    await page
      .locator('menu')
      .first()
      .getByLabel(`Mail Domains button`)
      .click();
    const domainFr = page.getByRole('listbox').first().getByText('domain.fr');
    const mailsFr = page.getByRole('listbox').first().getByText('mails.fr');
    const versaillesNet = page
      .getByRole('listbox')
      .first()
      .getByText('versailles.net');
    const parisFr = page.getByRole('listbox').first().getByText('paris.fr');

    await expect(domainFr).toBeVisible();
    await expect(mailsFr).toBeVisible();
    await expect(versaillesNet).toBeVisible();
    await expect(parisFr).toBeVisible();

    // Check that the button is enabled when the domain is enabled
    await domainFr.click();
    await expect(
      page.getByRole('button', { name: 'Create a mailbox' }),
    ).toBeEnabled();

    // Check that the button is enabled when the domain is pending
    await mailsFr.click();
    await expect(
      page.getByRole('button', { name: 'Create a mailbox' }),
    ).toBeEnabled();

    // Check that the button is disabled when the domain is disabled
    await versaillesNet.click();
    await expect(
      page.getByRole('button', { name: 'Create a mailbox' }),
    ).toBeDisabled();

    // Check that the button is disabled when the domain is failed
    await parisFr.click();
    await expect(
      page.getByRole('button', { name: 'Create a mailbox' }),
    ).toBeDisabled();
  });

  test('checks user can create a mailbox when he has post ability', async ({
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
