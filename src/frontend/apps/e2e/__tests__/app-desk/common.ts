import { Page, expect } from '@playwright/test';

export const keyCloakSignIn = async (
  page: Page,
  browserName: string,
  accountName?: string,
) => {
  const title = await page.locator('h1').first().textContent({
    timeout: 5000,
  });

  const username = accountName
    ? `e2e.${accountName}`
    : `user-e2e-${browserName}`;
  const password = accountName
    ? `password-e2e.${accountName}`
    : `password-e2e-${browserName}`;

  // const username = "e2e.marie"
  // const password = "password-e2e.marie"

  await page.waitForURL('http://localhost:8083/**');

  if (title?.includes('Sign in to your account')) {
    await page.getByRole('textbox', { name: 'username' }).fill(username);

    await page.getByRole('textbox', { name: 'password' }).fill(password);

    await page.click('input[type="submit"]', { force: true });
  }
  await page.waitForURL('http://localhost:3000/**');
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
  const buttonCreateHomepage = page.getByRole('button', {
    name: 'Create a new team',
  });
  const buttonCreate = page.getByRole('button', { name: 'Create the team' });

  const randomTeams = randomName(teamName, browserName, length);

  for (let i = 0; i < randomTeams.length; i++) {
    if (i == 0) {
      // for the first team, we need to click on the button in the homepage
      await buttonCreateHomepage.click();
    } else {
      // for the other teams, we need to click on the button in the panel of the detail view
      await panel.getByRole('button', { name: 'Add a team' }).click();
    }
    await page.getByText('Team name').fill(randomTeams[i]);
    await expect(buttonCreate).toBeEnabled();
    await buttonCreate.click();
    await expect(panel.locator('li').getByText(randomTeams[i])).toBeVisible();
  }

  return randomTeams;
};

export const addNewMember = async (
  page: Page,
  index: number,
  role: 'Administration' | 'Owner' | 'Member',
  fillText: string = 'test',
) => {
  const responsePromiseSearchUser = page.waitForResponse(
    (response) =>
      response.url().includes(`/users/?q=${fillText}`) &&
      response.status() === 200,
  );
  await page.getByLabel('Add members to the team').click();
  const inputSearch = page.getByLabel(/Find a member to add to the team/);

  // Select a new user
  await inputSearch.fill(fillText);

  // Intercept response
  const responseSearchUser = await responsePromiseSearchUser;
  const users = (await responseSearchUser.json()).results as {
    name: string;
  }[];

  // Choose user
  await page.getByRole('option', { name: users[index].name }).click();

  // Choose a role
  await page.getByRole('radio', { name: role }).click();

  await page.getByRole('button', { name: 'Add to group' }).click();

  const table = page.getByLabel('List members card').getByRole('table');

  await expect(table.getByText(users[index].name)).toBeVisible();
  await expect(
    page.getByText(`Member ${users[index].name} added to the team`),
  ).toBeVisible();

  return users[index].name;
};
