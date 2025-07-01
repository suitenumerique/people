import { Select } from '@openfun/cunningham-react';
import { useTranslation } from 'react-i18next';

import { Role } from '@/features/teams/team-management';

interface ChooseRoleProps {
  currentRole: Role;
  disabled: boolean;
  defaultRole: Role;
  setRole: (role: Role) => void;
}

export const ChooseRole = ({
  defaultRole,
  disabled,
  currentRole,
  setRole,
}: ChooseRoleProps) => {
  const { t } = useTranslation();

  const options = [
    { label: t('Member'), value: Role.MEMBER, disabled: false },
    { label: t('Administrator'), value: Role.ADMIN, disabled: false },
    {
      label: t('Owner'),
      value: Role.OWNER,
      disabled: disabled || currentRole !== Role.OWNER,
    },
  ];

  return (
    <Select
      label={t('Role')}
      value={defaultRole}
      onChange={(evt) => setRole(evt.target.value as Role)}
      disabled={disabled}
      options={options}
    />
  );
};
