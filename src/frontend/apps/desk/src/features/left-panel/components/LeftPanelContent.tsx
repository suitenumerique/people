import { useRouter } from 'next/router';

import { SeparatedSection } from '@/components';

export const LeftPanelContent = () => {
  const router = useRouter();
  const isHome = router.pathname === '/';

  return (
    <>
      {isHome && (
        <>
          <div
            style={{
              flex: '0 0 auto',
              width: '100%',
            }}
          >
            <SeparatedSection showSeparator={false}></SeparatedSection>
          </div>
          <div
            style={{
              overflowY: 'auto',
              overflowX: 'hidden',
            }}
          ></div>
        </>
      )}
    </>
  );
};
