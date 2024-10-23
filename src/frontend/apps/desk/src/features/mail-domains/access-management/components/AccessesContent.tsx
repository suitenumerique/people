import React from 'react';

import { AccessesGrid } from '@/features/mail-domains/access-management/components/AccessesGrid';

import { MailDomain, Role } from '../../domains';

export const AccessesContent = ({
  mailDomain,
  currentRole,
}: {
  mailDomain: MailDomain;
  currentRole: Role;
}) => (
  <>
    <AccessesGrid mailDomain={mailDomain} currentRole={currentRole} />
  </>
);
