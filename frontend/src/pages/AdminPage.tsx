import { Settings, Database, Clock, Users } from "lucide-react";

export default function AdminPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Administration</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-surface rounded-lg border border-border p-6 flex items-start gap-4">
          <div className="p-2 rounded-lg bg-accent-blue/20">
            <Database size={20} className="text-accent-blue" />
          </div>
          <div>
            <h2 className="font-semibold mb-1">Gestion des jeux</h2>
            <p className="text-sm text-text-secondary">
              Configurer les jeux de loterie et leurs paramètres.
            </p>
            <p className="text-xs text-text-secondary mt-2 italic">
              À venir — Phase 8
            </p>
          </div>
        </div>

        <div className="bg-surface rounded-lg border border-border p-6 flex items-start gap-4">
          <div className="p-2 rounded-lg bg-accent-green/20">
            <Clock size={20} className="text-accent-green" />
          </div>
          <div>
            <h2 className="font-semibold mb-1">Jobs & Scheduler</h2>
            <p className="text-sm text-text-secondary">
              Historique des tâches de scraping et recalcul.
            </p>
            <p className="text-xs text-text-secondary mt-2 italic">
              À venir — Phase 8
            </p>
          </div>
        </div>

        <div className="bg-surface rounded-lg border border-border p-6 flex items-start gap-4">
          <div className="p-2 rounded-lg bg-accent-purple/20">
            <Users size={20} className="text-accent-purple" />
          </div>
          <div>
            <h2 className="font-semibold mb-1">Utilisateurs</h2>
            <p className="text-sm text-text-secondary">
              Gestion des comptes et des rôles.
            </p>
            <p className="text-xs text-text-secondary mt-2 italic">
              À venir — Phase 9
            </p>
          </div>
        </div>

        <div className="bg-surface rounded-lg border border-border p-6 flex items-start gap-4">
          <div className="p-2 rounded-lg bg-accent-yellow/20">
            <Settings size={20} className="text-accent-yellow" />
          </div>
          <div>
            <h2 className="font-semibold mb-1">Paramètres</h2>
            <p className="text-sm text-text-secondary">
              Configuration du système et logs.
            </p>
            <p className="text-xs text-text-secondary mt-2 italic">
              À venir — Phase 9
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
