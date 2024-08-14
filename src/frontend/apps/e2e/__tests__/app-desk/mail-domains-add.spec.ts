import { expect, test } from '@playwright/test';

import { keyCloakSignIn, randomName } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Add Mail Domains', () => {
  test('checks all the elements are visible', async ({ page }) => {
    await page.goto('/mail-domains');

    const buttonFromHomePage = page.getByRole('button', {
      name: 'Add your mail domain',
    });

    await expect(buttonFromHomePage).toBeVisible();
    await buttonFromHomePage.click();

    await expect(buttonFromHomePage).toBeHidden();

    await expect(
      page.getByRole('heading', {
        name: 'Add your mail domain',
        level: 3,
      }),
    ).toBeVisible();

    const form = page.locator('form');

    await expect(form.getByLabel('Domain name')).toBeVisible();

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
    await page.goto('/mail-domains');

    const buttonFromHomePage = page.getByRole('button', {
      name: 'Add your mail domain',
    });
    await buttonFromHomePage.click();

    await expect(buttonFromHomePage).toBeHidden();

    await page
      .getByRole('button', {
        name: 'Cancel',
      })
      .click();

    await expect(buttonFromHomePage).toBeVisible();
  });

  test('checks form invalid status', async ({ page }) => {
    await page.goto('/mail-domains');

    const buttonFromHomePage = page.getByRole('button', {
      name: 'Add your mail domain',
    });
    await buttonFromHomePage.click();

    const form = page.locator('form');

    const inputName = form.getByLabel('Domain name');
    const buttonSubmit = page.getByRole('button', {
      name: 'Add the domain',
    });

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

    await page.goto('/mail-domains');

    const panel = page.getByLabel('Mail domains panel').first();

    await panel.getByRole('link', { name: 'Add your mail domain' }).click();

    const form = page.locator('form');

    await form.getByLabel('Domain name').fill(mailDomainName);
    await page.getByRole('button', { name: 'Add the domain' }).click();

    await expect(page).toHaveURL(`/mail-domains\/${mailDomainSlug}/`);

    await expect(
      page.getByRole('heading', {
        name: mailDomainName,
      }),
    ).toBeVisible();
  });

  test('checks error when duplicate mail domain', async ({
    page,
    browserName,
  }) => {
    await page.goto('/mail-domains');

    const panel = page.getByLabel('Mail domains panel').first();
    const additionLink = panel.getByRole('link', {
      name: 'Add your mail domain',
    });
    const form = page.locator('form');
    const inputName = form.getByLabel('Domain name');
    const submitButton = page.getByRole('button', {
      name: 'Add the domain',
    });

    const mailDomainName = randomName('duplicate.fr', browserName, 1)[0];
    const mailDomainSlug = mailDomainName.replace('.', '');

    await additionLink.click();
    await inputName.fill(mailDomainName);
    await submitButton.click();

    await expect(page).toHaveURL(`/mail-domains\/${mailDomainSlug}\/`);

    await additionLink.click();

    await inputName.fill(mailDomainName);
    await submitButton.click();

    await expect(
      page.getByText(
        'This mail domain is already used. Please, choose another one.',
      ),
    ).toBeVisible();
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
