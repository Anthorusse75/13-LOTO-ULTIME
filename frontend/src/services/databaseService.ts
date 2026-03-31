import api from "./api";

export interface ConnectionMode {
  label: string;
  host: string;
  port: number;
  url: string;
  network?: string;
}

export interface DatabaseInfo {
  engine: "sqlite" | "postgresql";
  driver: string;
  host: string | null;
  port: number | null;
  database: string;
  user: string | null;
  password: string | null;
  connections: {
    internal: ConnectionMode;
    docker_network: ConnectionMode;
    external: ConnectionMode;
  } | null;
  version: string;
  stats: {
    draws: number;
    games: number;
    users: number;
  };
}

export interface SwitchResult {
  engine: string;
  status: string;
  draws_found: number;
  fetch_triggered: boolean;
}

export const databaseService = {
  getInfo: async (): Promise<DatabaseInfo> => {
    const { data } = await api.get("/admin/database");
    return data;
  },

  switchEngine: async (engine: "sqlite" | "postgresql"): Promise<SwitchResult> => {
    const { data } = await api.post("/admin/database/switch", { engine });
    return data;
  },
};
