import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { useAuthStore } from '@/core/auth';
import { AppWrapper } from '@/tests/utils';

import { AccountDropdown } from '../AccountDropdown';

describe('AccountDropdown', () => {
  const mockLogout = jest.fn();

  const renderAccountDropdown = () =>
    render(<AccountDropdown />, { wrapper: AppWrapper });

  beforeEach(() => {
    jest.clearAllMocks();
    useAuthStore.setState({
      userData: {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
      },
      logout: mockLogout,
    });
  });

  it('renders the user name correctly', async () => {
    renderAccountDropdown();

    expect(await screen.findByText('Test User')).toBeInTheDocument();
  });

  it('renders "No Username" when userData name is missing', () => {
    useAuthStore.setState({
      userData: {
        id: '1',
        email: 'test@example.com',
      },
      logout: mockLogout,
    });

    renderAccountDropdown();
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
  });

  it('opens the dropdown and shows logout button when clicked', async () => {
    renderAccountDropdown();

    const dropButton = await screen.findByText('Test User');
    await userEvent.click(dropButton);

    expect(screen.getByText('Logout')).toBeInTheDocument();
    expect(screen.getByLabelText('Logout')).toBeInTheDocument();
  });

  it('calls logout function when logout button is clicked', async () => {
    renderAccountDropdown();

    const dropButton = await screen.findByText('Test User');
    await userEvent.click(dropButton);

    const logoutButton = screen.getByLabelText('Logout');
    await userEvent.click(logoutButton);

    expect(mockLogout).toHaveBeenCalledTimes(1);
  });
});
