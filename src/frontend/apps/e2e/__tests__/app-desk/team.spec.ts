import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Team', () => {
  test('checks all the top box elements are visible', async ({
    page,
    browserName,
  }) => {
    const panel = page.getByLabel('Teams panel').first();

    await panel.getByRole('button', { name: 'Add a team' }).click();

    const teamName = `My new team ${browserName}-${Math.floor(Math.random() * 1000)}`;
    await page.getByText('Team name').fill(teamName);
    await page.getByRole('button', { name: 'Create the team' }).click();

    await expect(page.getByLabel('icon group')).toBeVisible();
    await expect(
      page.getByRole('heading', {
        name: `Members of “${teamName}“`,
        level: 3,
      }),
    ).toBeVisible();
    await expect(
      page.getByText(`Add people to the “${teamName}“ group.`),
    ).toBeVisible();

    await expect(page.getByText(`1 member`)).toBeVisible();

    await expect(page.getByText(`Created at 06/02/2024`)).toBeVisible();
    await expect(page.getByText(`Last update at 07/02/2024`)).toBeVisible();
  });
});
