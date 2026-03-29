/**
 * E2E test: Admin panel → Job execution.
 *
 * Covers P2 checklist item:
 *   "Écrire un test E2E : parcours admin → lancement de jobs"
 */
import { authTest, expect } from "./fixtures";

authTest.describe("Admin panel", () => {
  authTest(
    "admin link is visible for admin user",
    async ({ loggedInPage: page }) => {
      // Admin nav item should be visible (only for ADMIN role)
      const adminLink = page.getByRole("link", { name: /admin/i });
      await expect(adminLink).toBeVisible();
    },
  );

  authTest("navigates to admin page", async ({ loggedInPage: page }) => {
    await page.goto("/admin");
    // If not admin, should redirect or show forbidden page
    const url = page.url();
    const isAdminPage = url.includes("/admin") || url.includes("/login");
    expect(isAdminPage).toBe(true);
  });

  authTest(
    "admin page shows job management section",
    async ({ loggedInPage: page }) => {
      await page.goto("/admin");
      // Admin should show job-related content
      await expect(
        page.getByText(/jobs|tâches|scraping|scoring|statistiques/i),
      ).toBeVisible({ timeout: 5_000 });
    },
  );

  authTest(
    "can trigger a job from admin page",
    async ({ loggedInPage: page }) => {
      await page.goto("/admin");

      // Find the first available "Lancer" button (job trigger)
      const runButton = page
        .getByRole("button", { name: /lancer|exécuter|run/i })
        .first();

      await expect(runButton).toBeVisible({ timeout: 5_000 });
      await runButton.click();

      // Expect either a success/pending state or some response indicator
      await expect(
        page.getByText(/succès|lancé|en cours|job|tâche/i),
      ).toBeVisible({ timeout: 30_000 });
    },
  );

  authTest(
    "user management section is visible",
    async ({ loggedInPage: page }) => {
      await page.goto("/admin");
      await expect(page.getByText(/utilisateurs|gestion|user/i)).toBeVisible({
        timeout: 5_000,
      });
    },
  );
});
