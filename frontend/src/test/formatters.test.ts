import {
  formatDate,
  formatNumber,
  formatPercent,
  formatScore,
} from "@/utils/formatters";
import { describe, expect, it } from "vitest";

describe("formatters", () => {
  it("formatNumber returns string with decimals", () => {
    expect(formatNumber(1234)).toBe("1234.00");
    expect(formatNumber(1.5, 1)).toBe("1.5");
  });

  it("formatPercent adds % sign", () => {
    const result = formatPercent(0.1234);
    expect(result).toContain("%");
  });

  it("formatScore for 0 returns 0.00", () => {
    expect(formatScore(0)).toBe("0.00");
  });

  it("formatScore multiplies by 10", () => {
    expect(formatScore(8.567)).toBe("85.67");
    expect(formatScore(1)).toBe("10.00");
  });

  it("formatDate returns a formatted date string", () => {
    const result = formatDate("2024-01-15");
    expect(result).toBeTruthy();
    expect(typeof result).toBe("string");
  });
});
