import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import fetchMock from 'fetch-mock';

import { AppWrapper } from '@/tests/utils';

import { Teams } from '..';

describe('Teams', () => {
  afterEach(() => {
    fetchMock.restore();
  });

  it('checks Teams rendering', async () => {
    fetchMock.mock(`/api/teams/`, {
      results: [
        {
          id: '1',
          name: 'Team 1',
        },
        {
          id: '2',
          name: 'Team 2',
        },
      ],
    });

    render(<Teams />, { wrapper: AppWrapper });

    expect(screen.getByRole('status')).toBeInTheDocument();

    expect(
      await screen.findByRole('button', {
        name: 'Create Team',
      }),
    ).toBeInTheDocument();

    expect(screen.getByText(/Team 1/)).toBeInTheDocument();
    expect(screen.getByText(/Team 2/)).toBeInTheDocument();
  });
});
