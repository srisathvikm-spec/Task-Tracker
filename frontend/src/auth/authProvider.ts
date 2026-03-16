/**
 * MSAL authentication provider configuration.
 */

import { PublicClientApplication, Configuration } from '@azure/msal-browser';

const redirectUri = import.meta.env.VITE_AZURE_REDIRECT_URI || 'http://localhost:5173';

const msalConfig: Configuration = {
  auth: {
    clientId: import.meta.env.VITE_AZURE_CLIENT_ID || '',
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_AZURE_TENANT_ID || 'common'}`,
    redirectUri,
    navigateToLoginRequestUrl: false,
  },
  cache: {
    cacheLocation: 'localStorage',
    storeAuthStateInCookie: false,
  },
};

export const msalInstance = new PublicClientApplication(msalConfig);

export const loginRequest = {
  scopes: ['openid', 'profile', 'email'],
};

/**
 * Acquire an ID token for the currently signed-in account.
 * Returns the token string or null if no account is logged in.
 */
export async function getIdToken(): Promise<string | null> {
  const active = msalInstance.getActiveAccount() || msalInstance.getAllAccounts()[0];
  if (!active) return null;

  const result = await msalInstance.acquireTokenSilent({
    ...loginRequest,
    account: active,
  });

  return result.idToken || null;
}
