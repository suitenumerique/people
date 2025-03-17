import { Page, expect, test } from '@playwright/test';

import { keyCloakSignIn, randomName } from './common';

const getElements = (page: Page) => {
  const modal = page.getByRole('dialog');
  const form = modal.locator('form');
  const inputName = form.getByLabel('Domain name');
  const inputSupportEmail = form.getByLabel('Support email address');
  const buttonSubmit = modal.getByRole('button', { name: 'Add the domain' });
  const buttonCancel = modal.getByRole('button', { name: 'Cancel' });

  return {
    modal,
    form,
    inputName,
    inputSupportEmail,
    buttonSubmit,
    buttonCancel,
  };
};

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Add Mail Domains', () => {
  test('checks all the elements are visible', async ({ page }) => {
    await page.goto('/mail-domains/');

    await page.getByRole('button', { name: 'Add a mail domain' }).click();

    const { modal, inputName, inputSupportEmail, buttonSubmit, buttonCancel } =
      getElements(page);

    await expect(modal).toBeVisible();
    await expect(inputName).toBeVisible();
    await expect(inputSupportEmail).toBeVisible();
    await expect(buttonSubmit).toBeVisible();
    await expect(buttonCancel).toBeVisible();
  });

  test('checks the cancel button interaction', async ({ page }) => {
    await page.goto('/mail-domains/');
    await page.getByRole('button', { name: 'Add a mail domain' }).click();

    const { modal, buttonCancel } = getElements(page);

    await buttonCancel.click();
    await expect(modal).toBeHidden();
  });

  test('checks form invalid status', async ({ page }) => {
    await page.goto('/mail-domains/');
    await page.getByRole('button', { name: 'Add a mail domain' }).click();

    const { inputName, buttonSubmit } = getElements(page);

    await expect(buttonSubmit).toBeDisabled();

    await inputName.fill('s');
    await inputName.clear();
    await expect(page.getByText('Example: saint-laurent.fr')).toBeVisible();
  });

  test('checks the routing on new mail domain added', async ({
    page,
    browserName,
  }) => {
    const mailDomainName = randomName('versailles.fr', browserName, 1)[0];
    const mailDomainSupportMail = 'support@'.concat(mailDomainName);

    await page.goto('/mail-domains/');
    await page.getByRole('button', { name: 'Add a mail domain' }).click();

    const { inputName, inputSupportEmail, buttonSubmit, modal } =
      getElements(page);

    await inputName.fill(mailDomainName);
    await inputSupportEmail.fill(mailDomainSupportMail);
    await buttonSubmit.click();

    await expect(modal).toBeHidden(); // La modale doit disparaître après validation
    await expect(page.getByText(mailDomainName)).toBeVisible(); // Vérifie que le nouveau domaine est bien ajouté
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
