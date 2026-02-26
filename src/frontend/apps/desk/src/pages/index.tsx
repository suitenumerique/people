import { useRouter as useNavigate } from 'next/navigation';
import { useEffect } from 'react';

import { useAuthStore } from '@/core/auth';
import { useConfigStore } from '@/core/config';
import { NextPageWithLayout } from '@/types/next';

const Page: NextPageWithLayout = () => {
  const { config } = useConfigStore();
  const { userData } = useAuthStore();
  const router = useNavigate();

  useEffect(() => {
    if (!userData) {
      router.push('/authenticate/');
      return;
    }

    // 1. The user can see mailboxes
    if (userData.abilities?.mailboxes?.can_view) {
      router.push('/mail-domains/');
      return;
    }

    // 2. The user can see teams
    if (userData.abilities?.teams?.can_view) {
      router.push('/teams/');
      return;
    }

    // Fallback to the default route according to global config
    router.push(config?.FEATURES.TEAMS_DISPLAY ? '/mail-domains/' : '/teams/');
  }, [config?.FEATURES.TEAMS_DISPLAY, userData, router]);

  return null;
};

export default Page;
