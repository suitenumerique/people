import { useRouter as useNavigate } from 'next/navigation';
import { useEffect } from 'react';

import { useConfigStore } from '@/core/config';
import { NextPageWithLayout } from '@/types/next';

const Page: NextPageWithLayout = () => {
  const { config } = useConfigStore();
  const router = useNavigate();

  useEffect(() => {
    config?.FEATURES.TEAMS
      ? router.push('/teams/')
      : router.push('/mail-domains/');
  }, [config?.FEATURES.TEAMS, router]);

  return null;
};

export default Page;
