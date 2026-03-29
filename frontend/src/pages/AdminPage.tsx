import { useJobs, useSchedulerStatus, useTriggerJob } from "@/hooks/useJobs";
import { authService } from "@/services/authService";
import { gameService } from "@/services/gameService";
import type { GameDefinition } from "@/types/game";
import type { JobExecution, JobStatus } from "@/types/job";
import type { User, UserRole } from "@/types/user";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  CheckCircle2,
  Clock,
  Database,
  Loader2,
  Play,
  Plus,
  Settings,
  UserPlus,
  Users,
  XCircle,
} from "lucide-react";
import { useState } from "react";

const JOB_LABELS: Record<string, string> = {
  fetch_loto: "Scraping Loto FDJ",
  fetch_euromillions: "Scraping EuroMillions",
  fetch_keno: "Scraping Keno",
  compute_stats: "Calcul statistiques",
  compute_scoring: "Scoring grilles",
  compute_top_grids: "Top grilles",
  optimize_portfolio: "Optimisation portefeuille",
  cleanup: "Nettoyage données",
  health_check: "Health check",
};

const STATUS_CONFIG: Record<
  JobStatus,
  { color: string; bg: string; icon: typeof CheckCircle2 }
> = {
  SUCCESS: {
    color: "text-accent-green",
    bg: "bg-accent-green/20",
    icon: CheckCircle2,
  },
  FAILED: { color: "text-accent-red", bg: "bg-accent-red/20", icon: XCircle },
  RUNNING: {
    color: "text-accent-blue",
    bg: "bg-accent-blue/20",
    icon: Loader2,
  },
  PENDING: {
    color: "text-accent-yellow",
    bg: "bg-accent-yellow/20",
    icon: Clock,
  },
  CANCELLED: { color: "text-text-secondary", bg: "bg-surface", icon: XCircle },
};

function formatDuration(seconds: number | null): string {
  if (seconds === null) return "—";
  if (seconds < 1) return `${Math.round(seconds * 1000)}ms`;
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`;
}

function formatDate(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function StatusBadge({ status }: { status: JobStatus }) {
  const cfg = STATUS_CONFIG[status] ?? STATUS_CONFIG.PENDING;
  const Icon = cfg.icon;
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${cfg.bg} ${cfg.color}`}
    >
      <Icon size={12} className={status === "RUNNING" ? "animate-spin" : ""} />
      {status}
    </span>
  );
}

