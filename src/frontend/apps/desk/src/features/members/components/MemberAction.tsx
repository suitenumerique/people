import { Button } from '@openfun/cunningham-react';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { DropButton, IconOptions, Text } from '@/components';

import { Access, Role } from '../types';

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
          <IconOptions
            isOpen={isDropOpen}
            aria-label={t('Open the member options modal')}
          />
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
