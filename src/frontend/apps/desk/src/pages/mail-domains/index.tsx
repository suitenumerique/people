import { Button, Input } from '@gouvfr-lasuite/cunningham-react';
import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Icon, SeparatedSection, Text } from '@/components';
import { ModalAddMailDomain } from '@/features/mail-domains/domains/components/ModalAddMailDomain';
import { MailDomainsListView } from '@/features/mail-domains/domains/components/panel/MailDomainsListView';
import { MainLayout } from '@/layouts';
import { NextPageWithLayout } from '@/types/next';

const Page: NextPageWithLayout = () => {
  const { t } = useTranslation();
  const [isModalOpen, setIsModalOpen] = React.useState(false);
  const [searchValue, setSearchValue] = React.useState('');

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchValue(event.target.value);
  };

  const clearInput = () => {
    setSearchValue('');
  };

  const openModal = () => {
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  return (
    <Box aria-label="Mail Domains panel" className="container">
      <Box
        data-testid="regie-grid"
        $direction="column"
        className="regie__panel__container"
      >
        <Box
          $css="padding: 16px 24px;"
        >
          <Box
            $direction="row"
            $justify="space-between"
            $align="center"
          >
            <Text
              $direction="row"
              $align="center"
              $minWidth="400px"
              $gap="8px"
              as="h2"
              $css="font-weight: 700; font-size: 1.5rem; margin: 0px;"
            >
              <Icon width="24" height="24" $theme="neutral" $variation="secondary" iconName="mail" />
              {t('Domains of the organization')}
            </Text>
            <Button theme="brand"
              icon={<span className="material-icons">add</span>}
              variant="tertiary"
              data-testid="button-new-domain"
              onClick={openModal}>
                {t('Add a mail domain')}
            </Button>
          </Box>

          <Text
            as="p"
            $width="70%"
            $maxWidth="600px"
            $css="font-weight: 400; font-size: 0.85rem;"
            $theme="neutral"
            $variation="secondary"
          >
            {t('You can add an existing domain name to the organization and manage it directly from the interface. Once configured, you can set up and manage email accounts associated with the domain, including creating and managing aliases linked to that domain.')}
          </Text>
        </Box>
        <SeparatedSection />
        <Box $css="padding: 24px;">
          <Box
            className="sm:block md:flex"
            $direction="row"
            $justify="space-between"
            $align="center"
            $gap="1em"
            $css="margin-bottom: 20px;"
          >
            <Box $flex="1">
              <Input
                style={{ width: '100%' }}
                label={t('Search a mail domain')}
                icon={<span className="material-icons">search</span>}
                rightIcon={
                  searchValue && (
                    <span
                      className="material-icons"
                      onClick={clearInput}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          clearInput();
                        }
                      }}
                      role="button"
                      tabIndex={0}
                      style={{ cursor: 'pointer' }}
                    >
                      close
                    </span>
                  )
                }
                value={searchValue}
                onChange={handleInputChange}
              />
            </Box>
          </Box>

          <MailDomainsListView querySearch={searchValue} />
          {isModalOpen && <ModalAddMailDomain closeModal={closeModal} />}
        </Box>
      </Box>
    </Box>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <MainLayout backgroundColor="grey">{page}</MainLayout>;
};

export default Page;
