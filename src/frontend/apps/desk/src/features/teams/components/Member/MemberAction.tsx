import { Button } from '@openfun/cunningham-react';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { DropButton, Text } from '@/components';
import { Access, Role } from '@/features/teams/api';

import { ModalRole } from './ModalRole';

interface MemberActionProps {
  access: Access;
  currentRole: Role;
  teamId: string;
}

export const MemberAction = ({
  access,
  currentRole,
  teamId,
}: MemberActionProps) => {
  const { t } = useTranslation();
  const [isModalRoleOpen, setIsModalRoleOpen] = useState(false);
  const [isDropOpen, setIsDropOpen] = useState(false);

  if (
    currentRole === Role.MEMBER ||
    (access.role === Role.OWNER && currentRole === Role.ADMIN)
  ) {
    return null;
  }

  return (
    <>
      <DropButton
        button={
          <span
            aria-label={t('Member options')}
            className="material-icons"
            style={{
              transition: 'all 0.3s ease-in-out',
              transform: `rotate(${isDropOpen ? '90' : '0'}deg)`,
            }}
          >
            more_vert
          </span>
        }
        onOpenChange={(isOpen) => setIsDropOpen(isOpen)}
        isOpen={isDropOpen}
      >
        <Button
          onClick={() => {
            setIsModalRoleOpen(true);
            setIsDropOpen(false);
          }}
          color="primary-text"
          icon={<span className="material-icons">edit</span>}
        >
          <Text $theme="primary">{t('Update the role')}</Text>
        </Button>
      </DropButton>
      {isModalRoleOpen && (
        <ModalRole
          access={access}
          currentRole={currentRole}
          onClose={() => setIsModalRoleOpen(false)}
          teamId={teamId}
        />
      )}
    </>
  );
};
