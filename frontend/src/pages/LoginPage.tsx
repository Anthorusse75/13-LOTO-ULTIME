import { authService } from "@/services/authService";
import { useAuthStore } from "@/stores/authStore";
import { isAxiosError } from "axios";
import { Loader2, Lock } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [debugInfo, setDebugInfo] = useState("");
  const login = useAuthStore((s) => s.login);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setDebugInfo("");
    setLoading(true);
    try {
      setDebugInfo("Étape 1/2 : envoi du login...");
      const tokenRes = await authService.login({ username, password });
      setDebugInfo("Étape 2/2 : récupération du profil...");
      const user = await authService.me(tokenRes.access_token);
      login(tokenRes.access_token, user);
      navigate("/");
    } catch (err) {
      if (isAxiosError(err)) {
        const code = err.code ?? "?";
        const status = err.response?.status;
        const detail = err.response?.data?.detail ?? "";
        if (!err.response) {
          setError("Serveur inaccessible — vérifiez que le backend est lancé.");
          setDebugInfo(`code=${code} message=${err.message}`);
        } else if (status === 401 || status === 403) {
          setError("Identifiants incorrects.");
          setDebugInfo(`HTTP ${status} ${detail}`);
        } else if (status === 429) {
          setError("Trop de tentatives. Veuillez patienter quelques instants.");
          setDebugInfo(`HTTP ${status}`);
        } else {
          setError(`Erreur ${status} — réessayez.`);
          setDebugInfo(`HTTP ${status} ${detail} code=${code}`);
        }
      } else {
        setError("Une erreur inattendue s'est produite.");
        setDebugInfo(String(err));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="bg-surface rounded-lg border border-border p-8">
          <div className="flex flex-col items-center mb-6">
            <div className="w-12 h-12 rounded-full bg-accent-blue/20 flex items-center justify-center mb-3">
              <Lock size={24} className="text-accent-blue" />
            </div>
            <h1 className="text-xl font-bold">LOTO ULTIME</h1>
            <p className="text-sm text-text-secondary">Connexion</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="login-username"
                className="text-xs text-text-secondary block mb-1"
              >
                Utilisateur ou email
              </label>
              <input
                id="login-username"
                type="email"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoComplete="username"
                autoCapitalize="none"
                autoCorrect="off"
                spellCheck={false}
                inputMode="email"
                className="w-full bg-surface-hover border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-accent-blue"
              />
            </div>
            <div>
              <label
                htmlFor="login-password"
                className="text-xs text-text-secondary block mb-1"
              >
                Mot de passe
              </label>
              <input
                id="login-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                className="w-full bg-surface-hover border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-accent-blue"
              />
            </div>

            {error && (
              <div
                role="alert"
                className="text-xs text-accent-red text-center space-y-1"
              >
                <p>{error}</p>
                {debugInfo && (
                  <p className="text-text-secondary font-mono break-all">
                    {debugInfo}
                  </p>
                )}
              </div>
            )}
            {loading && debugInfo && (
              <p className="text-xs text-text-secondary text-center font-mono">
                {debugInfo}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 bg-accent-blue text-white rounded-md text-sm font-medium hover:bg-accent-blue/90 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading && (
                <Loader2
                  size={16}
                  className="animate-spin"
                  aria-hidden="true"
                />
              )}
              Se connecter
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
