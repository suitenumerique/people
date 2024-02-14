'use client';

import { Button, Field, Input } from '@openfun/cunningham-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useCreateTeam } from '@/features/teams';

export default function Page() {
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
}
