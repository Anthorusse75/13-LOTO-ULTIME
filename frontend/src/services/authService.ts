import api from "./api";
import type { LoginRequest, TokenResponse, User } from "@/types/user";

export const authService = {
  login: async (req: LoginRequest): Promise<TokenResponse> => {
    const { data } = await api.post("/auth/login", req);
    return data;
  },

  me: async (): Promise<User> => {
    const { data } = await api.get("/auth/me");
    return data;
  },
};
