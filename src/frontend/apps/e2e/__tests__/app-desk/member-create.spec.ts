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
    await expect(page.getByRole('button', { name: 'Validate' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Cancel' })).toBeVisible();
  });
});
