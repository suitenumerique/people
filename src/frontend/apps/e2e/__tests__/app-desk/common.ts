import { Page, expect } from '@playwright/test';

export const keyCloakSignIn = async (page: Page, browserName: string) => {
  const title = await page.locator('h1').first().textContent({
    timeout: 5000,
  });

  if (title?.includes('Sign in to your account')) {
    await page
      .getByRole('textbox', { name: 'username' })
      .fill(`user-e2e-${browserName}`);

    await page
      .getByRole('textbox', { name: 'password' })
      .fill(`password-e2e-${browserName}`);

    await page.click('input[type="submit"]', { force: true });
  }
};

export const randomName = (name: string, browserName: string, length: number) =>
  Array.from({ length }, (_el, index) => {
    return `${browserName}-${Math.floor(Math.random() * 10000)}-${index}-${name}`;
  });

export const createTeam = async (
  page: Page,
  teamName: string,
  browserName: string,
  length: number,
) => {
  const panel = page.getByLabel('Teams panel').first();
  const buttonCreate = page.getByRole('button', { name: 'Create the team' });

  const randomTeams = randomName(teamName, browserName, length);

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
