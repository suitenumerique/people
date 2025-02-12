import { expect, test } from '@playwright/test';

import { createTeam, keyCloakSignIn, randomName } from './common';


test.describe('Login to people as Identity Provider', () => {
  test('checks a user with mailbox can login via people', async ({
    page,
    browserName,
  }) => {
    // go to people index page, wait for the redirection to keycloak
    await page.goto('/');
    const title = await page.locator('h1').first().textContent({
        timeout: 5000,
      });

    // keycloak - click on the login button
    await page.click('a[id=social-oidc-people-local]');

    // wait for the people login page to load and fill email/password
    await page.waitForSelector('input.c__input[type="email"]', { timeout: 10000 });
    await page.fill('input.c__input[type="email"]', 'user-e2e@example.com');

    await page.waitForSelector('input.c__input[type="password"]', { timeout: 10000 });
    await page.fill('input.c__input[type="password"]', 'password-user-e2e');

    await page.click('button.c__button[type="submit"]');

    // wait for the login to be successful
    await expect(page.getByText('0 group to display.')).toBeVisible();

    })});