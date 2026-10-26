import { CunninghamProvider } from '@gouvfr-lasuite/ui-kit';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useTranslation } from 'react-i18next';

import { useCunninghamTheme } from '@/cunningham';
import { CUNNINGHAM_LOCALES } from '@/i18n/conf';
import '@/i18n/initI18n';

import { Auth } from './auth/Auth';
import { ConfigProvider } from './config';

/**
 * QueryClient:
 *  - defaultOptions:
 *    - staleTime:
 *      - global cache duration - we decided 3 minutes
 *      - It can be overridden to each query
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 3,
    },
  },
});

export function AppProvider({ children }: { children: React.ReactNode }) {
  const { theme } = useCunninghamTheme();
  const { i18n } = useTranslation();

  return (
    <CunninghamProvider
      theme={theme}
      currentLocale={CUNNINGHAM_LOCALES[i18n.language]}
    >
      <QueryClientProvider client={queryClient}>
        <ReactQueryDevtools />
        <ConfigProvider>
          <Auth>{children}</Auth>
        </ConfigProvider>
      </QueryClientProvider>
    </CunninghamProvider>
  );
}
