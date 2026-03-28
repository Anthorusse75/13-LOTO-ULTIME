import { describe, expect, it, beforeEach } from "vitest";
import { useSettingsStore } from "@/stores/settingsStore";

describe("settingsStore", () => {
  beforeEach(() => {
    useSettingsStore.setState({ theme: "dark", sidebarCollapsed: false });
  });

  it("defaults to dark theme", () => {
    expect(useSettingsStore.getState().theme).toBe("dark");
  });

  it("defaults to sidebar expanded", () => {
    expect(useSettingsStore.getState().sidebarCollapsed).toBe(false);
  });

  it("toggleTheme switches dark to light", () => {
    useSettingsStore.getState().toggleTheme();
    expect(useSettingsStore.getState().theme).toBe("light");
  });

  it("toggleTheme switches light to dark", () => {
    useSettingsStore.setState({ theme: "light" });
    useSettingsStore.getState().toggleTheme();
    expect(useSettingsStore.getState().theme).toBe("dark");
  });

  it("toggleSidebar toggles collapsed state", () => {
    useSettingsStore.getState().toggleSidebar();
    expect(useSettingsStore.getState().sidebarCollapsed).toBe(true);
    useSettingsStore.getState().toggleSidebar();
    expect(useSettingsStore.getState().sidebarCollapsed).toBe(false);
  });
});
