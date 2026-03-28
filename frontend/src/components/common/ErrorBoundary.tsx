import { Component, type ReactNode } from "react";
import { AlertTriangle } from "lucide-react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center py-12 gap-4">
          <AlertTriangle size={48} className="text-accent-red" />
          <h2 className="text-lg font-semibold">Une erreur est survenue</h2>
          <p className="text-sm text-text-secondary max-w-md text-center">
            {this.state.error?.message}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="px-4 py-2 bg-accent-blue text-white rounded-md text-sm hover:bg-accent-blue/90"
          >
            Réessayer
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
