import ErrorMessage from "@/components/common/ErrorMessage";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

describe("ErrorMessage", () => {
  it("renders default message", () => {
    render(<ErrorMessage />);
    expect(screen.getByText("Une erreur est survenue.")).toBeInTheDocument();
  });

  it("renders custom message", () => {
    render(<ErrorMessage message="Erreur personnalisée" />);
    expect(screen.getByText("Erreur personnalisée")).toBeInTheDocument();
  });

  it("shows help text", () => {
    render(<ErrorMessage />);
    expect(screen.getByText(/Que faire/)).toBeInTheDocument();
  });

  it("shows retry button when onRetry provided", () => {
    const onRetry = vi.fn();
    render(<ErrorMessage onRetry={onRetry} />);
    const btn = screen.getByText("Réessayer");
    expect(btn).toBeInTheDocument();
    fireEvent.click(btn);
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it("hides retry button when no onRetry", () => {
    render(<ErrorMessage />);
    expect(screen.queryByText("Réessayer")).not.toBeInTheDocument();
  });
});
