import { faker } from '@faker-js/faker';

import { Access, Role } from '../types';

function createRandomAccess(): Access {
  return {
    id: faker.string.uuid(),
    user: {
      id: faker.string.uuid(),
      email: faker.internet.email(),
      name: faker.person.fullName(),
    },
    role: faker.helpers.enumValue(Role),
  };
}

export const dummyDataAPITeamAccesses = (count: number, pageSize: number) => {
  return {
    count,
    next: null,
    previous: null,
    results: faker.helpers.multiple(createRandomAccess, { count: pageSize }),
  };
};
