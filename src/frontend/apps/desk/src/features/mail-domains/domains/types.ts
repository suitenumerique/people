import { UUID } from 'crypto';

export interface MailDomain {
  id: UUID;
  name: string;
  created_at: string;
  updated_at: string;
  slug: string;
  status: 'pending' | 'enabled' | 'failed' | 'disabled' | 'action_required';
  support_email: string;
  abilities: {
    get: boolean;
    patch: boolean;
    put: boolean;
    post: boolean;
    delete: boolean;
    manage_accesses: boolean;
  };
}

export enum Role {
  ADMIN = 'administrator',
  OWNER = 'owner',
  VIEWER = 'viewer',
}
