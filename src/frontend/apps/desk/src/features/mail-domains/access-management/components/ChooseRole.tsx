import { Radio, RadioGroup } from '@openfun/cunningham-react';
import { useTranslation } from 'react-i18next';

import { Role } from '@/features/mail-domains/domains/types';

const ORDERED_ROLES = [Role.VIEWER, Role.ADMIN, Role.OWNER];

interface ChooseRoleProps {
  availableRoles: Role[];
  roleAccess: Role;
  currentRole: Role;
  disabled: boolean;
  setRole: (role: Role) => void;
}

export const ChooseRole = ({
  availableRoles,
  roleAccess,
  disabled,
  currentRole,
  setRole,
}: ChooseRoleProps) => {
  const { t } = useTranslation();
  const rolesToDisplay: Role[] = Array.from(
    new Set([roleAccess, ...availableRoles]),
  );

  const translations = {
    [Role.VIEWER]: t('Viewer'),
    [Role.ADMIN]: t('Administrator'),
    [Role.OWNER]: t('Owner'),
  };

  return (
    <RadioGroup>
      {ORDERED_ROLES.filter((role) => rolesToDisplay.includes(role)).map(
        (role) => {
          let disableRadio = disabled;
          if (role === Role.OWNER) {
            disableRadio = disableRadio || currentRole !== Role.OWNER;
          }

          return (
            <Radio
              key={role}
              label={translations[role]}
              value={role}
              name="role"
              onChange={(evt) => setRole(evt.target.value as Role)}
              defaultChecked={roleAccess === role}
              disabled={disableRadio}
            />
          );
        },
      )}
    </RadioGroup>
  );
};
