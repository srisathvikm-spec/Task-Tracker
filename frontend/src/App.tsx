import React, { useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { getIdToken } from './auth/authProvider';
import AppRoutes from './routes/AppRoutes';
import { useAuthStore } from './store/authStore';
import apiClient from './api/apiClient';
import './index.css';

/**
 * AuthInitializer checks for a signed-in MSAL account on every page load,
 * grabs the ID token, and calls /auth/me to hydrate the user object.
 */
const AuthInitializer: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { login, logout, setLoading } = useAuthStore();

  useEffect(() => {
    let cancelled = false;

    const init = async () => {
      setLoading(true);
      try {
        const token = getIdToken();
        const tokenValue = await token;
        if (!tokenValue || cancelled) {
          setLoading(false);
          return;
        }

        // Store the token so apiClient picks it up
        localStorage.setItem('auth_token', tokenValue);

        const res = await apiClient.get('/auth/me');
        const userData = res.data?.data;
        if (!cancelled && userData) {
          login(tokenValue, userData);
        }
      } catch {
        if (!cancelled) {
          localStorage.removeItem('auth_token');
          logout();
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    init();
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return <>{children}</>;
};

const App: React.FC = () => (
  <BrowserRouter>
    <AuthInitializer>
      <AppRoutes />
    </AuthInitializer>
  </BrowserRouter>
);

export default App;
