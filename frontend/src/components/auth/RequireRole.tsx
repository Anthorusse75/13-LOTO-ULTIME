import { useAuthStore } from "@/stores/authStore";
import type { UserRole } from "@/types/user";
import { Navigate } from "react-router-dom";

const ROLE_HIERARCHY: Record<UserRole, number> = {
  ADMIN: 3,
  UTILISATEUR: 2,
  CONSULTATION: 1,
};

interface RequireRoleProps {
  minRole: UserRole;
  children: React.ReactNode;
}

export default function RequireRole({ minRole, children }: RequireRoleProps) {
  const user = useAuthStore((s) => s.user);

  if (!user || ROLE_HIERARCHY[user.role] < ROLE_HIERARCHY[minRole]) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}
