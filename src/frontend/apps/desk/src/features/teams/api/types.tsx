enum Role {
  MEMBER = 'member',
  ADMIN = 'administrator',
  OWNER = 'owner',
}

export interface Access {
  id: string;
  role: Role;
  user: string;
}

export interface TeamResponse {
  id: string;
  name: string;
  accesses: Access[];
}
