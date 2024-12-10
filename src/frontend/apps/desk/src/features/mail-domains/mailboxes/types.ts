import { UUID } from 'crypto';

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
