import { Button } from '@gouvfr-lasuite/cunningham-react';
import { DropdownMenu, useDropdownMenu } from '@gouvfr-lasuite/ui-kit';
import { useTranslation } from 'react-i18next';

import { Icon } from '@/components';
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

  const translations: Record<Role, string> = {
    [Role.VIEWER]: t('Viewer'),
    [Role.ADMIN]: t('Administrator'),
    [Role.OWNER]: t('Owner'),
  };

  const { isOpen, setIsOpen } = useDropdownMenu();

  const orderedRolesToDisplay = ORDERED_ROLES.filter((role) =>
    rolesToDisplay.includes(role),
  );

  const selectedRole = orderedRolesToDisplay.includes(roleAccess)
    ? roleAccess
    : orderedRolesToDisplay[0];

  const menuOptions =
    orderedRolesToDisplay.map((role) => {
      const isOwnerDisabled = role === Role.OWNER && currentRole !== Role.OWNER;
      const isOptionDisabled = disabled || isOwnerDisabled;

      return {
        label: translations[role],
        callback: () => {
          if (isOptionDisabled) {
            return;
          }
          setIsOpen(false);
          setRole(role);
        },
        isDisabled: isOptionDisabled,
      };
    }) ?? [];

  const selectedLabel = selectedRole ? translations[selectedRole] : '';

  return (
    <DropdownMenu
      options={menuOptions}
      isOpen={isOpen}
      onOpenChange={setIsOpen}
    >
      <Button
        variant="tertiary"
        color="brand"
        size="small"
        disabled={disabled || orderedRolesToDisplay.length === 0}
        aria-haspopup="menu"
        aria-expanded={isOpen}
        icon={<Icon iconName="expand_more" $size="sm" $color="brand" />}
        iconPosition="right"
        onClick={() => {
          if (disabled || orderedRolesToDisplay.length === 0) {
            return;
          }
          setIsOpen(!isOpen);
        }}
      >
        {selectedLabel}
      </Button>
    </DropdownMenu>
  );
};
