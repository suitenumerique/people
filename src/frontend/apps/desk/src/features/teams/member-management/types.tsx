import { User } from '@/core/auth';
import { Role } from '@/features/teams/team-management';

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
