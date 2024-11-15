import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';

import { AppWrapper } from '@/tests/utils';

import { MainLayout } from '../MainLayout';
import { useAuthStore } from '../auth';
import { useConfigStore } from '../config';

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  usePathname: () => '/',
  useRouter: () => ({
    push: () => {},
  }),
}));

describe('MainLayout', () => {
  it('checks menu rendering with team feature', () => {
    useConfigStore.setState({
      config: {
        RELEASE: '1.0.0',
        COMMIT: 'NA',
        FEATURES: { TEAMS_DISPLAY: true },
        LANGUAGES: [],
      },
    });
    useAuthStore.setState({
      authenticated: true,
      userData: {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        abilities: {
          contacts: { can_view: true },
          teams: { can_view: true },
          mailboxes: { can_view: true },
        },
      },
    });

    render(<MainLayout />, { wrapper: AppWrapper });

    expect(
      screen.getByRole('button', {
        name: /Teams button/i,
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole('button', {
        name: /Mail Domains button/i,
      }),
    ).toBeInTheDocument();
  });

  it('checks menu rendering with no abilities', () => {
    useConfigStore.setState({
      config: {
        RELEASE: '1.0.0',
        COMMIT: 'NA',
        FEATURES: { TEAMS_DISPLAY: true },
        LANGUAGES: [],
      },
    });
    useAuthStore.setState({
      authenticated: true,
      userData: {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        abilities: {
          contacts: { can_view: false },
          teams: { can_view: false },
          mailboxes: { can_view: false },
        },
      },
    });

    render(<MainLayout />, { wrapper: AppWrapper });

    expect(
      screen.queryByRole('button', {
        // Changé de getByRole à queryByRole
        name: /Teams button/i,
      }),
    ).not.toBeInTheDocument(); //

    expect(
      screen.queryByRole('button', {
        name: /Mail Domains button/i,
      }),
    ).not.toBeInTheDocument();
  });

  it('checks menu rendering without team feature', () => {
    useConfigStore.setState({
      config: {
        RELEASE: '1.0.0',
        COMMIT: 'NA',
        FEATURES: { TEAMS_DISPLAY: false },
        LANGUAGES: [],
      },
    });
    useAuthStore.setState({
      authenticated: true,
      userData: {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        abilities: {
          contacts: { can_view: true },
          teams: { can_view: true },
          mailboxes: { can_view: true },
        },
      },
    });

    render(<MainLayout />, { wrapper: AppWrapper });

    expect(
      screen.queryByRole('button', {
        name: /Teams button/i,
      }),
    ).not.toBeInTheDocument();

    expect(
      screen.queryByRole('button', {
        name: /Mail Domains button/i,
      }),
    ).not.toBeInTheDocument();
  });
});
