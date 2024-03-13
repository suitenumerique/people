import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import fetchMock from 'fetch-mock';

import { AppWrapper } from '@/tests/utils';

import { MemberGrid } from '../components/MemberGrid';
import { Access, Role } from '../types';

describe('MemberGrid', () => {
  afterEach(() => {
    fetchMock.restore();
  });

  it('renders with no member to display', async () => {
    fetchMock.mock(`/api/teams/123456/accesses/?page=1`, {
      count: 0,
      results: [],
    });

    render(<MemberGrid teamId="123456" currentRole={Role.ADMIN} />, {
      wrapper: AppWrapper,
    });

    expect(screen.getByRole('status')).toBeInTheDocument();

    expect(await screen.findByRole('img')).toHaveAttribute(
      'alt',
      'Illustration of an empty table',
    );

    expect(screen.getByText('This table is empty')).toBeInTheDocument();
  });

  it('checks the render with members', async () => {
    const accesses: Access[] = [
      {
        id: '1',
        role: Role.OWNER,
        user: {
          id: '11',
          name: 'username1',
          email: 'user1@test.com',
        },
        abilities: {} as any,
      },
      {
        id: '2',
        role: Role.MEMBER,
        user: {
          id: '22',
          name: 'username2',
          email: 'user2@test.com',
        },
        abilities: {} as any,
      },
      {
        id: '32',
        role: Role.ADMIN,
        user: {
          id: '33',
          name: 'username3',
          email: 'user3@test.com',
        },
        abilities: {} as any,
      },
    ];

    fetchMock.mock(`/api/teams/123456/accesses/?page=1`, {
      count: 3,
      results: accesses,
    });

    render(<MemberGrid teamId="123456" currentRole={Role.ADMIN} />, {
      wrapper: AppWrapper,
    });

    expect(screen.getByRole('status')).toBeInTheDocument();

    expect(await screen.findByText('username1')).toBeInTheDocument();
    expect(screen.getByText('username2')).toBeInTheDocument();
    expect(screen.getByText('username3')).toBeInTheDocument();
    expect(screen.getByText('user1@test.com')).toBeInTheDocument();
    expect(screen.getByText('user2@test.com')).toBeInTheDocument();
    expect(screen.getByText('user3@test.com')).toBeInTheDocument();
    expect(screen.getByText('Owner')).toBeInTheDocument();
    expect(screen.getByText('Admin')).toBeInTheDocument();
    expect(screen.getByText('Member')).toBeInTheDocument();
  });

  it('checks the pagination', async () => {
    fetchMock.get(`begin:/api/teams/123456/accesses/?page=`, {
      count: 40,
      results: Array.from({ length: 20 }, (_, i) => ({
        id: i,
        role: Role.OWNER,
        user: {
          id: i,
          name: 'username' + i,
          email: `user${i}@test.com`,
        },
        abilities: {} as any,
      })),
    });

    render(<MemberGrid teamId="123456" currentRole={Role.ADMIN} />, {
      wrapper: AppWrapper,
    });

    expect(screen.getByRole('status')).toBeInTheDocument();

    expect(fetchMock.lastUrl()).toBe('/api/teams/123456/accesses/?page=1');

    expect(
      await screen.findByLabelText('You are currently on page 1'),
    ).toBeInTheDocument();

    await userEvent.click(screen.getByLabelText('Go to page 2'));

    expect(
      await screen.findByLabelText('You are currently on page 2'),
    ).toBeInTheDocument();

    expect(fetchMock.lastUrl()).toBe('/api/teams/123456/accesses/?page=2');
  });

  [
    {
      role: Role.OWNER,
      expected: true,
    },
    {
      role: Role.MEMBER,
      expected: false,
    },
    {
      role: Role.ADMIN,
      expected: true,
    },
  ].forEach(({ role, expected }) => {
    it(`checks action button when ${role}`, async () => {
      fetchMock.get(`begin:/api/teams/123456/accesses/?page=`, {
        count: 1,
        results: [
          {
            id: 1,
            role: Role.ADMIN,
            user: {
              id: 1,
              name: 'username1',
              email: `user1@test.com`,
            },
            abilities: {} as any,
          },
        ],
      });

      render(<MemberGrid teamId="123456" currentRole={role} />, {
        wrapper: AppWrapper,
      });

      expect(screen.getByRole('status')).toBeInTheDocument();

      /* eslint-disable jest/no-conditional-expect */
      if (expected) {
        expect(
          await screen.findAllByRole('button', {
            name: 'Member options',
          }),
        ).toBeDefined();
      } else {
        expect(
          screen.queryByRole('button', {
            name: 'Member options',
          }),
        ).not.toBeInTheDocument();
      }
      /* eslint-enable jest/no-conditional-expect */
    });
  });

  it('controls the render when api error', async () => {
    fetchMock.mock(`/api/teams/123456/accesses/?page=1`, {
      status: 500,
      body: {
        cause: 'All broken :(',
      },
    });

    render(<MemberGrid teamId="123456" currentRole={Role.ADMIN} />, {
      wrapper: AppWrapper,
    });

    expect(screen.getByRole('status')).toBeInTheDocument();

    expect(await screen.findByText('All broken :(')).toBeInTheDocument();
  });
});
