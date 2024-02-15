import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Teams', () => {
  test('checks all the create team elements are visible', async ({ page }) => {
    const buttonCreateHomepage = page.getByRole('button', {
      name: 'Create a new team',
    });
    await buttonCreateHomepage.click();
    await expect(buttonCreateHomepage).toBeHidden();

    const card = page.getByLabel('Create new team card').first();

    await expect(card.getByLabel('Team name')).toBeVisible();

    await expect(card.getByLabel('icon group')).toBeVisible();

    await expect(
      card.getByRole('heading', {
        name: 'Name the team',
        level: 3,
      }),
    ).toBeVisible();

    await expect(
      card.getByRole('button', {
        name: 'Create the team',
      }),
    ).toBeVisible();

    await expect(
      card.getByRole('button', {
        name: 'Cancel',
      }),
    ).toBeVisible();
  });

  test('checks the cancel button interaction', async ({ page }) => {
    const buttonCreateHomepage = page.getByRole('button', {
      name: 'Create a new team',
    });
    await buttonCreateHomepage.click();
    await expect(buttonCreateHomepage).toBeHidden();

    const card = page.getByLabel('Create new team card').first();

    await card
      .getByRole('button', {
        name: 'Cancel',
      })
      .click();

    await expect(buttonCreateHomepage).toBeVisible();
  });
});
