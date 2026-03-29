/**
 * E2E test: Login flow → Dashboard statistics consultation.
 *
 * Covers P2 checklist item:
 *   "Écrire un test E2E : parcours login → consultation statistiques"
 */
import { expect, test } from "@playwright/test";

test.describe("Login → Statistics", () => {
  const EMAIL = process.env.E2E_USER_EMAIL ?? "admin@loto-ultime.local";
  const PASSWORD = process.env.E2E_USER_PASSWORD ?? "Admin1234!";

  test("redirects unauthenticated users to login page", async ({ page }) => {
    await page.goto("/statistics");
    await expect(page).toHaveURL(/\/login/);
  });

  test("shows validation error on wrong credentials", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/email/i).fill("wrong@example.com");
    await page.getByLabel(/mot de passe|password/i).fill("wrongpassword");
    await page
      .getByRole("button", { name: /connexion|se connecter|login/i })
      .click();
    // Expect an error message to appear
    await expect(
      page.getByText(/identifiant|mot de passe|incorrect|invalide|erreur/i),
    ).toBeVisible({ timeout: 5_000 });
  });

  test("logs in successfully and shows dashboard", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/email/i).fill(EMAIL);
    await page.getByLabel(/mot de passe|password/i).fill(PASSWORD);
    await page
      .getByRole("button", { name: /connexion|se connecter|login/i })
      .click();

    // Should redirect to dashboard
    await expect(page).toHaveURL(/\/$/, { timeout: 10_000 });
    await expect(page.getByText(/dashboard|tableau de bord/i)).toBeVisible();
  });

  test("navigates to statistics and renders frequency tab", async ({
    page,
  }) => {
    // Login first
    await page.goto("/login");
    await page.getByLabel(/email/i).fill(EMAIL);
    await page.getByLabel(/mot de passe|password/i).fill(PASSWORD);
    await page
      .getByRole("button", { name: /connexion|se connecter|login/i })
      .click();
    await page.waitForURL("**/", { timeout: 10_000 });

    // Navigate to statistics
    await page.getByRole("link", { name: /statistiques/i }).click();
    await expect(page).toHaveURL(/\/statistics/);

    // Should show the frequency tab by default
    await expect(page.getByText(/fréquences/i)).toBeVisible();
    await expect(page.getByText(/écarts/i)).toBeVisible();
  });

  test("period selector appears on frequencies tab", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/email/i).fill(EMAIL);
    await page.getByLabel(/mot de passe|password/i).fill(PASSWORD);
    await page
      .getByRole("button", { name: /connexion|se connecter|login/i })
      .click();
    await page.waitForURL("**/", { timeout: 10_000 });

    await page.goto("/statistics");
    // Period selector should be visible
    await expect(page.getByText(/tous les tirages/i)).toBeVisible();
    await expect(page.getByText(/50 derniers/i)).toBeVisible();
    await expect(page.getByText(/100 derniers/i)).toBeVisible();
  });
});
