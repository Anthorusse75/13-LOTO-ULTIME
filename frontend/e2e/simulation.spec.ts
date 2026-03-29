/**
 * E2E test: Simulation → Results.
 *
 * Covers P2 checklist item:
 *   "Écrire un test E2E : parcours simulation → résultats"
 */
import { authTest, expect } from "./fixtures";

authTest.describe("Simulation flow", () => {
  authTest("navigates to simulation page", async ({ loggedInPage: page }) => {
    await page.getByRole("link", { name: /simulation/i }).click();
    await expect(page).toHaveURL(/\/simulation/);
    await expect(page.getByText(/monte carlo/i)).toBeVisible();
    await expect(page.getByText(/stabilité/i)).toBeVisible();
    await expect(page.getByText(/comparaison/i)).toBeVisible();
  });

  authTest(
    "shows validation error for wrong number count",
    async ({ loggedInPage: page }) => {
      await page.goto("/simulation");

      const numbersInput = page.getByPlaceholder(/ex: 3, 12/i);
      await numbersInput.fill("1, 2, 3"); // Too few numbers
      await expect(page.getByText(/exactement|numéros entre/i)).toBeVisible();
    },
  );

  authTest(
    "runs Monte Carlo simulation and renders chart",
    async ({ loggedInPage: page }) => {
      await page.goto("/simulation");

      // EuroMillions requires 5 main numbers
      const numbersInput = page.getByPlaceholder(/ex: 3, 12/i);
      await numbersInput.fill("3, 12, 25, 34, 49");

      // Set simulations to low value for speed
      const simInput = page.getByLabel(/nombre de simulations/i);
      await simInput.fill("1000");

      // Click Monte Carlo
      await page.getByRole("button", { name: /lancer monte carlo/i }).click();

      // Wait for results
      await expect(page.getByText(/simulations|distribution/i)).toBeVisible({
        timeout: 60_000,
      });
    },
  );

  authTest(
    "strategy comparison section shows two selectors",
    async ({ loggedInPage: page }) => {
      await page.goto("/simulation");
      await page.getByRole("button", { name: /comparaison/i }).click();

      await expect(page.getByText(/stratégie a/i)).toBeVisible();
      await expect(page.getByText(/stratégie b/i)).toBeVisible();
      await expect(page.getByText(/comparer deux stratégies/i)).toBeVisible();
    },
  );

  authTest("runs strategy comparison", async ({ loggedInPage: page }) => {
    await page.goto("/simulation");
    await page.getByRole("button", { name: /comparaison/i }).click();

    // Launch comparison with default strategies
    await page.getByRole("button", { name: /lancer la comparaison/i }).click();

    // Wait for results from both strategies
    await expect(page.getByText(/moy\.|max\./i)).toBeVisible({
      timeout: 60_000,
    });
  });
});
