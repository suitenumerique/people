import { expect, test } from '@playwright/test';

import { waitForElementCount } from '../helpers';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await keyCloakSignIn(page);
});

test.describe.configure({ mode: 'serial' });
test.describe('Teams', () => {
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

    await expect(
      panel.getByText(
        'Create your first team by clicking on the "Create a new team" button.',
      ),
    ).toBeVisible();
  });

  test('002 - check sort button', async ({ page, browserName }) => {
    const panel = page.getByLabel('Teams panel').first();

    await page.getByRole('button', { name: 'Add a team' }).click();

    const randomTeams = Array.from({ length: 3 }, () => {
      return `team-sort-${browserName}-${Math.floor(Math.random() * 1000)}`;
    });

    for (let i = 0; i < 3; i++) {
      await page.getByText('Team name').fill(`${randomTeams[i]}-${i}`);
      await page.getByRole('button', { name: 'Create a team' }).click();
      await expect(
        panel.locator('li').nth(0).getByText(`${randomTeams[i]}-${i}`),
      ).toBeVisible();
    }

    await panel
      .getByRole('button', {
        name: 'Sort the teams',
      })
      .click();

    for (let i = 0; i < 3; i++) {
      await expect(
        panel.locator('li').nth(i).getByText(`${randomTeams[i]}-${i}`),
      ).toBeVisible();
    }
  });

  test('003 - check the infinite scrool', async ({ page, browserName }) => {
    test.setTimeout(90000);
    const panel = page.getByLabel('Teams panel').first();

    await page.getByRole('button', { name: 'Add a team' }).click();

    const randomTeams = Array.from({ length: 40 }, () => {
      return `team-infinite-${browserName}-${Math.floor(Math.random() * 10000)}`;
    });
    for (let i = 0; i < 40; i++) {
      await page.getByText('Team name').fill(`${randomTeams[i]}-${i}`);
      await page.getByRole('button', { name: 'Create Team' }).click();
      await expect(
        panel.locator('li').getByText(`${randomTeams[i]}-${i}`),
      ).toBeVisible();
    }

    await expect(panel.locator('li')).toHaveCount(20);
    await panel.getByText(`${randomTeams[24]}-${24}`).click();

    await waitForElementCount(panel.locator('li'), 21, 10000);
    expect(await panel.locator('li').count()).toBeGreaterThan(20);
  });
});
