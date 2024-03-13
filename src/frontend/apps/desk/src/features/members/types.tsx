import { User } from '@/features/auth/';

export enum Role {
  MEMBER = 'member',
  ADMIN = 'administrator',
  OWNER = 'owner',
}

export interface Access {
  id: string;
  role: Role;
  user: User;
  abilities: {
    delete: boolean;
    get: boolean;
    patch: boolean;
    put: boolean;
    set_role_to: Role[];
  };
}
