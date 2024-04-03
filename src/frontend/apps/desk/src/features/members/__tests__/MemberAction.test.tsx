import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import fetchMock from 'fetch-mock';

import { Role, Team } from '@/features/teams';
import { AppWrapper } from '@/tests/utils';

import { MemberAction } from '../components/MemberAction';
import { Access } from '../types';

const access: Access = {
  id: '789',
  role: Role.ADMIN,
  user: {
    id: '11',
    name: 'username1',
    email: 'user1@test.com',
  },
  abilities: {
    set_role_to: [Role.MEMBER, Role.ADMIN],
  } as any,
};

const team = {
  id: '123456',
  name: 'teamName',
} as Team;

describe('MemberAction', () => {
  afterEach(() => {
    fetchMock.restore();
  });

  it('checks the render when owner', async () => {
    render(
      <MemberAction access={access} currentRole={Role.OWNER} team={team} />,
      {
        wrapper: AppWrapper,
      },
    );

    expect(
      await screen.findByLabelText('Open the member options modal'),
    ).toBeInTheDocument();
  });

  it('checks the render when member', () => {
    render(
      <MemberAction access={access} currentRole={Role.MEMBER} team={team} />,
      {
        wrapper: AppWrapper,
      },
    );

    expect(
      screen.queryByLabelText('Open the member options modal'),
    ).not.toBeInTheDocument();
  });

  it('checks the render when admin', async () => {
    render(
      <MemberAction access={access} currentRole={Role.ADMIN} team={team} />,
      {
        wrapper: AppWrapper,
      },
    );

    expect(
      await screen.findByLabelText('Open the member options modal'),
    ).toBeInTheDocument();
  });

  it('checks the render when admin to owner', () => {
    render(
      <MemberAction
        access={{ ...access, role: Role.OWNER }}
        currentRole={Role.ADMIN}
        team={team}
      />,
      {
        wrapper: AppWrapper,
      },
    );

    expect(
      screen.queryByLabelText('Open the member options modal'),
    ).not.toBeInTheDocument();
  });
});
