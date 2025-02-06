import { Button, ModalSize, useModal } from '@openfun/cunningham-react';
import { t } from 'i18next';
import { useRouter } from 'next/navigation';
import { PropsWithChildren } from 'react';

import { Box, Icon, SeparatedSection } from '@/components';
import { useAuthStore } from '@/core/auth/useAuthStore';
import { useLeftPanelStore } from '../stores';

export const LeftPanelHeader = ({ children }: PropsWithChildren) => {
  const router = useRouter();
  const searchModal = useModal();
  const auth = useAuthStore();
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
      <Box $width="100%">
        <SeparatedSection>
          <Box
            $padding={{ horizontal: 'sm' }}
            $width="100%"
            $direction="row"
            $justify="space-between"
            $align="center"
          >
            <Box $direction="row" $gap="2px">
              <Button
                onClick={goToHome}
                size="medium"
                color="tertiary-text"
                icon={
                  <Icon $variation="800" $theme="primary" iconName="house" />
                }
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
            </Box>
{/*            {auth.authenticated && (
              <Button onClick={createNewDoc}>{t('New doc')}</Button>
            )}*/}
          </Box>
        </SeparatedSection>
        {children}
      </Box>
{/*      {searchModal.isOpen && (
        <DocSearchModal {...searchModal} size={ModalSize.LARGE} />
      )}*/}
    </>
  );
};