function JobsPanel() {
  const { data: jobs, isLoading: jobsLoading } = useJobs(30);
  const { data: status } = useSchedulerStatus();
  const triggerMutation = useTriggerJob();
  const [triggering, setTriggering] = useState<string | null>(null);

  const handleTrigger = async (jobName: string) => {
    setTriggering(jobName);
    try {
      await triggerMutation.mutateAsync(jobName);
    } catch {
      // error handled by mutation
    } finally {
      setTriggering(null);
    }
  };

  return (
    <div className="space-y-4">
      {/* Status summary */}
      <div className="flex items-center gap-3 text-sm text-text-secondary">
        <span className="flex items-center gap-1">
          <span
            className={`h-2 w-2 rounded-full ${
              status?.running_count
                ? "bg-accent-green animate-pulse"
                : "bg-text-secondary"
            }`}
          />
          {status?.running_count ?? 0} job(s) en cours
        </span>
      </div>

      {/* Trigger buttons */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {Object.entries(JOB_LABELS).map(([key, label]) => {
          // Map frontend job key to the backend job_name used in running_jobs
          const backendName = key
            .replace("fetch_loto", "fetch_draws_loto-fdj")
            .replace("fetch_euromillions", "fetch_draws_euromillions")
            .replace("fetch_keno", "fetch_draws_keno");
          const isRunning =
            triggering === key ||
            status?.running_jobs?.some((r) => r.includes(backendName));
          return (
            <button
              key={key}
              onClick={() => handleTrigger(key)}
              disabled={!!isRunning}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-surface border border-border text-sm hover:border-accent-blue/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isRunning ? (
                <Loader2 size={14} className="animate-spin text-accent-blue" />
              ) : (
                <Play size={14} className="text-accent-green" />
              )}
              <span className="truncate">{label}</span>
            </button>
          );
        })}
      </div>

      {/* History table */}
      <div className="bg-surface rounded-lg border border-border overflow-hidden">
        <div className="px-4 py-3 border-b border-border flex items-center justify-between">
          <h3 className="font-medium text-sm">Historique récent</h3>
          <span className="text-xs text-text-secondary">
            {jobs?.length ?? 0} exécutions
          </span>
        </div>

        {jobsLoading ? (
          <div className="p-6 text-center text-text-secondary">
            <Loader2 className="animate-spin mx-auto mb-2" size={20} />
            Chargement…
          </div>
        ) : !jobs?.length ? (
          <div className="p-6 text-center text-text-secondary text-sm">
            Aucune exécution enregistrée. Le pipeline nocturne s'exécute chaque
            jour à 22h (Europe/Paris).
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-text-secondary border-b border-border">
                  <th className="px-4 py-2 font-medium">Job</th>
                  <th className="px-4 py-2 font-medium">Statut</th>
                  <th className="px-4 py-2 font-medium">Démarré</th>
                  <th className="px-4 py-2 font-medium">Durée</th>
                  <th className="px-4 py-2 font-medium">Source</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((job: JobExecution) => (
                  <tr
                    key={job.id}
                    className="border-b border-border/50 hover:bg-surface-hover/50 transition-colors"
                  >
                    <td className="px-4 py-2 font-mono text-xs">
                      {job.job_name}
                    </td>
                    <td className="px-4 py-2">
                      <StatusBadge status={job.status} />
                    </td>
                    <td className="px-4 py-2 text-text-secondary">
                      {formatDate(job.started_at)}
                    </td>
                    <td className="px-4 py-2 text-text-secondary">
                      {formatDuration(job.duration_seconds)}
                    </td>
                    <td className="px-4 py-2 text-text-secondary">
                      {job.triggered_by}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

const ROLE_LABELS: Record<UserRole, string> = {
  ADMIN: "Administrateur",
  UTILISATEUR: "Utilisateur",
  CONSULTATION: "Consultation",
};

const ROLE_COLORS: Record<UserRole, string> = {
  ADMIN: "bg-accent-red/20 text-accent-red",
  UTILISATEUR: "bg-accent-blue/20 text-accent-blue",
  CONSULTATION: "bg-accent-yellow/20 text-accent-yellow",
};

function UsersPanel() {
  const queryClient = useQueryClient();
  const { data: users, isLoading } = useQuery<User[]>({
    queryKey: ["users"],
    queryFn: authService.getUsers,
  });

  const [showForm, setShowForm] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("CONSULTATION");
  const [formError, setFormError] = useState("");

  const createMutation = useMutation({
    mutationFn: authService.register,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      setShowForm(false);
      setUsername("");
      setEmail("");
      setPassword("");
      setRole("CONSULTATION");
      setFormError("");
    },
    onError: (err: unknown) => {
      const msg =
        err instanceof Error ? err.message : "Erreur lors de la création";
      setFormError(msg);
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    createMutation.mutate({ username, email, password, role });
  };

  return (
    <div className="space-y-4">
      {/* Header with create button */}
      <div className="flex items-center justify-between">
        <span className="text-sm text-text-secondary">
          {users?.length ?? 0} utilisateur(s)
        </span>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-accent-blue text-white text-sm hover:bg-accent-blue/90 transition-colors"
        >
          {showForm ? <XCircle size={14} /> : <UserPlus size={14} />}
          {showForm ? "Annuler" : "Nouvel utilisateur"}
        </button>
      </div>

      {/* Create user form */}
      {showForm && (
        <form
          onSubmit={handleCreate}
          className="bg-surface rounded-lg border border-accent-blue/30 p-4 space-y-3"
        >
          <h3 className="text-sm font-semibold flex items-center gap-2">
            <Plus size={14} /> Créer un utilisateur
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-text-secondary block mb-1">
                Nom d'utilisateur
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                minLength={3}
                maxLength={50}
                className="w-full bg-surface-hover border border-border rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-accent-blue"
              />
            </div>
            <div>
              <label className="text-xs text-text-secondary block mb-1">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-surface-hover border border-border rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-accent-blue"
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
                minLength={8}
                autoComplete="new-password"
                className="w-full bg-surface-hover border border-border rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-accent-blue"
              />
              <p className="text-xs text-text-secondary mt-0.5">
                Min. 8 car., 1 majuscule, 1 minuscule, 1 chiffre
              </p>
            </div>
            <div>
              <label className="text-xs text-text-secondary block mb-1">
                Rôle
              </label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value as UserRole)}
                className="w-full bg-surface-hover border border-border rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-accent-blue"
              >
                <option value="CONSULTATION">Consultation</option>
                <option value="UTILISATEUR">Utilisateur</option>
                <option value="ADMIN">Administrateur</option>
              </select>
            </div>
          </div>
          {formError && <p className="text-xs text-accent-red">{formError}</p>}
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="flex items-center gap-2 px-4 py-1.5 rounded-md bg-accent-green text-white text-sm hover:bg-accent-green/90 disabled:opacity-50"
          >
            {createMutation.isPending && (
              <Loader2 size={14} className="animate-spin" />
            )}
            Créer
          </button>
        </form>
      )}

      {/* User list */}
      <div className="bg-surface rounded-lg border border-border overflow-hidden">
        {isLoading ? (
          <div className="p-6 text-center text-text-secondary">
            <Loader2 className="animate-spin mx-auto mb-2" size={20} />
            Chargement…
          </div>
        ) : !users?.length ? (
          <div className="p-6 text-center text-text-secondary text-sm">
            Aucun utilisateur.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-text-secondary border-b border-border">
                  <th className="px-4 py-2 font-medium">ID</th>
                  <th className="px-4 py-2 font-medium">Utilisateur</th>
                  <th className="px-4 py-2 font-medium">Email</th>
                  <th className="px-4 py-2 font-medium">Rôle</th>
                  <th className="px-4 py-2 font-medium">Actif</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr
                    key={u.id}
                    className="border-b border-border/50 hover:bg-surface-hover/50 transition-colors"
                  >
                    <td className="px-4 py-2 font-mono text-xs text-text-secondary">
                      {u.id}
                    </td>
                    <td className="px-4 py-2 font-medium">{u.username}</td>
                    <td className="px-4 py-2 text-text-secondary">{u.email}</td>
                    <td className="px-4 py-2">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${ROLE_COLORS[u.role]}`}
                      >
                        {ROLE_LABELS[u.role]}
                      </span>
                    </td>
                    <td className="px-4 py-2">
                      {u.is_active ? (
                        <CheckCircle2 size={16} className="text-accent-green" />
                      ) : (
                        <XCircle size={16} className="text-accent-red" />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function GamesPanel() {
  const { data: games, isLoading } = useQuery<GameDefinition[]>({
    queryKey: ["games"],
    queryFn: gameService.getAll,
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-sm text-text-secondary">
          {games?.length ?? 0} jeu(x) configuré(s)
        </span>
      </div>

      <div className="bg-surface rounded-lg border border-border overflow-hidden">
        {isLoading ? (
          <div className="p-6 text-center text-text-secondary">
            <Loader2 className="animate-spin mx-auto mb-2" size={20} />
            Chargement…
          </div>
        ) : !games?.length ? (
          <div className="p-6 text-center text-text-secondary text-sm">
            Aucun jeu configuré.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-text-secondary border-b border-border">
                  <th className="px-4 py-2 font-medium">ID</th>
                  <th className="px-4 py-2 font-medium">Nom</th>
                  <th className="px-4 py-2 font-medium">Slug</th>
                  <th className="px-4 py-2 font-medium">Numéros</th>
                  <th className="px-4 py-2 font-medium">Étoiles / Chance</th>
                  <th className="px-4 py-2 font-medium">Fréquence</th>
                  <th className="px-4 py-2 font-medium">Actif</th>
                </tr>
              </thead>
              <tbody>
                {games.map((g) => (
                  <tr
                    key={g.id}
                    className="border-b border-border/50 hover:bg-surface-hover/50 transition-colors"
                  >
                    <td className="px-4 py-2 font-mono text-xs text-text-secondary">
                      {g.id}
                    </td>
                    <td className="px-4 py-2 font-medium">{g.name}</td>
                    <td className="px-4 py-2 font-mono text-xs text-text-secondary">
                      {g.slug}
                    </td>
                    <td className="px-4 py-2">
                      {g.numbers_drawn} / {g.numbers_pool}
                    </td>
                    <td className="px-4 py-2">
                      {g.stars_pool ? (
                        <span>
                          {g.stars_drawn} / {g.stars_pool}{" "}
                          <span className="text-text-secondary text-xs">
                            ({g.star_name})
                          </span>
                        </span>
                      ) : (
                        <span className="text-text-secondary">—</span>
                      )}
                    </td>
                    <td className="px-4 py-2 text-text-secondary">
                      {g.draw_frequency}
                    </td>
                    <td className="px-4 py-2">
                      {g.is_active ? (
                        <CheckCircle2 size={16} className="text-accent-green" />
                      ) : (
                        <XCircle size={16} className="text-accent-red" />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <p className="text-xs text-text-secondary">
        Les jeux sont définis via les fichiers YAML dans{" "}
        <code className="bg-surface-hover px-1 rounded">
          backend/game_configs/
        </code>
        . Ajoutez un nouveau fichier YAML et relancez le backend pour l'activer.
      </p>
    </div>
  );
}

function SettingsPanel() {
  const { data: status } = useSchedulerStatus();

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-surface rounded-lg border border-border p-4 space-y-3">
          <h3 className="text-sm font-semibold">Scheduler</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-text-secondary">Status</span>
              <span className="flex items-center gap-1">
                <span
                  className={`h-2 w-2 rounded-full ${
                    status?.running_count
                      ? "bg-accent-green animate-pulse"
                      : "bg-accent-green"
                  }`}
                />
                Actif
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Pipeline nocturne</span>
              <span>22h00 (Europe/Paris)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Jobs en cours</span>
              <span>{status?.running_count ?? 0}</span>
            </div>
          </div>
        </div>

        <div className="bg-surface rounded-lg border border-border p-4 space-y-3">
          <h3 className="text-sm font-semibold">Base de données</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-text-secondary">Type</span>
              <span>SQLite (aiosqlite)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Migrations</span>
              <span>Alembic</span>
            </div>
          </div>
        </div>

        <div className="bg-surface rounded-lg border border-border p-4 space-y-3">
          <h3 className="text-sm font-semibold">Authentification</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-text-secondary">Méthode</span>
              <span>JWT HS256</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Access token</span>
              <span>30 min</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Refresh token</span>
              <span>7 jours</span>
            </div>
          </div>
        </div>

        <div className="bg-surface rounded-lg border border-border p-4 space-y-3">
          <h3 className="text-sm font-semibold">API</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-text-secondary">Framework</span>
              <span>FastAPI</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Rate limiting</span>
              <span>slowapi</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Docs</span>
              <a
                href="/api/v1/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="text-accent-blue hover:underline"
              >
                /api/v1/docs →
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<
    "overview" | "jobs" | "users" | "games" | "settings"
  >("overview");

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Administration</h1>

      {/* Tab navigation */}
      <div className="flex gap-1 border-b border-border">
        <button
          onClick={() => setActiveTab("overview")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "overview"
              ? "border-accent-blue text-accent-blue"
              : "border-transparent text-text-secondary hover:text-text"
          }`}
        >
          Vue d'ensemble
        </button>
        <button
          onClick={() => setActiveTab("jobs")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "jobs"
              ? "border-accent-blue text-accent-blue"
              : "border-transparent text-text-secondary hover:text-text"
          }`}
        >
          Jobs & Scheduler
        </button>
        <button
          onClick={() => setActiveTab("users")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "users"
              ? "border-accent-blue text-accent-blue"
              : "border-transparent text-text-secondary hover:text-text"
          }`}
        >
          Utilisateurs
        </button>
        <button
          onClick={() => setActiveTab("games")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "games"
              ? "border-accent-blue text-accent-blue"
              : "border-transparent text-text-secondary hover:text-text"
          }`}
        >
          Jeux
        </button>
        <button
          onClick={() => setActiveTab("settings")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "settings"
              ? "border-accent-blue text-accent-blue"
              : "border-transparent text-text-secondary hover:text-text"
          }`}
        >
          Paramètres
        </button>
      </div>

      {activeTab === "overview" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => setActiveTab("games")}
            className="bg-surface rounded-lg border border-accent-blue/30 p-6 flex items-start gap-4 text-left hover:border-accent-blue/60 transition-colors"
          >
            <div className="p-2 rounded-lg bg-accent-blue/20">
              <Database size={20} className="text-accent-blue" />
            </div>
            <div>
              <h2 className="font-semibold mb-1">Gestion des jeux</h2>
              <p className="text-sm text-text-secondary">
                Configurer les jeux de loterie et leurs paramètres.
              </p>
              <p className="text-xs text-accent-blue mt-2 font-medium">
                Actif — voir le détail →
              </p>
            </div>
          </button>

          <button
            onClick={() => setActiveTab("jobs")}
            className="bg-surface rounded-lg border border-accent-green/30 p-6 flex items-start gap-4 text-left hover:border-accent-green/60 transition-colors"
          >
            <div className="p-2 rounded-lg bg-accent-green/20">
              <Clock size={20} className="text-accent-green" />
            </div>
            <div>
              <h2 className="font-semibold mb-1">Jobs & Scheduler</h2>
              <p className="text-sm text-text-secondary">
                Historique des tâches de scraping et recalcul.
              </p>
              <p className="text-xs text-accent-green mt-2 font-medium">
                Actif — voir le détail →
              </p>
            </div>
          </button>

          <button
            onClick={() => setActiveTab("users")}
            className="bg-surface rounded-lg border border-accent-purple/30 p-6 flex items-start gap-4 text-left hover:border-accent-purple/60 transition-colors"
          >
            <div className="p-2 rounded-lg bg-accent-purple/20">
              <Users size={20} className="text-accent-purple" />
            </div>
            <div>
              <h2 className="font-semibold mb-1">Utilisateurs</h2>
              <p className="text-sm text-text-secondary">
                Gestion des comptes et des rôles.
              </p>
              <p className="text-xs text-accent-purple mt-2 font-medium">
                Actif — voir le détail →
              </p>
            </div>
          </button>

          <button
            onClick={() => setActiveTab("settings")}
            className="bg-surface rounded-lg border border-accent-yellow/30 p-6 flex items-start gap-4 text-left hover:border-accent-yellow/60 transition-colors"
          >
            <div className="p-2 rounded-lg bg-accent-yellow/20">
              <Settings size={20} className="text-accent-yellow" />
            </div>
            <div>
              <h2 className="font-semibold mb-1">Paramètres</h2>
              <p className="text-sm text-text-secondary">
                Configuration du système et logs.
              </p>
              <p className="text-xs text-accent-yellow mt-2 font-medium">
                Actif — voir le détail →
              </p>
            </div>
          </button>
        </div>
      )}

      {activeTab === "jobs" && <JobsPanel />}
      {activeTab === "users" && <UsersPanel />}
      {activeTab === "games" && <GamesPanel />}
      {activeTab === "settings" && <SettingsPanel />}
    </div>
  );
}
