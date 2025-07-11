import { Page, expect, test } from '@playwright/test';
import { MailDomain } from 'app-desk/src/features/mail-domains/domains';

import { keyCloakSignIn } from './common';

const currentDateIso = new Date().toISOString();

const interceptCommonApiCalls = async (
  page: Page,
  arrayMailDomains: MailDomain[],
) => {
  const singleMailDomain = arrayMailDomains[0];
  await page.route('**/api/v1.0/mail-domains/\?*', async (route) => {
    await route.fulfill({
      json: {
        count: arrayMailDomains.length,
        next: null,
        previous: null,
        results: arrayMailDomains,
      },
    });
  });

  await page.route('**/api/v1.0/mail-domains/domainfr/', async (route) => {
    await route.fulfill({
      json: singleMailDomain,
    });
  });

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
};
const clickOnMailDomainsNavButton = async (page: Page): Promise<void> =>
  await page.locator('menu').getByLabel(`Mail Domains button`).click();

const assertMailDomainUpperElementsAreVisible = async (page: Page) => {
  await expect(page).toHaveURL(/mail-domains\//);

  await expect(page.getByText('domain.fr', { exact: true })).toBeVisible();
  await page.getByLabel(`domain.fr listboxDomains button`).click();

  await expect(page).toHaveURL(/mail-domains\/domainfr\//);

  await expect(page.getByRole('heading', { name: 'domain.fr' })).toBeVisible();
};

const assertFilledMailboxesTableElementsAreVisible = async (
  page: Page,
  domainFr: object & { name: string },
  multiLevelArrayMailboxes: object & Array<{ local_part: string }[]>,
) => {
  await expect(page).toHaveURL(/mail-domains\//);

  await Promise.all(
    multiLevelArrayMailboxes[0].map((mailbox) =>
      expect(
        page.getByText(`${mailbox.local_part}@${domainFr.name}`),
      ).toBeVisible(),
    ),
  );

  const table = page.locator('table');
  await expect(table).toBeVisible();

  const tdNames = await table.getByText('John Doe').all();
  expect(tdNames.length).toEqual(20);
};

test.describe('Mail domain', () => {
  test('redirects to 404 page when the mail domain requested does not exist', async ({
    page,
    browserName,
  }) => {
    await page.goto('/');
    await keyCloakSignIn(page, browserName);

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
    await page.waitForURL('/404/');
    await expect(
      page.getByText(
        'It seems that the page you are looking for does not exist or cannot be displayed correctly.',
      ),
    ).toBeVisible();
  });

  test.describe('user is administrator or owner', () => {
    test.describe('mail domain is enabled', () => {
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

      test('checks all the elements are visible when domain exist but contains no mailboxes', async ({
        page,
        browserName,
      }) => {
        await interceptCommonApiCalls(page, mailDomainsFixtures);

        await page.goto('/');
        await keyCloakSignIn(page, browserName, 'mail-owner');

        await clickOnMailDomainsNavButton(page);

        await assertMailDomainUpperElementsAreVisible(page);

        await expect(page.getByTestId('button-new-mailbox')).toBeVisible();

        await expect(
          page.getByText('No mail box was created with this mail domain.'),
        ).toBeVisible();
      });

      test('can disable and enable mailbox', async ({ page, browserName }) => {
        await page.goto('/');
        await keyCloakSignIn(page, browserName, 'mail-owner');

        await clickOnMailDomainsNavButton(page);

        // Go to the enabled-domain.com management page
        await expect(page).toHaveURL(/mail-domains\//);
        await expect(
          page.getByText('enabled-domain.com', { exact: true }),
        ).toBeVisible();
        await page
          .getByLabel(`enabled-domain.com listboxDomains button`)
          .click();
        await expect(page).toHaveURL(/mail-domains\/enabled-domaincom\//);
        await expect(
          page.getByRole('heading', { name: 'enabled-domain.com' }),
        ).toBeVisible();

        // Click new mailbox button
        await page.getByTestId('button-new-mailbox').click();

        // Fill in mailbox form with random string
        const randomString = Math.random().toString(36).substring(2, 8);
        await page.getByLabel('First name').fill('John');
        await page.getByLabel('Last name').fill('Doe');
        await page.getByLabel('Name of the new address').fill(randomString);
        await page
          .getByLabel('Personal email address')
          .fill(`${randomString}@example.com`);

        // Submit form
        await page.getByRole('button', { name: 'Create' }).click();

        // Verify success toast appears
        await expect(page.getByText('Mailbox created!')).toBeVisible();

        // Verify mailbox appears in list
        await expect(
          page.getByText(`${randomString}@enabled-domain.com`),
        ).toBeVisible();

        // Click the options button for the specific mailbox
        await page
          .getByRole('row', { name: `${randomString}@enabled-domain.com` })
          .getByLabel('Open the access options modal')
          .click();

        // Click disable button
        await page.getByText('Disable mailbox').click();

        // Verify modal appears
        await expect(
          page.getByText('Are you sure you want to disable this mailbox?'),
        ).toBeVisible();

        // Click disable in modal
        await page.getByRole('button', { name: 'Disable' }).click();

        // Verify mailbox status shows as disabled
        await expect(
          page
            .getByRole('row', { name: `${randomString}@enabled-domain.com` })
            .getByText('Disabled'),
        ).toBeVisible();

        // Click options button again
        await page
          .getByRole('row', { name: `${randomString}@enabled-domain.com` })
          .getByLabel('Open the access options modal')
          .click();

        // Click enable button
        await page.getByText('Enable mailbox').click();

        // Verify mailbox status shows as enabled
        await expect(
          page
            .getByRole('row', { name: `${randomString}@enabled-domain.com` })
            .getByText('Enabled'),
        ).toBeVisible();
      });
    });

    test.describe('mail domain creation is pending', () => {
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
      ];

      test('checks expected elements are visible', async ({
        page,
        browserName,
      }) => {
        await interceptCommonApiCalls(page, mailDomainsFixtures);

        await page.goto('/');
        await keyCloakSignIn(page, browserName, 'mail-owner');

        await clickOnMailDomainsNavButton(page);

        await expect(page).toHaveURL(/mail-domains\//);

        await page.getByLabel(`domain.fr listboxDomains button`).click();

        await expect(page).toHaveURL(/mail-domains\/domainfr\//);

        await expect(
          page.getByRole('heading', { name: 'domain.fr' }),
        ).toBeVisible();

        await expect(page.getByTestId('button-new-mailbox')).toBeVisible();

        await expect(
          page.getByText('No mail box was created with this mail domain.'),
        ).toBeVisible();
      });
    });

    test.describe('mail domain is disabled', () => {
      const mailDomainsFixtures: MailDomain[] = [
        {
          name: 'domain.fr',
          id: '456ac6ca-0402-4615-8005-69bc1efde43f',
          created_at: currentDateIso,
          updated_at: currentDateIso,
          slug: 'domainfr',
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
      ];

      test('checks expected elements are visible', async ({
        page,
        browserName,
      }) => {
        await interceptCommonApiCalls(page, mailDomainsFixtures);

        await page.goto('/');
        await keyCloakSignIn(page, browserName, 'mail-owner');

        await clickOnMailDomainsNavButton(page);

        await assertMailDomainUpperElementsAreVisible(page);

        await expect(
          page.getByText(
            'This domain name is deactivated. No new mailboxes can be created.',
          ),
        ).toBeVisible();

        await expect(page.getByTestId('button-new-mailbox')).toBeDisabled();

        await expect(
          page.getByText('No mail box was created with this mail domain.'),
        ).toBeVisible();
      });
    });

    test.describe('mail domain creation has failed', () => {
      const mailDomainsFixtures: MailDomain[] = [
        {
          name: 'domain.fr',
          id: '456ac6ca-0402-4615-8005-69bc1efde43f',
          created_at: currentDateIso,
          updated_at: currentDateIso,
          slug: 'domainfr',
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

      test('checks expected elements are visible', async ({
        page,
        browserName,
      }) => {
        await interceptCommonApiCalls(page, mailDomainsFixtures);

        await page.goto('/');
        await keyCloakSignIn(page, browserName, 'mail-owner');

        await clickOnMailDomainsNavButton(page);

        await assertMailDomainUpperElementsAreVisible(page);

        await expect(
          page.getByText(
            'The domain name encounters an error. Please contact our support team to solve the problem:',
          ),
        ).toBeVisible();

        await expect(
          page.getByRole('link', { name: 'suiteterritoriale@anct.gouv.fr' }),
        ).toBeVisible();

        await expect(page.getByTestId('button-new-mailbox')).toBeDisabled();

        await expect(
          page.getByText('No mail box was created with this mail domain.'),
        ).toBeVisible();
      });
    });
  });

  test.describe('user is member', () => {
    test.describe('mail domain is enabled', () => {
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
            patch: false,
            put: false,
            post: false,
            delete: false,
            manage_accesses: false,
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
            patch: false,
            put: false,
            post: false,
            delete: false,
            manage_accesses: false,
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
            patch: false,
            put: false,
            post: false,
            delete: false,
            manage_accesses: false,
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
            patch: false,
            put: false,
            post: false,
            delete: false,
            manage_accesses: false,
          },
        },
      ];

      test('checks all the elements are visible when domain exist but contains no mailboxes', async ({
        page,
        browserName,
      }) => {
        await interceptCommonApiCalls(page, mailDomainsFixtures);

        await page.goto('/');
        await keyCloakSignIn(page, browserName, 'mail-member');

        await clickOnMailDomainsNavButton(page);

        await assertMailDomainUpperElementsAreVisible(page);

        await expect(
          page.getByText('No mail box was created with this mail domain.'),
        ).toBeVisible();
      });

      test('checks all the elements are visible when domain exists and contains 2 pages of mailboxes', async ({
        page,
        browserName,
      }) => {
        const mailboxesFixtures = {
          domainFr: {
            page1: Array.from({ length: 20 }, (_, i) => ({
              id: `456ac6ca-0402-4615-8005-69bc1efde${i}f`,
              first_name: 'john',
              last_name: 'doe',
              local_part: `local_part-${i}`,
              secondary_email: `secondary_email-${i}`,
            })),
            page2: Array.from({ length: 2 }, (_, i) => ({
              id: `456ac6ca-0402-4615-8005-69bc1efde${i}d`,
              first_name: 'john',
              last_name: 'doe',
              local_part: `local_part-${i}`,
              secondary_email: `secondary_email-${i}`,
            })),
          },
        };
        const interceptApiCalls = async () => {
          await page.route(
            '**/api/v1.0/mail-domains/?page=*',
            async (route) => {
              await route.fulfill({
                json: {
                  count: mailDomainsFixtures.length,
                  next: null,
                  previous: null,
                  results: mailDomainsFixtures,
                },
              });
            },
          );
          await page.route(
            '**/api/v1.0/mail-domains/domainfr/',
            async (route) => {
              await route.fulfill({
                json: mailDomainsFixtures[0],
              });
            },
          );
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

        await page.goto('/');
        await keyCloakSignIn(page, browserName, 'mail-member');

        await clickOnMailDomainsNavButton(page);

        await assertMailDomainUpperElementsAreVisible(page);

        await expect(page.getByTestId('button-new-mailbox')).toBeDisabled();

        await assertFilledMailboxesTableElementsAreVisible(
          page,
          mailDomainsFixtures[0],
          [mailboxesFixtures.domainFr.page1, mailboxesFixtures.domainFr.page2],
        );
      });
    });

    test.describe('mail domain creation is pending', () => {
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
            patch: false,
            put: false,
            post: false,
            delete: false,
            manage_accesses: false,
          },
        },
      ];

      test('checks expected elements are visible', async ({
        page,
        browserName,
      }) => {
        await interceptCommonApiCalls(page, mailDomainsFixtures);

        await page.goto('/');
        await keyCloakSignIn(page, browserName, 'mail-member');

        await clickOnMailDomainsNavButton(page);

        await expect(page).toHaveURL(/mail-domains\//);

        await page.getByLabel(`domain.fr listboxDomains button`).click();

        await expect(page).toHaveURL(/mail-domains\/domainfr\//);

        await expect(
          page.getByRole('heading', { name: 'domain.fr' }),
        ).toBeVisible();

        await expect(page.getByTestId('button-new-mailbox')).toBeDisabled();

        await expect(
          page.getByText('No mail box was created with this mail domain.'),
        ).toBeVisible();
      });
    });

    test.describe('mail domain is disabled', () => {
      const mailDomainsFixtures: MailDomain[] = [
        {
          name: 'domain.fr',
          id: '456ac6ca-0402-4615-8005-69bc1efde43f',
          created_at: currentDateIso,
          updated_at: currentDateIso,
          slug: 'domainfr',
          status: 'disabled',
          abilities: {
            get: true,
            patch: false,
            put: false,
            post: false,
            delete: false,
            manage_accesses: false,
          },
        },
      ];

      test('checks expected elements are visible', async ({
        page,
        browserName,
      }) => {
        await interceptCommonApiCalls(page, mailDomainsFixtures);

        await page.goto('/');
        await keyCloakSignIn(page, browserName, 'mail-member');

        await clickOnMailDomainsNavButton(page);

        await assertMailDomainUpperElementsAreVisible(page);

        await expect(
          page.getByText(
            'This domain name is deactivated. No new mailboxes can be created.',
          ),
        ).toBeVisible();

        await expect(page.getByTestId('button-new-mailbox')).toBeDisabled();

        await expect(
          page.getByText('No mail box was created with this mail domain.'),
        ).toBeVisible();
      });
    });

    test.describe('mail domain creation has failed', () => {
      const mailDomainsFixtures: MailDomain[] = [
        {
          name: 'domain.fr',
          id: '456ac6ca-0402-4615-8005-69bc1efde43f',
          created_at: currentDateIso,
          updated_at: currentDateIso,
          slug: 'domainfr',
          status: 'failed',
          abilities: {
            get: true,
            patch: false,
            put: false,
            post: false,
            delete: false,
            manage_accesses: false,
          },
        },
      ];

      test('checks expected elements are visible', async ({
        page,
        browserName,
      }) => {
        await interceptCommonApiCalls(page, mailDomainsFixtures);

        await page.goto('/');
        await keyCloakSignIn(page, browserName, 'mail-member');

        await clickOnMailDomainsNavButton(page);

        await assertMailDomainUpperElementsAreVisible(page);

        await expect(
          page.getByText(
            'The domain name encounters an error. Please contact our support team to solve the problem:',
          ),
        ).toBeVisible();

        await expect(page.getByTestId('button-new-mailbox')).toBeDisabled();

        await expect(
          page.getByText('No mail box was created with this mail domain.'),
        ).toBeVisible();
      });
    });
  });
});
