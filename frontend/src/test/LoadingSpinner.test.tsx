import LoadingSpinner from "@/components/common/LoadingSpinner";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

describe("LoadingSpinner", () => {
  it("renders without message", () => {
    const { container } = render(<LoadingSpinner />);
    expect(container.querySelector(".animate-spin")).toBeInTheDocument();
  });

  it("renders with message", () => {
    render(<LoadingSpinner message="Chargement…" />);
    expect(screen.getByText("Chargement…")).toBeInTheDocument();
  });

  it("hides message when not provided", () => {
    const { container } = render(<LoadingSpinner />);
    const p = container.querySelector("p");
    expect(p).toBeNull();
  });
});
