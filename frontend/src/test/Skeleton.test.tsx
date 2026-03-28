import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import Skeleton from "@/components/common/Skeleton";

describe("Skeleton", () => {
  it("renders one skeleton by default", () => {
    const { container } = render(<Skeleton />);
    const items = container.querySelectorAll(".animate-pulse");
    expect(items).toHaveLength(1);
  });

  it("renders multiple skeletons with count", () => {
    const { container } = render(<Skeleton count={3} />);
    const items = container.querySelectorAll(".animate-pulse");
    expect(items).toHaveLength(3);
  });

  it("applies custom className", () => {
    const { container } = render(<Skeleton className="h-8 w-24" />);
    const item = container.querySelector(".animate-pulse");
    expect(item).toHaveClass("h-8", "w-24");
  });
});
