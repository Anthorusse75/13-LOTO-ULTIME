import { create } from "zustand";
import { persist } from "zustand/middleware";

interface SettingsState {
  theme: "dark" | "light";
  sidebarCollapsed: boolean;
  coachEnabled: boolean;
  onboardingDone: boolean;
  toggleTheme: () => void;
  toggleSidebar: () => void;
  toggleCoach: () => void;
  setOnboardingDone: (done: boolean) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set, get) => ({
      theme: "dark",
      sidebarCollapsed: false,
      coachEnabled: true,
      onboardingDone: false,
      toggleTheme: () => {
        const next = get().theme === "dark" ? "light" : "dark";
        document.documentElement.classList.toggle("dark", next === "dark");
        document.documentElement.classList.toggle("light", next === "light");
        set({ theme: next });
      },
      toggleSidebar: () => set({ sidebarCollapsed: !get().sidebarCollapsed }),
      toggleCoach: () => set({ coachEnabled: !get().coachEnabled }),
      setOnboardingDone: (done) => set({ onboardingDone: done }),
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
