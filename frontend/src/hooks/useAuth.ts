/**
 * Custom hook exposing auth state and role checks.
 */

import { useAuthStore } from '../store/authStore';

export function useAuth() {
  const { user, token, isAuthenticated, isLoading, login, logout } = useAuthStore();

  const hasRole = (role: string): boolean => {
    return user?.roles?.some((r) => r.name === role) ?? false;
  };

  const isAdmin = hasRole('Admin');
  const isManager = hasRole('Manager') || isAdmin;
  const isReadOnlyUser = hasRole('Read Only User');

  return { user, token, isAuthenticated, isLoading, isAdmin, isManager, isReadOnlyUser, hasRole, login, logout };
}
