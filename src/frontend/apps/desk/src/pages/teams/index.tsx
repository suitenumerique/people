import { Button, Input, Tooltip } from '@gouvfr-lasuite/cunningham-react';
import { useRouter as useNavigate } from 'next/navigation';
import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Icon, SeparatedSection, Text } from '@/components';
import { useAuthStore } from '@/core/auth';
import { useCunninghamTheme } from '@/cunningham';
import { TeamsListView } from '@/features/teams/team-management/components/TeamsListView';
import { MainLayout } from '@/layouts';
import { NextPageWithLayout } from '@/types/next';

const Page: NextPageWithLayout = () => {
  const { t } = useTranslation();
  const router = useNavigate();
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

  return (
    <Box aria-label="Teams panel" className="container">
      <Box
        data-testid="regie-grid"
        $background="white"
        $radius="4px"
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
            $gap="8px"
            as="h2"
            $css="font-weight: 700; font-size: 1.5rem; margin: 0px;"
          >
            <Icon width="24" height="24" $theme="neutral" $variation="secondary" iconName="group" />
            {t('Groups')}
          </Text>

            <Box>
              {can_create ? (
                <Button
                  theme="brand"
                  icon={<span className="material-icons">add</span>}
                  variant="tertiary"
                  data-testid="button-new-team"
                  onClick={() => void router.push('/teams/create')}
                >
                  {t('New group')}
                </Button>
              ) : (
                <Tooltip content="You don't have the correct access right">
                  <div>
                    <Button
                      theme="brand"
                      icon={<span className="material-icons">add</span>}
                      variant="tertiary"
                      data-testid="button-new-team"
                      onClick={() => void router.push('/teams/create')}
                      disabled={!can_create}
                    >
                      {t('New group')}
                    </Button>
                  </div>
                </Tooltip>
              )}
            </Box>
          </Box>

          <Text
            as="p"
            $width="80%"
            $css="font-weight: 400; font-size: 0.85rem;"
            $theme="neutral"
            $variation="secondary"
          >
            {t('Create groups to bring people together. Groups can be invited to any LaSuite app just like a single person, making it easier to collaborate and share with multiple people at once.')}
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
              background-color: var(--c--contextuals--background--surface--primary);
              height: 32px;
              width: 1px;
            `}
          ></Box> 
        </Box>

        {!can_create && (
          <p style={{ textAlign: 'center' }}>
            {t('Click on team to view details')}
          </p>
        )}

        <TeamsListView querySearch={searchValue} />
      </Box>
      </Box>
    </Box>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <MainLayout backgroundColor="grey">{page}</MainLayout>;
};

export default Page;
