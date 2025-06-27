import { expect, test } from '@playwright/test';

import { addNewMember, createTeam, keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName, 'team-member');
});

test.describe('Members Delete', () => {
  test('it cannot delete himself when it is the last owner', async ({
    page,
    browserName,
  }) => {
    await createTeam(page, 'member-delete-1', browserName, 1);

    const table = page.getByRole('table');

    const cells = table.getByRole('row').nth(1).getByRole('cell');
    await expect(cells.nth(0)).toContainText('E2E Group Member');
    await cells.nth(2).getByLabel('Member options').click();
    await page.getByLabel('Open the modal to delete this member').click();

    await expect(
      page.getByText(
        'You are the last owner, you cannot be removed from your team.',
      ),
    ).toBeVisible();
    await expect(
      page.getByRole('button', { name: 'Remove from the group' }),
    ).toBeDisabled();
  });

  test('it deletes himself when it is not the last owner', async ({
    page,
    browserName,
  }) => {
    await createTeam(page, 'member-delete-2', browserName, 1);

    await addNewMember(page, 0, 'Owner');

    const table = page.getByLabel('List members card').getByRole('table');

    // find row where regexp match the name
    const cells = table
      .getByRole('row')
      .filter({ hasText: /E2E Group Member/i })
      .getByRole('cell');
    await cells.nth(2).getByLabel('Member options').click();
    await page.getByLabel('Open the modal to delete this member').click();

    await page.getByRole('button', { name: 'Remove from the group' }).click();
    await expect(
      page.getByText(`The member has been removed from the team`),
    ).toBeVisible();
    await expect(
      page.getByRole('button', { name: `Create a new team` }),
    ).toBeVisible();
  });

  test('it cannot delete owner member', async ({ page, browserName }) => {
    await createTeam(page, 'member-delete-3', browserName, 1);

    const username = await addNewMember(page, 0, 'Owner');

    const table = page.getByLabel('List members card').getByRole('table');

    // find row where regexp match the name
    const cells = table
      .getByRole('row')
      .filter({ hasText: username })
      .getByRole('cell');
    await cells.nth(2).getByLabel('Member options').click();
    await page.getByLabel('Open the modal to delete this member').click();

    await expect(
      page.getByText(`You cannot remove other owner.`),
    ).toBeVisible();
    await expect(
      page.getByRole('button', { name: 'Remove from the group' }),
    ).toBeDisabled();
  });

  test('it deletes admin member', async ({ page, browserName }) => {
    await createTeam(page, 'member-delete-4', browserName, 1);

    const username = await addNewMember(page, 0, 'Administrator');

    const table = page.getByLabel('List members card').getByRole('table');

    // find row where regexp match the name
    const cells = table
      .getByRole('row')
      .filter({ hasText: username })
      .getByRole('cell');
    await cells.nth(2).getByLabel('Member options').click();
    await page.getByLabel('Open the modal to delete this member').click();

    await page.getByRole('button', { name: 'Remove from the group' }).click();
    await expect(
      page.getByText(`The member has been removed from the team`),
    ).toBeVisible();
    await expect(table.getByText(username)).toBeHidden();
  });

  test('it cannot delete owner member when admin', async ({
    page,
    browserName,
  }) => {
    await createTeam(page, 'member-delete-5', browserName, 1);

    const username = await addNewMember(page, 0, 'Owner');

    const table = page.getByLabel('List members card').getByRole('table');

    // find row where regexp match the name
    const myCells = table
      .getByRole('row')
      .filter({ hasText: 'E2E Group Member' })
      .getByRole('cell');
    await myCells.nth(2).getByLabel('Open the member options modal').click();

    // Change role to Admin
    await page.getByText('Update role').click();

    await page.getByRole('combobox', { name: /Role/i }).click();
    await page.getByRole('option', { name: /Administrator/i }).click();
    await page.getByRole('button', { name: 'Validate' }).click();

    const cells = table
      .getByRole('row')
      .filter({ hasText: username })
      .getByRole('cell');
    await expect(cells.getByLabel('Member options')).toBeHidden();
  });

  test('it deletes admin member when admin', async ({ page, browserName }) => {
    await createTeam(page, 'member-delete-6', browserName, 1);

    // To not be the only owner
    await addNewMember(page, 0, 'Owner', 'E2E');

    const table = page.getByLabel('List members card').getByRole('table');

    // find row where regexp match the name
    const myCells = table
      .getByRole('row')
      .filter({ hasText: 'E2E Group Member' })
      .getByRole('cell');
    await myCells.nth(2).getByLabel('Member options').click();

    // Change role to Admin
    await page.getByText('Update role').click();
    await page.getByRole('combobox', { name: /Role/i }).click();
    await page.getByRole('option', { name: /Administrator/i }).click();
    await page.getByRole('button', { name: 'Validate' }).click();

    const username = await addNewMember(page, 0, 'Administrator', 'Monique');
    const cells = table
      .getByRole('row')
      .filter({ hasText: username })
      .getByRole('cell');
    await cells.nth(2).getByLabel('Member options').click();
    await page.getByLabel('Open the modal to delete this member').click();

    await page.getByRole('button', { name: 'Remove from the group' }).click();
    await expect(
      page.getByText(`The member has been removed from the team`),
    ).toBeVisible();
    await expect(table.getByText(username)).toBeHidden();
  });
});
