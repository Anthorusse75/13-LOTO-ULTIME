import ErrorBoundary from "@/components/common/ErrorBoundary";
import { Outlet } from "react-router-dom";
import Header from "./Header";
import Sidebar from "./Sidebar";

export default function MainLayout() {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-4 pt-14 md:p-6 md:pt-6">
          <ErrorBoundary>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
}
