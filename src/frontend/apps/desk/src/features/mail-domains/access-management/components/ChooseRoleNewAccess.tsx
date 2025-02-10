import { Radio, RadioGroup } from '@openfun/cunningham-react';
import { useTranslation } from 'react-i18next';
import { useState } from 'react';

import { Role } from '@/features/teams/team-management';

interface ChooseRoleNewAccessProps {
  defaultRole: Role;
  disabled: boolean;
  currentRole: Role;
  setRole: (role: Role) => void;
}

export const ChooseRoleNewAccess = ({ defaultRole, disabled, currentRole, setRole }: ChooseRoleProps) => {
  const { t } = useTranslation();
  const [role, setLocalRole] = useState<Role>(defaultRole);

  const handleChange = (evt: React.ChangeEvent<HTMLInputElement>) => {
    const newRole = evt.target.value as Role;
    setLocalRole(newRole);
    setRole(newRole);
  };

  return (
    <RadioGroup value={role} onChange={handleChange}>
      {Object.values(Role).map((roleValue) => (
        <Radio
          key={roleValue}
          label={t(roleValue)}
          value={roleValue}
          name="role"
          disabled={disabled || (roleValue === Role.OWNER && currentRole !== Role.OWNER)}
        />
      ))}
    </RadioGroup>
  );
};
