/* eslint-disable @typescript-eslint/no-unused-vars */
declare module '*.svg' {
  const content: string;
  export default content;
}

namespace NodeJS {
  interface ProcessEnv {
    NEXT_PUBLIC_API_URL?: string;
    NEXT_PUBLIC_KEYCLOAK_URL?: string;
    NEXT_PUBLIC_KEYCLOAK_REALM?: string;
    NEXT_PUBLIC_KEYCLOAK_CLIENT_ID?: string;
    NEXT_PUBLIC_KEYCLOAK_LOGIN?: string;
  }
}
