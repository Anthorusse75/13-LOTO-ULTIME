import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User, UserRole } from "@/types/user";

interface AuthState {
  token: string | null;
  user: User | null;
  login: (token: string, user: User) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
  hasRole: (role: UserRole) => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      login: (token, user) => set({ token, user }),
      logout: () => set({ token: null, user: null }),
      isAuthenticated: () => !!get().token,
      hasRole: (role) => get().user?.role === role,
    }),
    { name: "auth-storage" }
  )
);
