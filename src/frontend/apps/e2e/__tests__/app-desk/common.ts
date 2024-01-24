import { Page } from '@playwright/test';

export const keyCloakSignIn = async (page: Page) => {
  const title = await page.locator('h1').first().textContent({
    timeout: 5000,
  });

  if (title?.includes('Sign in to your account')) {
    await page.getByRole('textbox', { name: 'username' }).fill('user-e2e');
    await page.getByRole('textbox', { name: 'password' }).fill('password-e2e');

    await page.click('input[type="submit"]');
  }
};
