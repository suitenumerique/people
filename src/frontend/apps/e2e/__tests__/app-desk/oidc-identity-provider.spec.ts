import { expect, test } from '@playwright/test';

test.describe('Login to people as Identity Provider', () => {
  test('checks a user with mailbox can login via people', async ({ page }) => {
    // go to people index page, wait for the redirection to keycloak
    await page.goto('/');
    await page.waitForURL('http://localhost:8083/**');

    // keycloak - click on the login button
    await page.click('a[id=social-oidc-people-local]');

    // wait for the people login page to load and fill email/password
    await page.fill('input.c__input[type="email"]', 'user-e2e@example.com');

    await page.fill('input.c__input[type="password"]', 'password-user-e2e', {
      timeout: 10000,
    });

    await page.click('button.c__button[type="submit"]');

    // wait for URL to be localhost:3000 and the page to be loaded
    await expect(page).toHaveURL('http://localhost:3000/', { timeout: 10000 });

    // check the user is logged in
    await expect(page.getByRole('heading', { name: 'Teams' })).toBeVisible();
    await expect(page.getByText('No teams exist.')).toBeVisible();
  });
});
