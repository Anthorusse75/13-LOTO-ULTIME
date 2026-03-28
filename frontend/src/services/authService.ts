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

  me: async (): Promise<User> => {
    const { data } = await api.get("/auth/me");
    return data;
  },

  getUsers: async (): Promise<User[]> => {
    const { data } = await api.get("/auth/users");
    return data;
  },
};
