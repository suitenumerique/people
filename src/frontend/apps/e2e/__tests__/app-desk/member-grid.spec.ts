import { expect, test } from '@playwright/test';

import { createTeam, keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Member Grid', () => {
  test('checks the owner member is displayed correctly', async ({
    page,
    browserName,
  }) => {
    await createTeam(page, 'team-owner', browserName, 1);

    const table = page.getByRole('table');

    const thead = table.locator('thead');
    await expect(thead.getByText(/Member/i)).toBeVisible();
    await expect(thead.getByText(/Role/i)).toBeVisible();

    const cells = table.getByRole('row').nth(1).getByRole('cell');
    await expect(cells.nth(0).getByLabel('Member icon')).toBeVisible();
    await expect(cells.nth(0)).toContainText(
      new RegExp(`E2E ${browserName}`, 'i'),
    );
    await expect(cells.nth(0)).toContainText(
      `user-e2e-${browserName}@example.org`,
    );
    await expect(cells.nth(1)).toContainText(/Owner/i);
  });

  test('try to update the owner role but cannot because it is the last owner', async ({
    page,
    browserName,
  }) => {
    await createTeam(page, 'team-owner-role', browserName, 1);

    const table = page.getByRole('table');

    const cells = table.getByRole('row').nth(1).getByRole('cell');
    await expect(cells.nth(0)).toContainText(
      new RegExp(`E2E ${browserName}`, 'i'),
    );
    await cells.nth(2).getByLabel('Member options').click();
    await page.getByText('Update role').click();

    await expect(
      page.getByText(
        'You are the sole owner of this group. Make another member the group owner, before you can change your own role.',
      ),
    ).toBeVisible();

    const roleSelect = page.getByRole('combobox', { name: /Role/i });
    const cursor = await roleSelect.evaluate(
      (el) => getComputedStyle(el).cursor,
    );
    expect(cursor).toBe('not-allowed');

    await expect(
      page.getByRole('button', {
        name: 'Validate',
      }),
    ).toBeDisabled();
  });
});
