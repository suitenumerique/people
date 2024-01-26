import { expect, test } from "@playwright/test";

import { keyCloakSignIn } from "./common";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await keyCloakSignIn(page);
});

test.describe("Menu", () => {
  test("checks all the elements are visible", async ({ page }) => {
    const menu = page.locator("menu").first();

    await expect(menu.getByLabel("Search button")).toBeVisible();
    await expect(menu.getByLabel("Favoris button")).toBeVisible();
    await expect(menu.getByLabel("Recent button")).toBeVisible();
    await expect(menu.getByLabel("Contacts button")).toBeVisible();
    await expect(menu.getByLabel("Groups button")).toBeVisible();

    await menu.getByLabel("Search button").hover();
    await expect(menu.getByLabel("tooltip")).toHaveText("Search");

    await menu.getByLabel("Contacts button").hover();
    await expect(menu.getByLabel("tooltip")).toHaveText("Contacts");
  });
});
