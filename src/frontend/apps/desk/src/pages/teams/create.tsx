import { Button, Field, Input } from '@openfun/cunningham-react';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useCreateTeam } from '@/features/teams';
import { NextPageWithLayout } from '@/types/next';

import TeamLayout from './TeamLayout';

const Page: NextPageWithLayout = () => {
  const { t } = useTranslation();
  const { mutate: createTeam } = useCreateTeam();
  const [teamName, setTeamName] = useState('');

  return (
    <Field>
      <Input
        type="text"
        label={t('Team name')}
        onChange={(e) => setTeamName(e.target.value)}
      />
      <Button fullWidth onClick={() => createTeam(teamName)} className="mt-s">
        {t('Create a team')}
      </Button>
    </Field>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <TeamLayout>{page}</TeamLayout>;
};

export default Page;
