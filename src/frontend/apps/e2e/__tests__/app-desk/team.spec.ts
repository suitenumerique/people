import { expect, test } from '@playwright/test';

import { createTeam, keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Team', () => {
  test('checks all the top box elements are visible', async ({
    page,
    browserName,
  }) => {
    const teamName = (
      await createTeam(page, 'team-top-box', browserName, 1)
    ).shift();

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

    const today = new Date(Date.now());
    const todayFormated = today.toLocaleDateString('en', {
      month: '2-digit',
      day: '2-digit',
      year: 'numeric',
    });
    await expect(page.getByText(`Created at ${todayFormated}`)).toBeVisible();
    await expect(
      page.getByText(`Last update at ${todayFormated}`),
    ).toBeVisible();
  });

  test('checks the datagrid members', async ({ page, browserName }) => {
    await createTeam(page, 'team-admin', browserName, 1);

    const table = page.getByLabel('List members card').getByRole('table');

    const thead = table.locator('thead');
    await expect(thead.getByText(/Names/i)).toBeVisible();
    await expect(thead.getByText(/Emails/i)).toBeVisible();
    await expect(thead.getByText(/Roles/i)).toBeVisible();

    const rows = table.getByRole('row');
    expect(await rows.count()).toBe(21);

    await expect(
      rows.nth(1).getByRole('cell').nth(0).getByLabel('Member icon'),
    ).toBeVisible();

    const textCellName = await rows
      .nth(1)
      .getByRole('cell')
      .nth(1)
      .textContent();
    expect(textCellName).toEqual(expect.any(String));
    await expect(rows.nth(1).getByRole('cell').nth(2)).toContainText('@');
    expect(
      ['owner', 'member', 'admin'].includes(
        (await rows.nth(1).getByRole('cell').nth(3).textContent()) as string,
      ),
    ).toBeTruthy();
  });
});
