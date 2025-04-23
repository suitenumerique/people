import { User } from '@/core/auth';

import { Role, Team } from '../team-management';

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
  team: Team['id'];
  role: Role;
  issuer: User['id'];
  is_expired: boolean;
}
