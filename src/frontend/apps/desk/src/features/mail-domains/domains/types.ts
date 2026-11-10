import { UUID } from 'crypto';

import { User } from '@/core/auth';

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

export enum OptionType {
  INVITATION = 'invitation',
  NEW_MEMBER = 'new_member',
}

export const isOptionNewMember = (
  data: OptionSelect,
): data is OptionNewMember => {
  return 'id' in data.value;
};

export interface OptionInvitation {
  value: { email: string };
  label: string;
  type: OptionType.INVITATION;
}

export interface OptionNewMember {
  value: User;
  label: string;
  type: OptionType.NEW_MEMBER;
}

export type OptionSelect = OptionNewMember | OptionInvitation;

export type OptionsSelect = readonly OptionSelect[];

export interface Invitation {
  id: string;
  created_at: string;
  email: string;
  team: 0;
  role: Role;
  issuer: User['id'];
  is_expired: boolean;
}
