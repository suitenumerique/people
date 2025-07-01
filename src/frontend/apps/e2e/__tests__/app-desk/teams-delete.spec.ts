import { expect, test } from '@playwright/test';

import { addNewMember, createTeam, keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Teams Delete', () => {
  test('it deletes the team when we are owner', async ({
    page,
    browserName,
  }) => {
    const teamName = `team-update-name-1-${browserName}`;
    await createTeam(page, teamName, browserName, 1);

    // On est redirigé sur la page de la team
    await expect(page.getByRole('heading', { name: teamName })).toBeVisible();

    // Ouvre le menu d'options de la team
    await page.getByLabel('Open the team options').click();
    await page
      .getByRole('button')
      .getByText(/Delete the team/i)
      .click();

    // La modale s'ouvre, on confirme la suppression
    await page.getByRole('button', { name: 'Confirm deletion' }).click();

    // Vérifie le toast et le retour à l'accueil
    await expect(page.getByText('The team has been removed.')).toBeVisible();
    await expect(
      page.getByRole('button', { name: 'Create a new team' }),
    ).toBeVisible();
  });

  test('it cannot delete the team when we are admin', async ({
    page,
    browserName,
  }) => {
    const teamName = `team-update-name-2-${browserName}`;
    await createTeam(page, teamName, browserName, 1);

    await addNewMember(page, 0, 'Owner');

    // Change role to Administration via le select custom
    const table = page.getByLabel('List members card').getByRole('table');
    const myRow = table
      .getByRole('row')
      .filter({ hasText: new RegExp(`E2E ${browserName}`, 'i') })
      .first();
    await myRow.getByLabel('Member options').click();

    await page.getByText('Update role').click();
    const roleSelect = page.getByRole('combobox', { name: /role/i });
    await roleSelect.click();
    await page.getByRole('option', { name: 'Administrator' }).click();
    await page.getByRole('button', { name: 'Validate' }).click();

    await page.reload();

    // On reste sur la page de la team, le bouton Delete the team ne doit pas être visible
    await page.getByLabel('Open the team options').click();
    await expect(
      page
        .getByRole('button')
        .getByText(/Delete the team/i)
        .first(),
    ).toBeHidden();
  });

  test('it cannot delete the team when we are member', async ({
    page,
    browserName,
  }) => {
    const teamName = `team-update-name-3-${browserName}`;
    await createTeam(page, teamName, browserName, 1);

    await addNewMember(page, 0, 'Owner');

    // Change role à Administrator
    const table = page.getByLabel('List members card').getByRole('table');
    let myRow = table
      .getByRole('row')
      .filter({ hasText: new RegExp(`E2E ${browserName}`, 'i') })
      .first();
    await myRow.getByLabel('Member options').click();

    await page.getByText('Update role').click();
    let roleSelect = page.getByRole('combobox', { name: /role/i });
    await roleSelect.click();
    await page.getByRole('option', { name: 'Administrator' }).click();
    await page.getByRole('button', { name: 'Validate' }).click();

    await page.reload();

    // Refaire la manip pour passer à Member
    myRow = table
      .getByRole('row')
      .filter({ hasText: new RegExp(`E2E ${browserName}`, 'i') })
      .first();
    await myRow.getByLabel('Member options').click();
    await page.getByText('Update role').click();
    roleSelect = page.getByRole('combobox', { name: /role/i });
    await roleSelect.click();
    await page.getByRole('option', { name: 'Member' }).click();
    await page.getByRole('button', { name: 'Validate' }).click();

    await page.reload();

    // Le bouton d'options de la team ne doit plus être visible
    await expect(page.getByLabel('Open the team options')).toBeHidden();
  });
});
