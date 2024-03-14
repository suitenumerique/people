import { expect, test } from '@playwright/test';

import { createTeam, keyCloakSignIn } from './common';

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
  });

  test('it selects non existing email', async ({ page, browserName }) => {
    await createTeam(page, 'member-modal-search-user', browserName, 1);

    await page.getByLabel('Add members to the team').click();

    const inputSearch = page.getByLabel(/Find a member to add to the team/);
    await inputSearch.fill('test@test.fr');
    await page.getByRole('option', { name: 'test@test.fr' }).click();

    await expect(page.getByText('test@test.fr', { exact: true })).toBeVisible();
    await expect(page.getByLabel(`Remove test@test.fr`)).toBeVisible();
  });
});
