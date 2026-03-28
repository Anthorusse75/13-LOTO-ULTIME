import {
  OPTIMIZATION_METHODS,
  PORTFOLIO_STRATEGIES,
  SCORE_CRITERIA,
  SCORING_PROFILES,
} from "@/utils/constants";
import { describe, expect, it } from "vitest";

describe("constants", () => {
  it("has 5 optimization methods", () => {
    expect(OPTIMIZATION_METHODS).toHaveLength(5);
    const values = OPTIMIZATION_METHODS.map((m) => m.value);
    expect(values).toContain("auto");
    expect(values).toContain("genetic");
  });

  it("has 4 scoring profiles", () => {
    expect(SCORING_PROFILES).toHaveLength(4);
    const values = SCORING_PROFILES.map((p) => p.value);
    expect(values).toContain("equilibre");
    expect(values).toContain("tendance");
  });

  it("has 4 portfolio strategies", () => {
    expect(PORTFOLIO_STRATEGIES).toHaveLength(4);
  });

  it("has 6 score criteria with tooltips", () => {
    expect(SCORE_CRITERIA).toHaveLength(6);
    for (const c of SCORE_CRITERIA) {
      expect(c.key).toBeTruthy();
      expect(c.label).toBeTruthy();
      expect(c.tooltip).toBeTruthy();
    }
  });
});
