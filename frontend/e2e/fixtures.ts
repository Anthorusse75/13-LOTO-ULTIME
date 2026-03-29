/**
 * Shared E2E fixtures and helpers.
 * Provides a pre-authenticated page for tests that require a logged-in user.
 */
import { test as base, expect, type Page } from "@playwright/test";

const E2E_EMAIL = process.env.E2E_USER_EMAIL ?? "admin@loto-ultime.local";
const E2E_PASSWORD = process.env.E2E_USER_PASSWORD ?? "Admin1234!";

/**
 * Log in via the login form and wait until redirected to the dashboard.
 */
async function loginUser(page: Page) {
  await page.goto("/login");
  await page.getByLabel(/email/i).fill(E2E_EMAIL);
  await page.getByLabel(/mot de passe|password/i).fill(E2E_PASSWORD);
  await page
    .getByRole("button", { name: /connexion|se connecter|login/i })
    .click();
  await page.waitForURL("**/", { timeout: 10_000 });
}

/** Extended test fixture that logs in before each test. */
export const authTest = base.extend<{ loggedInPage: Page }>({
  loggedInPage: async ({ page }, use) => {
    await loginUser(page);
    await use(page);
  },
});

export { expect };
