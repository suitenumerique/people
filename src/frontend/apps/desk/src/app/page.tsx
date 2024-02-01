'use client';

import { Button, Field, Input } from '@openfun/cunningham-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

import { Box } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import { Panel, useCreateTeam } from '@/features';

const StyledButton = styled(Button)`
  width: fit-content;
`;

export default function Home() {
  const { t } = useTranslation();
  const { mutate: createTeam } = useCreateTeam();
  const [teamName, setTeamName] = useState('');
  const { colorsTokens } = useCunninghamTheme();

  return (
    <Box $height="inherit" $direction="row">
      <Panel />
      <Box
        $background={colorsTokens()['primary-bg']}
        $justify="center"
        $align="center"
        $width="100%"
        $gap="5rem"
      >
        <StyledButton>{t('Create a new team')}</StyledButton>
        <Field>
          <Input
            type="text"
            label={t('Team name')}
            onChange={(e) => setTeamName(e.target.value)}
          />
          <Button
            fullWidth
            onClick={() => createTeam(teamName)}
            className="mt-s"
          >
            {t('Create a team')}
          </Button>
        </Field>
      </Box>
    </Box>
  );
}
