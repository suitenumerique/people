import { expect, test } from '@playwright/test';

import { keyCloakSignIn } from './common';

test.beforeEach(async ({ page, browserName }) => {
  await page.goto('/');
  await keyCloakSignIn(page, browserName);
});

test.describe('Teams Panel', () => {
  test('checks all the elements are visible', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Teams' })).toBeVisible();

    await expect(page.getByTestId('button-new-team')).toBeVisible();
  });

  // test('checks the hover and selected state', async ({ page, browserName }) => {
  //   const panel = page.getByLabel('Teams panel').first();
  //   await createTeam(page, 'team-hover', browserName, 2);

  //   const selectedTeam = panel.locator('li').nth(0);
  //   await expect(selectedTeam).toHaveCSS(
  //     'background-color',
  //     'rgb(133, 133, 246)',
  //   );

  //   const hoverTeam = panel.locator('li').nth(1);
  //   await hoverTeam.hover();
  //   await expect(hoverTeam).toHaveCSS('background-color', 'rgb(202, 202, 251)');
  // });
});
