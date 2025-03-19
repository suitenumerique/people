import { Page, expect, test } from '@playwright/test';

import { keyCloakSignIn, randomName } from './common';

const getElements = (page: Page) => {
  const panel = page.getByLabel('Mail domains panel').first();
  const linkIndexPageAddDomain = page.getByRole('link', {
    name: 'Add a mail domain',
  });
  const form = page.locator('form');
  const inputName = form.getByLabel('Domain name');
  const inputSupportEmail = form.getByLabel('Support email address');
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
    inputSupportEmail,
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

    const {
      linkIndexPageAddDomain,
      inputName,
      inputSupportEmail,
      buttonSubmit,
    } = getElements(page);

    await linkIndexPageAddDomain.click();

    await expect(inputName).toBeVisible();
    await expect(inputSupportEmail).toBeVisible();
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
    const mailDomainSupportMail = 'support@'.concat(mailDomainName);
    const mailDomainSlug = mailDomainName.replace('.', '');

    await page.goto('/mail-domains/');

    const {
      linkIndexPageAddDomain,
      inputName,
      inputSupportEmail,
      buttonSubmit,
    } = getElements(page);

    await linkIndexPageAddDomain.click();

    await inputName.fill(mailDomainName);
    await inputSupportEmail.fill(mailDomainSupportMail);

    await buttonSubmit.click();

    await expect(page).toHaveURL(`/mail-domains/${mailDomainSlug}/`);

    await expect(
      page.getByRole('heading', {
        name: mailDomainName,
      }),
    ).toBeVisible();
  });

  test('checks 404 on mail-domains/[slug] page', async ({ page }) => {
    await page.goto('/mail-domains/unknown-domain');

    await expect(
      page.getByText(
        'It seems that the page you are looking for does not exist or cannot be displayed correctly.',
      ),
    ).toBeVisible();
  });
});
