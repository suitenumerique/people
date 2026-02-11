import {
  Button,
  VariantType,
  useToastProvider,
} from '@openfun/cunningham-react';
import React, { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { IconOptions, Text } from '@/components';

import { MailDomain, Role } from '../../domains/types';
import { useDeleteMailDomainInvitation } from '../api';
import { Access } from '../types';

interface InvitationActionProps {
  access: Access;
  currentRole: Role;
  mailDomain: MailDomain;
}

export const InvitationAction = ({
  access,
  currentRole,
  mailDomain,
}: InvitationActionProps) => {
  const { t } = useTranslation();
  const { toast } = useToastProvider();
  const [isDropOpen, setIsDropOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const { mutate: deleteMailDomainInvitation } = useDeleteMailDomainInvitation({
    onSuccess: () => {
      toast(t('The invitation has been deleted'), VariantType.SUCCESS, {
        duration: 4000,
      });
    },
  });

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

  if (currentRole === Role.VIEWER) {
    return null;
  }

  const canDelete = currentRole === Role.OWNER || currentRole === Role.ADMIN;

  if (!canDelete) {
    return null;
  }

  return (
    <div
      style={{ position: 'relative', display: 'inline-block' }}
      ref={dropdownRef}
    >
      <button
        onClick={() => setIsDropOpen((prev) => !prev)}
        aria-label={t('Open the invitation options modal')}
        style={{
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          padding: 4,
        }}
        type="button"
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
          {canDelete && (
            <Button
              aria-label={t('Delete this invitation')}
              onClick={() => {
                deleteMailDomainInvitation({
                  slug: mailDomain.slug,
                  invitationId: access.id,
                });
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
              <Text $theme="primary">{t('Delete invitation')}</Text>
            </Button>
          )}
        </div>
      )}
    </div>
  );
};
