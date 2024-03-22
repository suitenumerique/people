import { expect, test } from '@playwright/test';

import { createTeam, keyCloakSignIn, randomName } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Members Create', () => {
  test('it opens the modals to add a member to the team', async ({
    page,
    browserName,
  }) => {
    await createTeam(page, 'member-open-modal', browserName, 1);

    await page.getByLabel('Add members to the team').click();

    await expect(page.getByText('Add members to the team')).toBeVisible();
    await expect(
      page.getByLabel(/Find a member to add to the team/),
    ).toBeVisible();

    await expect(page.getByRole('button', { name: 'Validate' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Cancel' })).toBeVisible();
  });

  test('it selects 2 users', async ({ page, browserName }) => {
    const responsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/users/?q=test') && response.status() === 200,
    );
    await createTeam(page, 'member-modal-search-user', browserName, 1);

    await page.getByLabel('Add members to the team').click();

    await expect(page.getByRole('radio', { name: 'Owner' })).toBeHidden();

    const inputSearch = page.getByLabel(/Find a member to add to the team/);

    for (let i = 0; i < 2; i++) {
      await inputSearch.fill('test');

      const response = await responsePromise;
      const users = (await response.json()).results as {
        name: string;
      }[];

      await page.getByText(users[i].name).click();

      await expect(
        page.getByText(`${users[i].name}`, { exact: true }),
      ).toBeVisible();
      await expect(page.getByLabel(`Remove ${users[i].name}`)).toBeVisible();
    }

    await expect(page.getByText(/Choose a role/)).toBeVisible();
    await expect(page.getByRole('radio', { name: 'Member' })).toBeChecked();
    await expect(page.getByRole('radio', { name: 'Owner' })).toBeVisible();
    await expect(page.getByRole('radio', { name: 'Admin' })).toBeVisible();
  });

  test('it sends an invitation', async ({ page, browserName }) => {
    await createTeam(page, 'member-invitation', browserName, 1);

    await page.getByLabel('Add members to the team').click();

    const inputSearch = page.getByLabel(/Find a member to add to the team/);

    const email = randomName('test@test.fr', browserName, 1)[0];
    await inputSearch.fill(email);
    await page.getByRole('option', { name: email }).click();

    await expect(page.getByText(email, { exact: true })).toBeVisible();
    await expect(page.getByLabel(`Remove ${email}`)).toBeVisible();

    await page.getByRole('radio', { name: 'Owner' }).click();

    const responsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/invitations/') && response.status() === 201,
    );

    await page.getByRole('button', { name: 'Validate' }).click();
    await expect(page.getByText(`Invitation sent to ${email}`)).toBeVisible();

    const response = await responsePromise;
    expect(response.ok()).toBeTruthy();
  });
});
