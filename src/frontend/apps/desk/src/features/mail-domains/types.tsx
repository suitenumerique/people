import { UUID } from 'crypto';

export interface MailDomain {
  id: UUID;
  name: string;
  created_at: string;
  updated_at: string;
  slug: string;
  abilities: {
    get: boolean;
    patch: boolean;
    put: boolean;
    post: boolean;
    delete: boolean;
    manage_accesses: boolean;
  };
}

export interface MailDomainMailbox {
  id: UUID;
  local_part: string;
  secondary_email: string;
}
