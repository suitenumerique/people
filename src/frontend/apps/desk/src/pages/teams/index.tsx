import { Button, Input, Tooltip } from '@openfun/cunningham-react';
import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Text } from '@/components';
import { useAuthStore } from '@/core/auth';
import { useCunninghamTheme } from '@/cunningham';
import { ModalCreateTeam } from '@/features/teams/team-management/components/ModalCreateTeam';
import { TeamsListView } from '@/features/teams/team-management/components/TeamsListView';
import { MainLayout } from '@/layouts';
import { NextPageWithLayout } from '@/types/next';

const Page: NextPageWithLayout = () => {
  const { t } = useTranslation();
  const [isModalOpen, setIsModalOpen] = React.useState(false);
  const { userData } = useAuthStore();
  const can_create = userData?.abilities?.teams.can_create ?? false;
  const [searchValue, setSearchValue] = React.useState('');
  const { colorsTokens } = useCunninghamTheme();
  const colors = colorsTokens();

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
    <Box aria-label="Teams panel" className="container">
      <Box
        data-testid="regie-grid"
        $background="white"
        $radius="4px"
        $direction="column"
        $css={`
          height: 100%;
          width: 100%;
          padding: 16px;
          overflow-x: hidden;
          overflow-y: auto;
          border: 1px solid ${colorsTokens()['greyscale-200']};
        `}
      >
        <Text
          as="h2"
          $css="font-weight: 700; font-size: 1.5rem; margin-bottom: 20px;"
        >
          {t('Teams')}
        </Text>

        <Box
          className="sm:block md:flex"
          $direction="row"
          $justify="space-between"
          $align="center"
          $gap="1em"
          $css="margin-bottom: 20px;"
        >
          <Box $css="width: calc(100% - 245px);" $flex="1">
            <Input
              style={{ width: '100%' }}
              label={t('Search a team')}
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

          <Box
            className="hidden md:flex"
            $css={`
              background: ${colors['greyscale-200']};
              height: 32px;
              width: 1px;
            `}
          ></Box>

          <Box>
            {can_create ? (
              <Button data-testid="button-new-team" onClick={openModal}>
                {t('Create a new team')}
              </Button>
            ) : (
              <Tooltip content="You don't have the correct access right">
                <div>
                  <Button
                    data-testid="button-new-team"
                    onClick={openModal}
                    disabled={!can_create}
                  >
                    {t('Create a new team')}
                  </Button>
                </div>
              </Tooltip>
            )}
          </Box>
        </Box>

        {!can_create && (
          <p style={{ textAlign: 'center' }}>
            {t('Click on team to view details')}
          </p>
        )}

        <TeamsListView querySearch={searchValue} />
        {isModalOpen && <ModalCreateTeam closeModal={closeModal} />}
      </Box>
    </Box>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <MainLayout backgroundColor="grey">{page}</MainLayout>;
};

export default Page;
