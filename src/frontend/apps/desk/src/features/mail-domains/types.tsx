import { UUID } from 'crypto';

export interface MailDomain {
  id: UUID;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface MailDomainMailbox {
  id: UUID;
  local_part: string;
  secondary_email: string;
}
