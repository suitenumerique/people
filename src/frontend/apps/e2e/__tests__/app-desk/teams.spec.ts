import { expect, test } from "@playwright/test";

import { keyCloakSignIn } from "./common";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await keyCloakSignIn(page);
});

test.describe("Teams", () => {
  test("checks all the elements are visible", async ({ page }) => {
    const panel = page.getByLabel("Teams panel").first();

    await expect(panel.getByText("Recents")).toBeVisible();

    await expect(
      panel.getByRole("button", {
        name: "Sort the teams",
      }),
    ).toBeVisible();

    await expect(
      panel.getByRole("button", {
        name: "Add a team",
      }),
    ).toBeVisible();

    await expect(
      panel.getByText(
        'Create your first team by clicking on the "Create a new team" button.',
      ),
    ).toBeVisible();
  });
});
