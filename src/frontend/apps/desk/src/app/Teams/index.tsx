import { Button, Field, Input, Loader } from '@openfun/cunningham-react';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useCreateTeam } from './api/useCreateTeam';
import { useTeams } from './api/useTeams';

export const Teams = () => {
  const { data, isPending } = useTeams();
  const { mutate: createTeam } = useCreateTeam();
  const [teamName, setTeamName] = useState('');
  const { t } = useTranslation();

  if (isPending) {
    return (
      <div>
        <Loader />
      </div>
    );
  }

  return (
    <>
      <Field>
        <Input
          type="text"
          label={t('Team name')}
          onChange={(e) => setTeamName(e.target.value)}
        />
        <Button fullWidth onClick={() => createTeam(teamName)} className="mt-s">
          {t('Create Team')}
        </Button>
      </Field>
      <section>
        <ul>
          {data?.results.map((post, index) => (
            <li key={post.id}>
              <div>
                <span>
                  {index + 1}. {post.name}
                </span>
              </div>
            </li>
          ))}
        </ul>
      </section>
    </>
  );
};
