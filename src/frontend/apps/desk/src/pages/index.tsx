import { useRouter as useNavigate } from 'next/navigation';
import { useEffect } from 'react';

import { useConfigStore } from '@/core/config';
import { NextPageWithLayout } from '@/types/next';

const Page: NextPageWithLayout = () => {
  const { config } = useConfigStore();
  const router = useNavigate();

  useEffect(() => {
    router.push(config?.FEATURES.TEAMS_DISPLAY ? '/teams/' : '/mail-domains/');
  }, [config?.FEATURES.TEAMS_DISPLAY, router]);

  return null;
};

export default Page;
