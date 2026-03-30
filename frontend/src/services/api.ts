import axios, { AxiosError } from "axios";
import { toast } from "sonner";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api/v1",
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

  // Map known backend messages to user-friendly French
  if (detail) {
    const mapped = mapDetailToFrench(detail);
    if (mapped) return mapped;
    return detail;
  }

  switch (status) {
    case 400:
      return "Requête invalide.";
    case 403:
      return "Accès interdit.";
    case 404:
      return "Ressource introuvable.";
    case 409:
      return "Conflit — opération déjà en cours.";
    case 422:
      return "Données invalides. Vérifiez les champs du formulaire.";
    case 429:
      return "Trop de requêtes. Veuillez patienter quelques instants.";
    case 500:
      return "Une erreur inattendue s'est produite. Réessayez dans quelques instants.";
    case 502:
    case 503:
    case 504:
      return "Service temporairement indisponible. Réessayez dans quelques instants.";
    default:
      return `Erreur ${status}`;
  }
}

/**
 * Map common backend detail messages to user-friendly French equivalents.
 */
function mapDetailToFrench(detail: string): string | null {
  const map: Record<string, string> = {
    "Insufficient data for computation":
      "Pas assez de tirages pour le calcul. Lancez l'import des tirages depuis l'administration.",
    "Internal server error":
      "Une erreur inattendue s'est produite. Réessayez dans quelques instants.",
    "Not authenticated": "Votre session a expiré. Veuillez vous reconnecter.",
    "Rate limit exceeded":
      "Trop de requêtes. Veuillez patienter quelques instants.",
  };

  for (const [key, value] of Object.entries(map)) {
    if (detail.toLowerCase().includes(key.toLowerCase())) return value;
  }
  return null;
}

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (err: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null) {
  for (const prom of failedQueue) {
    if (token) {
      prom.resolve(token);
    } else {
      prom.reject(error);
    }
  }
  failedQueue = [];
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<{ detail?: string }>) => {
    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !(originalRequest as unknown as Record<string, unknown>)._retry
    ) {
      // Don't retry refresh or login requests
      const url = originalRequest.url ?? "";
      if (url.includes("/auth/refresh") || url.includes("/auth/login")) {
        localStorage.removeItem("auth-storage");
        window.location.href = "/login";
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (token: string) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              resolve(api(originalRequest));
            },
            reject,
          });
        });
      }

      (originalRequest as unknown as Record<string, unknown>)._retry = true;
      isRefreshing = true;

      try {
        const raw = localStorage.getItem("auth-storage");
        const parsed = raw ? JSON.parse(raw) : null;
        const refreshToken = parsed?.state?.refreshToken;

        if (!refreshToken) {
          throw new Error("No refresh token");
        }

        const { data } = await api.post("/auth/refresh", {
          refresh_token: refreshToken,
        });

        // Update store
        const newState = {
          ...parsed,
          state: {
            ...parsed.state,
            token: data.access_token,
            refreshToken: data.refresh_token,
          },
        };
        localStorage.setItem("auth-storage", JSON.stringify(newState));

        processQueue(null, data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        localStorage.removeItem("auth-storage");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    const message = extractErrorMessage(error);
    const method = error.config?.method?.toUpperCase() ?? "";
    const path = error.config?.url ?? "";
    const status = error.response?.status;

    // Don't show toast for expected "no data yet" responses
    const isExpectedEmpty =
      (status === 404 || status === 422) &&
      method === "GET" &&
      (path.includes("/draws/latest") || path.includes("/statistics"));

    // Don't show toast for login throttle (LoginPage handles it)
    const isLoginThrottle = status === 429 && path.includes("/auth/login");

    // Don't show toast for permission errors on data-fetching requests
    const isForbiddenGet = status === 403 && method === "GET";

    if (!isExpectedEmpty && !isLoginThrottle && !isForbiddenGet) {
      toast.error(message, {
        description: `${method} ${path}`,
        duration: 6000,
      });
    }

    return Promise.reject(error);
  },
);

export default api;
