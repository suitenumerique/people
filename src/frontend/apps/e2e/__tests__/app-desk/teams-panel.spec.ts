import { expect, test } from '@playwright/test';

import { createTeam, keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Teams Panel', () => {
  test('checks all the elements are visible', async ({ page }) => {
    const panel = page.getByLabel('Teams panel').first();

    await expect(panel.getByText('Groups')).toBeVisible();

    await expect(
      panel.getByRole('button', {
        name: 'Sort the teams',
      }),
    ).toBeVisible();

    await expect(
      panel.getByRole('button', {
        name: 'Add a team',
      }),
    ).toBeVisible();
  });

  test('checks the sort button', async ({ page }) => {
    const responsePromiseSortDesc = page.waitForResponse(
      (response) =>
        response.url().includes('/teams/?ordering=-created_at') &&
        response.status() === 200,
    );

    const responsePromiseSortAsc = page.waitForResponse(
      (response) =>
        response.url().includes('/teams/?ordering=created_at') &&
        response.status() === 200,
    );

    const panel = page.getByLabel('Teams panel').first();

    await panel
      .getByRole('button', {
        name: 'Sort the teams by creation date ascendent',
      })
      .click();

    const responseSortAsc = await responsePromiseSortAsc;
    expect(responseSortAsc.ok()).toBeTruthy();

    await panel
      .getByRole('button', {
        name: 'Sort the teams by creation date descendent',
      })
      .click();

    const responseSortDesc = await responsePromiseSortDesc;
    expect(responseSortDesc.ok()).toBeTruthy();
  });

  test('checks the hover and selected state', async ({ page, browserName }) => {
    const panel = page.getByLabel('Teams panel').first();
    await createTeam(page, 'team-hover', browserName, 2);

    const selectedTeam = panel.locator('li').nth(0);
    await expect(selectedTeam).toHaveCSS(
      'background-color',
      'rgb(133, 133, 246)',
    );

    const hoverTeam = panel.locator('li').nth(1);
    await hoverTeam.hover();
    await expect(hoverTeam).toHaveCSS('background-color', 'rgb(202, 202, 251)');
  });
});
