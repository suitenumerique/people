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
