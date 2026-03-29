import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
} from "@/types/user";
import api from "./api";

export const authService = {
  login: async (req: LoginRequest): Promise<TokenResponse> => {
    const { data } = await api.post("/auth/login", req);
    return data;
  },

  register: async (req: RegisterRequest): Promise<User> => {
    const { data } = await api.post("/auth/register", req);
    return data;
  },

  me: async (token?: string): Promise<User> => {
    const headers = token ? { Authorization: `Bearer ${token}` } : undefined;
    const { data } = await api.get("/auth/me", { headers });
    return data;
  },

  refreshTokens: async (refreshToken: string): Promise<TokenResponse> => {
    const { data } = await api.post("/auth/refresh", {
      refresh_token: refreshToken,
    });
    return data;
  },

  getUsers: async (): Promise<User[]> => {
    const { data } = await api.get("/auth/users");
    return data;
  },
};
