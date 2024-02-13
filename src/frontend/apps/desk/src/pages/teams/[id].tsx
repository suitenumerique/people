import { Loader } from '@openfun/cunningham-react';
import { useRouter } from 'next/router';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Text } from '@/components';
import { useTeam } from '@/features/teams/api/useTeam';
import { NextPageWithLayout } from '@/types/next';

import TeamLayout from './TeamLayout';

const Page: NextPageWithLayout = () => {
  const {
    query: { id },
  } = useRouter();

  if (typeof id !== 'string') {
    throw new Error('Invalid team id');
  }

  return <Team id={id} />;
};

interface TeamProps {
  id: string;
}

const Team = ({ id }: TeamProps) => {
  const { t } = useTranslation();
  const { data: team, isLoading, isError } = useTeam({ id });

  if (isError) {
    return (
      <Text
        $align="center"
        $justify="center"
        $height="100%"
        $theme="danger"
        $textAlign="center"
      >
        {t('Something bad happens, please retry.')}
      </Text>
    );
  }

  if (isLoading) {
    return (
      <Box $align="center" $justify="center" $height="100%">
        <Loader />
      </Box>
    );
  }

  return (
    <Text as="h3" $textAlign="center">
      Teams: {team?.name}
    </Text>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <TeamLayout>{page}</TeamLayout>;
};

export default Page;
