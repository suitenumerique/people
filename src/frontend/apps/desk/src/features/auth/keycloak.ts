import Keycloak, { KeycloakConfig } from 'keycloak-js';

const keycloakConfig: KeycloakConfig = {
  url: process.env.NEXT_PUBLIC_KEYCLOAK_URL,
  realm: process.env.NEXT_PUBLIC_KEYCLOAK_REALM || '',
  clientId: process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID || '',
};

export const initKeycloak = (onAuthSuccess: (_token?: string) => void) => {
  const keycloak = new Keycloak(keycloakConfig);
  keycloak
    .init({
      onLoad: 'login-required',
    })
    .then((authenticated) => {
      if (authenticated) {
        onAuthSuccess(keycloak.token);
      }
    })
    .catch(() => {
      throw new Error('Failed to initialize Keycloak.');
    });
};
