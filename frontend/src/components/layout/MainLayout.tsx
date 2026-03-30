import AiCoach from "@/components/common/AiCoach";
import ErrorBoundary from "@/components/common/ErrorBoundary";
import OnboardingTour from "@/components/common/OnboardingTour";
import { Outlet } from "react-router-dom";
import Header from "./Header";
import Sidebar from "./Sidebar";

export default function MainLayout() {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* WCAG 2.4.1 — Skip to main content */}
      <a href="#main-content" className="skip-link">
        Aller au contenu principal
      </a>

      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header />
        <main
          id="main-content"
          tabIndex={-1}
          className="flex-1 overflow-x-hidden overflow-y-auto p-4 pt-14 md:p-6 md:pt-6"
        >
          <ErrorBoundary>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>
      <AiCoach />
      <OnboardingTour />
    </div>
  );
}
