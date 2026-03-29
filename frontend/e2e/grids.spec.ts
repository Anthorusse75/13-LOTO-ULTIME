/**
 * E2E test: Grid generation → Grid consultation.
 *
 * Covers P2 checklist item:
 *   "Écrire un test E2E : parcours génération de grilles → consultation"
 */
import { authTest, expect } from "./fixtures";

authTest.describe("Grids generation and consultation", () => {
  authTest("navigates to grids page", async ({ loggedInPage: page }) => {
    await page.getByRole("link", { name: /grilles/i }).click();
    await expect(page).toHaveURL(/\/grids/);
    await expect(page.getByText(/générer des grilles/i)).toBeVisible();
  });

  authTest("generates grids and shows results", async ({ loggedInPage: page }) => {
    await page.goto("/grids");

    // Set count to 5 grids
    const countInput = page.getByLabel(/nombre de grilles/i);
    await countInput.fill("5");

    // Click generate
    await page.getByRole("button", { name: /générer/i }).click();

    // Wait for results (may take a few seconds)
    await expect(
      page.getByText(/grilles générée|5 grilles/i)
    ).toBeVisible({ timeout: 60_000 });
  });

  authTest("can select a grid to see detail panel", async ({ loggedInPage: page }) => {
    await page.goto("/grids");

    const countInput = page.getByLabel(/nombre de grilles/i);
    await countInput.fill("1");
    await page.getByRole("button", { name: /générer/i }).click();

    // Wait for at least one grid row to appear
    await page.waitForSelector(".rounded-md.cursor-pointer", { timeout: 60_000 });

    // Click the first grid
    const firstGrid = page.locator(".rounded-md.cursor-pointer").first();
    await firstGrid.click();

    // Detail panel should appear
    await expect(page.getByText(/détail/i)).toBeVisible();
    await expect(page.getByText(/score/i)).toBeVisible();
  });

  authTest("top grids section is visible", async ({ loggedInPage: page }) => {
    await page.goto("/grids");
    await expect(page.getByText(/top 10|meilleures grilles/i)).toBeVisible();
  });

  authTest("favorites page loads without error", async ({ loggedInPage: page }) => {
    await page.goto("/favorites");
    await expect(page).toHaveURL(/\/favorites/);
    await expect(
      page.getByText(/mes favoris|aucune grille en favori/i)
    ).toBeVisible();
  });

  authTest("history page loads without error", async ({ loggedInPage: page }) => {
    await page.goto("/history");
    await expect(page).toHaveURL(/\/history/);
    await expect(
      page.getByText(/historique|grilles jouées|aucune grille jouée/i)
    ).toBeVisible();
  });
});
