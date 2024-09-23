import { UUID } from 'crypto';

import { User } from '@/core/auth';

import { Role } from '../domains/types';

export interface Access {
  id: UUID;
  role: Role;
  user: User;
  can_set_role_to: Role[];
}
