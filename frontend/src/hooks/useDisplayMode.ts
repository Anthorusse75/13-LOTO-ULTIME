import { useSettingsStore } from "@/stores/settingsStore";

export function useDisplayMode() {
  const displayMode = useSettingsStore((s) => s.displayMode);
  const toggleDisplayMode = useSettingsStore((s) => s.toggleDisplayMode);
  const isExpert = displayMode === "expert";

  return { displayMode, isExpert, toggleDisplayMode };
}
