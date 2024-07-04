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

  void page.route('**/api/v1.0/mail-domains/domainfr', (route) => {
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

  // user should have administrator or owner role on this domain to be able perform this action
  test('checks user can create a mailbox for a mail domain', async ({
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
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        const payload: Omit<CreateMailboxParams, 'mailDomainId'> =
          request.postDataJSON();

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

    await expect(page.getByTitle('Mailbox creation form')).toBeHidden();

    await page.getByRole('button', { name: 'Create a mailbox' }).click();

    await expect(page.getByTitle('Mailbox creation form')).toBeVisible();
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

  test('checks client invalidation messages are displayed and no mailbox creation request is sent when fields are not properly filled', async ({
    page,
  }) => {
    let isCreateMailboxRequestSent = false;
    page.on(
      'request',
      (request) =>
        (isCreateMailboxRequestSent =
          request.url().includes('/mail-domains/domainfr/mailboxes/') &&
          request.method() === 'POST'),
    );

    void interceptCommonApiRequests(page);

    await navigateToMailboxCreationFormForMailDomainFr(page);

    const inputFirstName = page.getByLabel('First name');
    const inputLastName = page.getByLabel('Last name');
    const inputLocalPart = page.getByLabel('Email address prefix');
    const inputSecondaryEmailAddress = page.getByLabel(
      'Secondary email address',
    );
    const textInvalidLocalPart = page.getByText(
      'It must not contain spaces, accents or special characters (except "." or "-"). E.g.: jean.dupont',
    );
    const textInvalidSecondaryEmailAddress = page.getByText(
      'Please enter a valid email address.\nE.g. : jean.dupont@mail.fr',
    );

    await inputFirstName.fill(' ');
    await inputFirstName.clear();
    await expect(page.getByText('Please enter your first name')).toBeVisible();

    await inputLastName.fill(' ');
    await inputLastName.clear();
    await expect(page.getByText('Please enter your last name')).toBeVisible();

    await inputLocalPart.fill('wrong@');
    await expect(textInvalidLocalPart).toBeVisible();

    await inputSecondaryEmailAddress.fill('uncomplete@mail');
    await expect(textInvalidSecondaryEmailAddress).toBeVisible();

    await inputLocalPart.clear();
    await inputLocalPart.fill('wrong ');
    await expect(textInvalidLocalPart).toBeVisible();

    await inputLocalPart.clear();
    await expect(
      page.getByText('You must have minimum 1 character'),
    ).toBeVisible();

    await page.getByRole('button', { name: 'Create the mailbox' }).click();

    expect(isCreateMailboxRequestSent).toBeFalsy();
  });

  test('checks field invalidation messages are displayed when sending already existing local_part data in mail domain to api', async ({
    page,
  }) => {
    const interceptRequests = (page: Page) => {
      void interceptCommonApiRequests(page);

      void page.route(
        '**/api/v1.0/mail-domains/domainfr/mailboxes/',
        (route) => {
          if (route.request().method() === 'POST') {
            void route.fulfill({
              status: 400,
              json: {
                local_part: [
                  'Mailbox with this Local_part and Domain already exists.',
                ],
              },
            });
          }
        },
        { times: 1 },
      );
    };

    void interceptRequests(page);

    await navigateToMailboxCreationFormForMailDomainFr(page);

    const inputFirstName = page.getByLabel('First name');
    const inputLastName = page.getByLabel('Last name');
    const inputLocalPart = page.getByLabel('Email address prefix');
    const inputSecondaryEmailAddress = page.getByLabel(
      'Secondary email address',
    );
    const submitButton = page.getByRole('button', {
      name: 'Create the mailbox',
    });

    const textAlreadyUsedLocalPart = page.getByText(
      'This email prefix is already used.',
    );

    await inputFirstName.fill('John');
    await inputLastName.fill('Doe');
    await inputLocalPart.fill('john.already');
    await inputSecondaryEmailAddress.fill('john.already@mail.com');

    await submitButton.click();

    await expect(textAlreadyUsedLocalPart).toBeVisible();
  });

  test('checks unknown api error causes are displayed above form when they are not related with invalid field', async ({
    page,
  }) => {
    const interceptRequests = async (page: Page) => {
      void interceptCommonApiRequests(page);

      await page.route(
        '**/api/v1.0/mail-domains/domainfr/mailboxes/',
        async (route) => {
          if (route.request().method() === 'POST') {
            await route.fulfill({
              status: 500,
              json: {
                unknown_error: ['Unknown error from server'],
              },
            });
          }
        },
        { times: 1 },
      );
    };

    void interceptRequests(page);

    await navigateToMailboxCreationFormForMailDomainFr(page);

    const inputFirstName = page.getByLabel('First name');
    const inputLastName = page.getByLabel('Last name');
    const inputLocalPart = page.getByLabel('Email address prefix');
    const inputSecondaryEmailAddress = page.getByLabel(
      'Secondary email address',
    );

    await inputFirstName.fill('John');
    await inputLastName.fill('Doe');
    await inputLocalPart.fill('john.doe');

    await inputSecondaryEmailAddress.fill('john.do@mail.fr');

    await page.getByRole('button', { name: 'Create the mailbox' }).click();

    await expect(page.getByText('Unknown error from server')).toBeVisible();
  });
});
