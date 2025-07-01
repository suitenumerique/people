import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import fetchMock from 'fetch-mock';
import React from 'react';

import { AppWrapper } from '@/tests/utils';

import { ModalCreateTeam } from '../ModalCreateTeam';

const mockClose = jest.fn();

const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

describe('ModalCreateTeam', () => {
  const renderModal = () =>
    render(<ModalCreateTeam closeModal={mockClose} />, { wrapper: AppWrapper });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    fetchMock.restore();
  });

  it('renders all the elements', () => {
    renderModal();
    expect(screen.getByText('Create a new team')).toBeInTheDocument();
    expect(screen.getByLabelText('Team name')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
    expect(screen.getByText('Create the team')).toBeInTheDocument();
  });

  it('handles input for team name and enables submit button', async () => {
    const user = userEvent.setup();
    renderModal();
    const teamNameInput = screen.getByLabelText('Team name');
    const createButton = screen.getByText('Create the team');
    expect(createButton).toBeDisabled();
    await user.type(teamNameInput, 'New Team');
    expect(createButton).toBeEnabled();
  });

  it('creates a team successfully and redirects', async () => {
    fetchMock.post('end:teams/', {
      id: '270328ea-c2c0-4f74-a449-5cdc976dcdb6',
      name: 'New Team',
    });
    const user = userEvent.setup();
    renderModal();
    const teamNameInput = screen.getByLabelText('Team name');
    const createButton = screen.getByText('Create the team');
    await user.type(teamNameInput, 'New Team');
    await user.click(createButton);
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith(
        '/teams/270328ea-c2c0-4f74-a449-5cdc976dcdb6',
      );
    });
    expect(fetchMock.calls()).toHaveLength(1);
    expect(fetchMock.lastCall()?.[0]).toContain('/teams/');
    expect(fetchMock.lastCall()?.[1]?.body).toEqual(
      JSON.stringify({ name: 'New Team' }),
    );
  });

  it('displays an error message when team name already exists', async () => {
    fetchMock.post('end:teams/', {
      body: {
        cause: ['Team with this Slug already exists.'],
      },
      status: 400,
    });
    const user = userEvent.setup();
    renderModal();
    const teamNameInput = screen.getByLabelText('Team name');
    const createButton = screen.getByText('Create the team');
    await user.type(teamNameInput, 'Existing Team');
    await user.click(createButton);
    await waitFor(() => {
      expect(
        screen.getByText(/This name is already used for another group/i),
      ).toBeInTheDocument();
    });
  });

  it('handles server error gracefully', async () => {
    fetchMock.post('end:/teams/', {
      body: {},
      status: 500,
    });
    const user = userEvent.setup();
    renderModal();
    const teamNameInput = screen.getByLabelText('Team name');
    const createButton = screen.getByText('Create the team');
    await user.type(teamNameInput, 'Server Error Team');
    await user.click(createButton);
    await waitFor(() => {
      expect(
        screen.getByText(
          /Your request cannot be processed because the server is experiencing an error/i,
        ),
      ).toBeInTheDocument();
    });
    expect(fetchMock.calls()).toHaveLength(1);
    expect(fetchMock.lastCall()?.[0]).toContain('/teams/');
    expect(fetchMock.lastCall()?.[1]?.body).toEqual(
      JSON.stringify({ name: 'Server Error Team' }),
    );
  });

  it('disables create button when API request is pending', async () => {
    // Never resolves
    fetchMock.post('end:teams/', new Promise(() => {}));
    const user = userEvent.setup();
    renderModal();
    const teamNameInput = screen.getByLabelText('Team name');
    const createButton = screen.getByText('Create the team');
    await user.type(teamNameInput, 'Pending Team');
    await user.click(createButton);
    expect(createButton).toBeDisabled();
  });
});
