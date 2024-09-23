import { Radio, RadioGroup } from '@openfun/cunningham-react';
import { useTranslation } from 'react-i18next';

import { Role } from '../../domains';

interface ChooseRoleProps {
  availableRoles: Role[];
  currentRole: Role;
  disabled: boolean;
  setRole: (role: Role) => void;
}

export const ChooseRole = ({
  availableRoles,
  disabled,
  currentRole,
  setRole,
}: ChooseRoleProps) => {
  const { t } = useTranslation();
  const rolesToDisplay = Array.from(new Set([currentRole, ...availableRoles]));

  return (
    <RadioGroup>
      {rolesToDisplay?.map((role) => {
        switch (role) {
          case Role.VIEWER:
            return (
              <Radio
                key={Role.VIEWER}
                label={t('Viewer')}
                value={Role.VIEWER}
                name="role"
                onChange={(evt) => setRole(evt.target.value as Role)}
                defaultChecked={currentRole === Role.VIEWER}
                disabled={disabled}
              />
            );
          case Role.ADMIN:
            return (
              <Radio
                key={Role.ADMIN}
                label={t('Administrator')}
                value={Role.ADMIN}
                name="role"
                onChange={(evt) => setRole(evt.target.value as Role)}
                defaultChecked={currentRole === Role.ADMIN}
                disabled={disabled}
              />
            );
          case Role.OWNER:
            return (
              <Radio
                key={Role.OWNER}
                label={t('Owner')}
                value={Role.OWNER}
                name="role"
                onChange={(evt) => setRole(evt.target.value as Role)}
                defaultChecked={currentRole === Role.OWNER}
                disabled={disabled || currentRole !== Role.OWNER}
              />
            );
        }
      })}
    </RadioGroup>
  );
};
