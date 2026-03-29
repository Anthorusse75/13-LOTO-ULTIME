import RequireAuth from "@/components/auth/RequireAuth";
import RequireRole from "@/components/auth/RequireRole";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import MainLayout from "@/components/layout/MainLayout";
import { Suspense, lazy } from "react";
import { Route, Routes } from "react-router-dom";

const AdminPage = lazy(() => import("@/pages/AdminPage"));
const DashboardPage = lazy(() => import("@/pages/DashboardPage"));
const DrawsPage = lazy(() => import("@/pages/DrawsPage"));
const FavoritesPage = lazy(() => import("@/pages/FavoritesPage"));
const GlossaryPage = lazy(() => import("@/pages/GlossaryPage"));
const GridsPage = lazy(() => import("@/pages/GridsPage"));
const HistoryPage = lazy(() => import("@/pages/HistoryPage"));
const HowItWorksPage = lazy(() => import("@/pages/HowItWorksPage"));
const LoginPage = lazy(() => import("@/pages/LoginPage"));
const NotFoundPage = lazy(() => import("@/pages/NotFoundPage"));
const PortfolioPage = lazy(() => import("@/pages/PortfolioPage"));
const SimulationPage = lazy(() => import("@/pages/SimulationPage"));
const StatisticsPage = lazy(() => import("@/pages/StatisticsPage"));

export default function App() {
  return (
    <Suspense fallback={<LoadingSpinner message="Chargement…" />}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          element={
            <RequireAuth>
              <MainLayout />
            </RequireAuth>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="draws" element={<DrawsPage />} />
          <Route path="statistics" element={<StatisticsPage />} />
          <Route path="grids" element={<GridsPage />} />
          <Route path="portfolio" element={<PortfolioPage />} />
          <Route path="simulation" element={<SimulationPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="favorites" element={<FavoritesPage />} />
          <Route path="how-it-works" element={<HowItWorksPage />} />
          <Route path="glossary" element={<GlossaryPage />} />
          <Route
            path="admin"
            element={
              <RequireRole minRole="ADMIN">
                <AdminPage />
              </RequireRole>
            }
          />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </Suspense>
  );
}
