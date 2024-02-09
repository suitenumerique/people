import { Page } from '@playwright/test';

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

    await page.click('input[type="submit"]');
  }
};
