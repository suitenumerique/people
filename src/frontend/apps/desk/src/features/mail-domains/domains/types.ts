import { UUID } from 'crypto';

export interface MailDomain {
  id: UUID;
  name: string;
  count_mailboxes?: number;
  created_at: string;
  updated_at: string;
  slug: string;
  status: 'pending' | 'enabled' | 'failed' | 'disabled' | 'action_required';
  support_email: string;
  action_required_details?: Record<string, string>;
  abilities: {
    get: boolean;
    patch: boolean;
    put: boolean;
    post: boolean;
    delete: boolean;
    manage_accesses: boolean;
  };
  expected_config?: Array<{
    target: string;
    type: string;
    value: string;
  }>;
}

export enum Role {
  ADMIN = 'administrator',
  OWNER = 'owner',
  VIEWER = 'viewer',
}
