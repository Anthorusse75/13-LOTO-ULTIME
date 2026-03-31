import { create } from "zustand";
import { persist } from "zustand/middleware";

interface SettingsState {
  theme: "dark" | "light";
  sidebarCollapsed: boolean;
  coachEnabled: boolean;
  onboardingDone: boolean;
  displayMode: "simple" | "expert";
  toggleTheme: () => void;
  toggleSidebar: () => void;
  toggleCoach: () => void;
  setOnboardingDone: (done: boolean) => void;
  toggleDisplayMode: () => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set, get) => ({
      theme: "dark",
      sidebarCollapsed: false,
      coachEnabled: true,
      onboardingDone: false,
      displayMode: "simple",
      toggleTheme: () => {
        const next = get().theme === "dark" ? "light" : "dark";
        document.documentElement.classList.toggle("dark", next === "dark");
        document.documentElement.classList.toggle("light", next === "light");
        set({ theme: next });
      },
      toggleSidebar: () => set({ sidebarCollapsed: !get().sidebarCollapsed }),
      toggleCoach: () => set({ coachEnabled: !get().coachEnabled }),
      setOnboardingDone: (done) => set({ onboardingDone: done }),
      toggleDisplayMode: () =>
        set({
          displayMode: get().displayMode === "simple" ? "expert" : "simple",
        }),
    }),
    {
      name: "settings-storage",
      onRehydrateStorage: () => (state) => {
        if (state) {
          document.documentElement.classList.toggle(
            "dark",
            state.theme === "dark",
          );
          document.documentElement.classList.toggle(
            "light",
            state.theme === "light",
          );
        }
      },
    },
  ),
);
