import { useRouter as useNavigate } from 'next/navigation';
import { useEffect } from 'react';

import { useAuthStore } from '@/core/auth';
import { NextPageWithLayout } from '@/types/next';

const Page: NextPageWithLayout = () => {
  const { userData } = useAuthStore();
  const router = useNavigate();

  useEffect(() => {
    if (!userData) {
      router.push('/authenticate/');
      return;
    }

    // The user can see mailboxes
    if (userData.abilities?.mailboxes?.can_view) {
      router.push('/mail-domains/');
      return;
    }

    // Fallback to the default route according to global config
    router.push('/mail-domains/');
  }, [userData, router]);

  return null;
};

export default Page;
