import type { User, UserRole } from "@/types/user";
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: User | null;
  login: (token: string, refreshToken: string, user: User) => void;
  logout: () => void;
  setTokens: (token: string, refreshToken: string) => void;
  isAuthenticated: () => boolean;
  hasRole: (role: UserRole) => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      refreshToken: null,
      user: null,
      login: (token, refreshToken, user) => set({ token, refreshToken, user }),
      logout: () => set({ token: null, refreshToken: null, user: null }),
      setTokens: (token, refreshToken) => set({ token, refreshToken }),
      isAuthenticated: () => !!get().token,
      hasRole: (role) => get().user?.role === role,
    }),
    { name: "auth-storage" },
  ),
);
