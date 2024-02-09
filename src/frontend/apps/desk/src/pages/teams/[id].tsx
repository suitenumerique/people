import { Loader } from '@openfun/cunningham-react';
import { useRouter as useNavigate } from 'next/navigation';
import { useRouter } from 'next/router';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Text } from '@/components';
import { TeamInfo, useTeam } from '@/features/teams/';
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
  const { data: team, isLoading, isError, error } = useTeam({ id });
  const navigate = useNavigate();

  if (isError) {
    if (error.status === 404) {
      navigate.replace(`/404`);
      return null;
    }

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

  if (isLoading || !team) {
    return (
      <Box $align="center" $justify="center" $height="100%">
        <Loader />
      </Box>
    );
  }

  return <TeamInfo team={team} />;
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <TeamLayout>{page}</TeamLayout>;
};

export default Page;
