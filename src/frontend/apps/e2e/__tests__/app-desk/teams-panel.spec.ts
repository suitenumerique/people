import { expect, test } from '@playwright/test';

import { waitForElementCount } from '../helpers';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe.configure({ mode: 'serial' });
test.describe('Teams Panel', () => {
  test('001 - checks all the elements are visible', async ({ page }) => {
    const panel = page.getByLabel('Teams panel').first();

    await expect(panel.getByText('Recents')).toBeVisible();

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

  test('002 - checks the sort button', async ({ page, browserName }) => {
    const panel = page.getByLabel('Teams panel').first();

    const buttonCreate = page.getByRole('button', { name: 'Create the team' });
    const randomTeams = Array.from({ length: 3 }, (_el, index) => {
      return `team-sort-${browserName}-${Math.floor(Math.random() * 1000)}-${index}`;
    });

    for (let i = 0; i < randomTeams.length; i++) {
      await panel.getByRole('button', { name: 'Add a team' }).click();
      await page.getByText('Team name').fill(randomTeams[i]);
      await expect(buttonCreate).toBeEnabled();
      await buttonCreate.click();
      await expect(
        panel.locator('li').nth(0).getByText(randomTeams[i]),
      ).toBeVisible();
    }

    await panel
      .getByRole('button', {
        name: 'Sort the teams',
      })
      .click();

    await expect(panel.locator('li').getByText(randomTeams[1])).toBeVisible();

    const allTeams = await panel.locator('li').allTextContents();
    const sortedTeamTexts = allTeams.filter((team) =>
      randomTeams.some((randomTeam) => team.includes(randomTeam)),
    );
    expect(sortedTeamTexts).toStrictEqual(randomTeams);
  });

  test('003 - checks the infinite scrool', async ({ page, browserName }) => {
    test.setTimeout(90000);
    const panel = page.getByLabel('Teams panel').first();

    const buttonCreate = page.getByRole('button', { name: 'Create the team' });
    const randomTeams = Array.from({ length: 40 }, (_el, index) => {
      return `team-infinite-${browserName}-${Math.floor(Math.random() * 10000)}-${index}`;
    });
    for (let i = 0; i < randomTeams.length; i++) {
      await panel.getByRole('button', { name: 'Add a team' }).click();
      await page.getByText('Team name').fill(randomTeams[i]);
      await expect(buttonCreate).toBeEnabled();
      await buttonCreate.click();
      await expect(panel.locator('li').getByText(randomTeams[i])).toBeVisible();
    }

    await expect(panel.locator('li')).toHaveCount(20);
    await panel.getByText(randomTeams[24]).click();

    await waitForElementCount(panel.locator('li'), 21, 10000);
    expect(await panel.locator('li').count()).toBeGreaterThan(20);
  });
});
