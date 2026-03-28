import { useState } from "react";
import { useAuthStore } from "@/stores/authStore";
import { authService } from "@/services/authService";
import { useNavigate } from "react-router-dom";
import { Loader2, Lock } from "lucide-react";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const login = useAuthStore((s) => s.login);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const tokenRes = await authService.login({ username, password });
      // Temporarily store token so the API interceptor includes it in /me request
      localStorage.setItem("auth-storage", JSON.stringify({ state: { token: tokenRes.access_token } }));
      const user = await authService.me();
      login(tokenRes.access_token, user);
      navigate("/");
    } catch {
      setError("Identifiants incorrects");
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
              <label className="text-xs text-text-secondary block mb-1">
                Utilisateur ou email
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoComplete="username"
                className="w-full bg-surface-hover border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-accent-blue"
              />
            </div>
            <div>
              <label className="text-xs text-text-secondary block mb-1">
                Mot de passe
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                className="w-full bg-surface-hover border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-accent-blue"
              />
            </div>

            {error && (
              <p className="text-xs text-accent-red text-center">{error}</p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 bg-accent-blue text-white rounded-md text-sm font-medium hover:bg-accent-blue/90 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading && <Loader2 size={16} className="animate-spin" />}
              Se connecter
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
