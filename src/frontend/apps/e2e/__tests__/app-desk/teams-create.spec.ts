import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Teams Create', () => {
  test('checks all the create team elements are visible', async ({ page }) => {
    const buttonCreateHomepage = page.getByRole('button', {
      name: 'Create a new team',
    });
    await buttonCreateHomepage.click();

    const modal = page.getByRole('dialog')
    await expect(modal).getByText(/Create a new team/i).toBeVisible();
    await expect(modal).toBeVisible();

    await expect(modal.getByRole('button', { name: 'Cancel' })).toBeVisible();
  });

  test('checks the cancel button interaction', async ({ page }) => {
    const buttonCreateHomepage = page.getByRole('button', {
      name: 'Create a new team',
    });
    await buttonCreateHomepage.click();

    const modal = page.getByRole('dialog');

    await modal
      .getByRole('button', {
        name: 'Cancel',
      })
      .click();

    await expect(buttonCreateHomepage).toBeVisible();
  });

  test('checks the routing on new team created', async ({
    page,
    browserName,
  }) => {
    const buttonCreateHomepage = page.getByRole('button', {
      name: 'Create a new team',
    });
    await buttonCreateHomepage.click();

    const teamName = `My routing team ${browserName}-${Math.floor(Math.random() * 1000)}`;
    await page.getByText('Team name').fill(teamName);
    await page.getByRole('button', { name: 'Create the team' }).click();

    const elTeam = page.getByRole('heading', { name: teamName });
    await expect(elTeam).toBeVisible();
  });

  test('checks 404 on teams/[id] page', async ({ page }) => {
    await page.goto('/teams/some-unknown-team');
    await page.waitForURL('/404/');
    await expect(
      page.getByText(
        'It seems that the page you are looking for does not exist or cannot be displayed correctly.',
      ),
    ).toBeVisible();
  });
});
