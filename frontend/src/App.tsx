import { Routes, Route } from "react-router-dom";
import RequireAuth from "@/components/auth/RequireAuth";
import RequireRole from "@/components/auth/RequireRole";
import MainLayout from "@/components/layout/MainLayout";
import DashboardPage from "@/pages/DashboardPage";
import DrawsPage from "@/pages/DrawsPage";
import StatisticsPage from "@/pages/StatisticsPage";
import GridsPage from "@/pages/GridsPage";
import PortfolioPage from "@/pages/PortfolioPage";
import SimulationPage from "@/pages/SimulationPage";
import AdminPage from "@/pages/AdminPage";
import LoginPage from "@/pages/LoginPage";
import NotFoundPage from "@/pages/NotFoundPage";

export default function App() {
  return (
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
  );
}
