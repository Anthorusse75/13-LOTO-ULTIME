import { Link } from "react-router-dom";
import { Home } from "lucide-react";

export default function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <p className="text-6xl font-bold font-mono text-accent-blue mb-2">404</p>
      <h1 className="text-xl font-semibold mb-2">Page introuvable</h1>
      <p className="text-sm text-text-secondary mb-6">
        La page que vous cherchez n'existe pas ou a été déplacée.
      </p>
      <Link
        to="/"
        className="inline-flex items-center gap-2 px-4 py-2 bg-accent-blue text-white rounded-md text-sm hover:bg-accent-blue/90"
      >
        <Home size={16} />
        Retour à l'accueil
      </Link>
    </div>
  );
}
