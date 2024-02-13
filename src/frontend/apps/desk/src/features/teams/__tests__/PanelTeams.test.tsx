import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import fetchMock from 'fetch-mock';

import { AppWrapper } from '@/tests/utils';

import { PanelTeams } from '../components/PanelTeams';

describe('PanelTeams', () => {
  afterEach(() => {
    fetchMock.restore();
  });

  it('renders with no team to display', async () => {
    fetchMock.mock(`/api/teams/?page=1&ordering=-created_at`, {
      count: 0,
      results: [],
    });

    render(<PanelTeams />, { wrapper: AppWrapper });

    expect(screen.getByRole('status')).toBeInTheDocument();

    expect(
      await screen.findByText(
        'Create your first team by clicking on the "Create a new team" button.',
      ),
    ).toBeInTheDocument();
  });

  it('renders with empty team to display', async () => {
    fetchMock.mock(`/api/teams/?page=1&ordering=-created_at`, {
      count: 1,
      results: [
        {
          id: '1',
          name: 'Team 1',
          accesses: [],
        },
      ],
    });

    render(<PanelTeams />, { wrapper: AppWrapper });

    expect(screen.getByRole('status')).toBeInTheDocument();

    expect(await screen.findByLabelText('Empty team icon')).toBeInTheDocument();
  });

  it('renders with not team to display', async () => {
    fetchMock.mock(`/api/teams/?page=1&ordering=-created_at`, {
      count: 1,
      results: [
        {
          id: '1',
          name: 'Team 1',
          accesses: [
            {
              id: '1',
              role: 'admin',
            },
          ],
        },
      ],
    });

    render(<PanelTeams />, { wrapper: AppWrapper });

    expect(screen.getByRole('status')).toBeInTheDocument();

    expect(await screen.findByLabelText('Team icon')).toBeInTheDocument();
  });

  it('renders the error', async () => {
    fetchMock.mock(`/api/teams/?page=1&ordering=-created_at`, {
      status: 500,
    });

    render(<PanelTeams />, { wrapper: AppWrapper });

    expect(screen.getByRole('status')).toBeInTheDocument();

    expect(
      await screen.findByText(
        'Something bad happens, please refresh the page.',
      ),
    ).toBeInTheDocument();
  });
});
