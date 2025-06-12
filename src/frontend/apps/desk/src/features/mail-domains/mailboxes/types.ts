import { UUID } from 'crypto';

import { ReactNode } from 'react';

export interface MailDomainMailbox {
  id: UUID;
  local_part: string;
  first_name: string;
  last_name: string;
  secondary_email: string;
  status: MailDomainMailboxStatus;
}

export type MailDomainMailboxStatus =
  | 'enabled'
  | 'disabled'
  | 'pending'
  | 'failed';

export interface ViewMailbox {
  id: string;
  first_name: string;
  last_name: string;
  local_part: string;
  secondary_email: string;
  status: MailDomainMailboxStatus;
}

export interface Step {
  title: string;
  content: ReactNode;
  leftAction: ReactNode;
  rightAction?: ReactNode;
}
