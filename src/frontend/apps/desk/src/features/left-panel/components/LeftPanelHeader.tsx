import { Button } from '@openfun/cunningham-react';
import { useRouter } from 'next/navigation';
import { PropsWithChildren } from 'react';

import { Icon, SeparatedSection } from '@/components';
// import { useAuthStore } from '@/core/auth/useAuthStore';

import { useLeftPanelStore } from '../stores';

export const LeftPanelHeader = ({ children }: PropsWithChildren) => {
  const router = useRouter();
  // const auth = useAuthStore();
  const { togglePanel } = useLeftPanelStore();

  const goToHome = () => {
    router.push('/');
    togglePanel();
  };

  // const createNewDoc = () => {
  //   createDoc({ title: t('Untitled document') });
  // };

  return (
    <>
      <div>
        <SeparatedSection>
          <div>
            <Button
              onClick={goToHome}
              size="medium"
              color="tertiary-text"
              icon={<Icon $variation="800" $theme="primary" iconName="house" />}
            />
            {/*              {auth.authenticated && (
                <Button
                  onClick={searchModal.open}
                  size="medium"
                  color="tertiary-text"
                  icon={
                    <Icon $variation="800" $theme="primary" iconName="search" />
                  }
                />
              )}*/}
          </div>
          {/*            {auth.authenticated && (
              <Button onClick={createNewDoc}>{t('New doc')}</Button>
            )}*/}
        </SeparatedSection>
        {children}
      </div>
      {/*      {searchModal.isOpen && (
        <DocSearchModal {...searchModal} size={ModalSize.LARGE} />
      )}*/}
    </>
  );
};
