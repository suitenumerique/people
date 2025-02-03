import { Button } from '@openfun/cunningham-react';
import React, { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { IconOptions, Text } from '@/components';

import { MailDomain, Role } from '../../domains/types';
import { Access } from '../types';

import { ModalDelete } from './ModalDelete';
import { ModalRole } from './ModalRole';

interface AccessActionProps {
  access: Access;
  currentRole: Role;
  mailDomain: MailDomain;
}

export const AccessAction = ({
  access,
  currentRole,
  mailDomain,
}: AccessActionProps) => {
  const { t } = useTranslation();
  const [isModalRoleOpen, setIsModalRoleOpen] = useState(false);
  const [isModalDeleteOpen, setIsModalDeleteOpen] = useState(false);
  const [isDropOpen, setIsDropOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Ferme le menu si clic en dehors
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node)
      ) {
        setIsDropOpen(false);
      }
    };
    if (isDropOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isDropOpen]);

  if (
    currentRole === Role.VIEWER ||
    (access.role === Role.OWNER && currentRole === Role.ADMIN)
  ) {
    return null;
  }

  return (
    <>
      <div
        style={{ position: 'relative', display: 'inline-block' }}
        ref={dropdownRef}
      >
        <button
          onClick={() => setIsDropOpen((prev) => !prev)}
          aria-label={t('Open the access options modal')}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: 4,
          }}
        >
          <IconOptions />
        </button>

        {isDropOpen && (
          <div
            role="menu"
            tabIndex={0}
            style={{
              position: 'absolute',
              top: '100%',
              right: 0,
              zIndex: 1000,
              background: 'white',
              border: '1px solid #ccc',
              borderRadius: 4,
              padding: '0.5rem',
              minWidth: '210px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            }}
            onClick={(e) => e.stopPropagation()}
            onKeyDown={(e) => {
              if (e.key === 'Escape' || e.key === 'Enter') {
                setIsDropOpen(false);
              }
            }}
          >
            {(mailDomain.abilities.put || mailDomain.abilities.patch) && (
              <Button
                aria-label={t(
                  'Open the modal to update the role of this access',
                )}
                onClick={() => {
                  setIsModalRoleOpen(true);
                  setIsDropOpen(false);
                }}
                color="primary-text"
                size="small"
                fullWidth
                icon={
                  <span className="material-icons" aria-hidden="true">
                    edit
                  </span>
                }
              >
                <Text $theme="primary">{t('Update role')}</Text>
              </Button>
            )}
            {mailDomain.abilities.delete && (
              <Button
                aria-label={t('Open the modal to delete this access')}
                onClick={() => {
                  setIsModalDeleteOpen(true);
                  setIsDropOpen(false);
                }}
                color="primary-text"
                size="small"
                fullWidth
                icon={
                  <span className="material-icons" aria-hidden="true">
                    delete
                  </span>
                }
              >
                <Text $theme="primary">{t('Remove from domain')}</Text>
              </Button>
            )}
          </div>
        )}
      </div>

      {isModalRoleOpen &&
        (mailDomain.abilities.put || mailDomain.abilities.patch) && (
          <ModalRole
            access={access}
            currentRole={currentRole}
            onClose={() => setIsModalRoleOpen(false)}
            slug={mailDomain.slug}
          />
        )}
      {isModalDeleteOpen && mailDomain.abilities.delete && (
        <ModalDelete
          access={access}
          currentRole={currentRole}
          onClose={() => setIsModalDeleteOpen(false)}
          mailDomain={mailDomain}
        />
      )}
    </>
  );
};
