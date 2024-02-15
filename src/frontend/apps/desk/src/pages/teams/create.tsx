import { Button, Input, Loader } from '@openfun/cunningham-react';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';

import IconGroup from '@/assets/icons/icon-group2.svg';
import { Box, Card, StyledLink, Text } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import { useCreateTeam } from '@/features/teams';
import { NextPageWithLayout } from '@/types/next';

import TeamLayout from './TeamLayout';

const Page: NextPageWithLayout = () => {
  const { t } = useTranslation();
  const { mutate: createTeam, isError, isPending } = useCreateTeam();
  const [teamName, setTeamName] = useState('');
  const { colorsTokens } = useCunninghamTheme();

  return (
    <Box className="p-l" $justify="center" $align="start" $height="inherit">
      <Card
        className="p-b"
        $height="70%"
        $justify="space-between"
        $width="100%"
        $maxWidth="24rem"
        $minWidth="22rem"
        aria-label={t('Create new team card')}
      >
        <Box $gap="1rem">
          <Box $align="center">
            <IconGroup
              width={44}
              color={colorsTokens()['primary-text']}
              aria-label={t('icon group')}
            />
            <Text as="h3" $textAlign="center">
              {t('Name the team')}
            </Text>
          </Box>
          <Input
            fullWidth
            type="text"
            label={t('Team name')}
            onChange={(e) => setTeamName(e.target.value)}
            rightIcon={<span className="material-icons">edit</span>}
          />
          {isError && (
            <Text className="mt-s" $theme="danger" $textAlign="center">
              {t('Something bad happens, please retry.')}
            </Text>
          )}
          {isPending && (
            <Box $align="center">
              <Loader />
            </Box>
          )}
        </Box>
        <Box $justify="space-between" $direction="row" $align="center">
          <StyledLink href="/">
            <Button color="secondary">{t('Cancel')}</Button>
          </StyledLink>
          <Button onClick={() => createTeam(teamName)} disabled={!teamName}>
            {t('Create the team')}
          </Button>
        </Box>
      </Card>
    </Box>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <TeamLayout>{page}</TeamLayout>;
};

export default Page;
