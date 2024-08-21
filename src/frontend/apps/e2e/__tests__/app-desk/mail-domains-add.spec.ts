import { Page, expect, test } from '@playwright/test';

import { keyCloakSignIn, randomName } from './common';

const getElements = (page: Page) => {
  const panel = page.getByLabel('Mail domains panel').first();
  const linkIndexPageAddDomain = page.getByRole('link', {
    name: 'Add a mail domain',
  });
  const form = page.locator('form');
  const inputName = form.getByLabel('Domain name');
  const buttonSubmit = page.getByRole('button', {
    name: 'Add the domain',
  });

  const buttonCancel = page.getByRole('button', {
    name: 'Cancel',
  });

  return {
    panel,
    linkIndexPageAddDomain,
    form,
    inputName,
    buttonCancel,
    buttonSubmit,
  };
};

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Add Mail Domains', () => {
  test('checks all the elements are visible', async ({ page }) => {
    await page.goto('/mail-domains/');

    const { linkIndexPageAddDomain, inputName } = getElements(page);

    await expect(linkIndexPageAddDomain).toBeVisible();
    await linkIndexPageAddDomain.click();

    await expect(linkIndexPageAddDomain).toBeHidden();

    await expect(
      page.getByRole('heading', {
        name: 'Add a mail domain',
        level: 3,
      }),
    ).toBeVisible();

    await expect(inputName).toBeVisible();

    await expect(page.getByText('Example: saint-laurent.fr')).toBeVisible();

    await expect(
      page.getByRole('button', {
        name: 'Add the domain',
      }),
    ).toBeVisible();
    await expect(
      page.getByRole('button', {
        name: 'Cancel',
      }),
    ).toBeVisible();
  });

  test('checks the cancel button interaction', async ({ page }) => {
    await page.goto('/mail-domains/');

    const { linkIndexPageAddDomain, buttonCancel } = getElements(page);

    await linkIndexPageAddDomain.click();
    await buttonCancel.click();

    await expect(buttonCancel).toBeHidden();

    await expect(linkIndexPageAddDomain).toBeVisible();
  });

  test('checks form invalid status', async ({ page }) => {
    await page.goto('/mail-domains/');

    const { linkIndexPageAddDomain, inputName, buttonSubmit } =
      getElements(page);

    await linkIndexPageAddDomain.click();

    await expect(inputName).toBeVisible();
    await expect(page.getByText('Example: saint-laurent.fr')).toBeVisible();

    await expect(
      page.getByRole('button', {
        name: 'Cancel',
      }),
    ).toBeEnabled();

    await expect(buttonSubmit).toBeDisabled();

    await inputName.fill('s');
    await expect(page.getByText('Example: saint-laurent.fr')).toBeVisible();

    await inputName.clear();

    await expect(page.getByText('Example: saint-laurent.fr')).toBeVisible();
  });

  test('checks the routing on new mail domain added', async ({
    page,
    browserName,
  }) => {
    const mailDomainName = randomName('versailles.fr', browserName, 1)[0];
    const mailDomainSlug = mailDomainName.replace('.', '');

    await page.goto('/mail-domains/');

    const { linkIndexPageAddDomain, inputName, buttonSubmit } =
      getElements(page);

    await linkIndexPageAddDomain.click();

    await inputName.fill(mailDomainName);
    await buttonSubmit.click();

    await expect(page).toHaveURL(`/mail-domains/${mailDomainSlug}/`);

    await expect(
      page.getByRole('heading', {
        name: mailDomainName,
      }),
    ).toBeVisible();
  });

  test('checks form submits at "Enter" key press', async ({ page }) => {
    void page.route('**/api/v1.0/mail-domains/', (route) => {
      if (route.request().method() === 'POST') {
        void route.fulfill({
          json: {
            id: '2ebcfcfb-1dfa-4ed1-8e4a-554c63307b7c',
            name: 'enter.fr',
            slug: 'enterfr',
            status: 'pending',
            abilities: {
              get: true,
              patch: true,
              put: true,
              post: true,
              delete: true,
              manage_accesses: true,
            },
            created_at: '2024-08-21T10:55:21.081994Z',
            updated_at: '2024-08-21T10:55:21.082109Z',
          },
        });
      } else {
        void route.continue();
      }
    });

    await page.goto('/mail-domains/');

    const { linkIndexPageAddDomain, inputName } = getElements(page);

    await linkIndexPageAddDomain.click();

    await inputName.fill('enter.fr');
    await page.keyboard.press('Enter');

    await expect(page).toHaveURL(`/mail-domains/enterfr/`);
  });

  test('checks error when duplicate mail domain name', async ({
    page,
    browserName,
  }) => {
    await page.goto('/mail-domains/');

    const { linkIndexPageAddDomain, inputName, buttonSubmit } =
      getElements(page);

    const mailDomainName = randomName('duplicate.fr', browserName, 1)[0];
    const mailDomainSlug = mailDomainName.replace('.', '');

    await linkIndexPageAddDomain.click();
    await inputName.fill(mailDomainName);
    await buttonSubmit.click();

    await expect(page).toHaveURL(`/mail-domains\/${mailDomainSlug}\/`);

    await linkIndexPageAddDomain.click();

    await inputName.fill(mailDomainName);
    await buttonSubmit.click();

    await expect(page).toHaveURL(/mail-domains\//);
    await expect(
      page.getByText(
        'This mail domain is already used. Please, choose another one.',
      ),
    ).toBeVisible();
    await expect(inputName).toBeFocused();
  });

  test('checks error when duplicate mail domain slug', async ({
    page,
    browserName,
  }) => {
    await page.goto('/mail-domains/');

    const { linkIndexPageAddDomain, inputName, buttonSubmit } =
      getElements(page);

    const mailDomainSlug = randomName('duplicate', browserName, 1)[0];

    await linkIndexPageAddDomain.click();
    await inputName.fill(mailDomainSlug);
    await buttonSubmit.click();

    await expect(page).toHaveURL(`/mail-domains\/${mailDomainSlug}\/`);

    await linkIndexPageAddDomain.click();

    await inputName.fill(mailDomainSlug);
    await buttonSubmit.click();

    await expect(page).toHaveURL(/mail-domains\//);
    await expect(
      page.getByText(
        'This mail domain is already used. Please, choose another one.',
      ),
    ).toBeVisible();
    await expect(inputName).toBeFocused();
  });

  test('checks unknown api error causes are displayed', async ({ page }) => {
    await page.route(
      '**/api/v1.0/mail-domains/',
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

    await page.goto('/mail-domains/');

    const { linkIndexPageAddDomain, inputName, buttonSubmit } =
      getElements(page);

    await linkIndexPageAddDomain.click();
    await inputName.fill('server-error.fr');
    await buttonSubmit.click();

    await expect(page).toHaveURL(/mail-domains\//);
    await expect(
      page.getByText(
        'Your request cannot be processed because the server is experiencing an error. If the problem ' +
          'persists, please contact our support to resolve the issue: suiteterritoriale@anct.gouv.fr.',
      ),
    ).toBeVisible();
    await expect(inputName).toBeFocused();
  });

  test('checks 404 on mail-domains/[slug] page', async ({ page }) => {
    await page.goto('/mail-domains/unknown-domain');

    await expect(
      page.getByText(
        'It seems that the page you are looking for does not exist or cannot be displayed correctly.',
      ),
    ).toBeVisible({
      timeout: 15000,
    });
  });
});
