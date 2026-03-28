import axios, { AxiosError } from "axios";
import { toast } from "sonner";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const raw = localStorage.getItem("auth-storage");
  if (raw) {
    try {
      const parsed = JSON.parse(raw);
      const token = parsed?.state?.token;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch {
      // ignore parse errors
    }
  }
  return config;
});

function extractErrorMessage(error: AxiosError<{ detail?: string }>): string {
  if (!error.response) {
    return "Serveur inaccessible — vérifiez que le backend est lancé.";
  }
  const status = error.response.status;
  const detail = error.response.data?.detail;

  if (detail) return detail;

  switch (status) {
    case 400: return "Requête invalide.";
    case 403: return "Accès interdit.";
    case 404: return "Ressource introuvable.";
    case 409: return "Conflit — opération déjà en cours.";
    case 422: return "Données invalides.";
    case 500: return "Erreur interne du serveur.";
    default:  return `Erreur ${status}`;
  }
}

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("auth-storage");
      window.location.href = "/login";
      return Promise.reject(error);
    }

    const message = extractErrorMessage(error);
    const method = error.config?.method?.toUpperCase() ?? "";
    const path = error.config?.url ?? "";

    toast.error(message, {
      description: `${method} ${path}`,
      duration: 6000,
    });

    return Promise.reject(error);
  },
);

export default api;
