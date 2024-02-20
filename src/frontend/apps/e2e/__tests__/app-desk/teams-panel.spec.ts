import { Page, expect, test } from '@playwright/test';

import { waitForElementCount } from '../helpers';

import { keyCloakSignIn } from './common';

const createTeam = async (
  page: Page,
  teamName: string,
  browserName: string,
  length: number,
) => {
  const panel = page.getByLabel('Teams panel').first();
  const buttonCreate = page.getByRole('button', { name: 'Create the team' });

  const randomTeams = Array.from({ length }, (_el, index) => {
    return `${teamName}-${browserName}-${Math.floor(Math.random() * 10000)}-${index}`;
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

  return randomTeams;
};

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
    const randomTeams = await createTeam(page, 'team-sort', browserName, 3);

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

    const randomTeams = await createTeam(
      page,
      'team-infinite',
      browserName,
      40,
    );

    await expect(panel.locator('li')).toHaveCount(20);
    await panel.getByText(randomTeams[24]).click();

    await waitForElementCount(panel.locator('li'), 21, 10000);
    expect(await panel.locator('li').count()).toBeGreaterThan(20);
  });

  test('004 - checks the hover and selected state', async ({
    page,
    browserName,
  }) => {
    const panel = page.getByLabel('Teams panel').first();
    await createTeam(page, 'team-hover', browserName, 2);

    const selectedTeam = panel.locator('li').nth(0);
    await expect(selectedTeam).toHaveCSS(
      'background-color',
      'rgb(202, 202, 251)',
    );

    const hoverTeam = panel.locator('li').nth(1);
    await hoverTeam.hover();
    await expect(hoverTeam).toHaveCSS('background-color', 'rgb(227, 227, 253)');
  });
});
