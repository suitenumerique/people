import '@testing-library/jest-dom';
import { render } from '@testing-library/react';

import { useConfigStore } from '@/core';
import { useAuthStore } from '@/core/auth';
import { AppWrapper } from '@/tests/utils';

import Page from '../pages';

const mockedPush = jest.fn();
const mockedUseRouter = jest.fn().mockReturnValue({
  push: mockedPush,
});

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: () => mockedUseRouter(),
}));

describe('Page', () => {
  afterEach(() => jest.clearAllMocks());

  it('checks Page rendering with team feature', () => {
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

    useConfigStore.setState({
      config: {
        CRISP_WEBSITE_ID: 'wesh',
        RELEASE: '1.0.0',
        COMMIT: 'NA',
        FEATURES: { TEAMS_DISPLAY: true },
        LANGUAGES: [],
      },
    });

    render(<Page />, { wrapper: AppWrapper });

    expect(mockedPush).toHaveBeenCalledWith('/teams/');
  });

  it('checks Page rendering without team feature', () => {
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

    useConfigStore.setState({
      config: {
        CRISP_WEBSITE_ID: 'wesh',
        RELEASE: '1.0.0',
        COMMIT: 'NA',
        FEATURES: { TEAMS_DISPLAY: false },
        LANGUAGES: [],
      },
    });

    render(<Page />, { wrapper: AppWrapper });

    expect(mockedPush).toHaveBeenCalledWith('/mail-domains/');
  });

  it('checks Page rendering with team permission', () => {
    useAuthStore.setState({
      authenticated: true,
      userData: {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        abilities: {
          contacts: { can_view: false },
          teams: { can_view: true },
          mailboxes: { can_view: false },
        },
      },
    });

    useConfigStore.setState({
      config: {
        CRISP_WEBSITE_ID: 'wesh',
        RELEASE: '1.0.0',
        COMMIT: 'NA',
        FEATURES: { TEAMS_DISPLAY: false },
        LANGUAGES: [],
      },
    });

    render(<Page />, { wrapper: AppWrapper });

    expect(mockedPush).toHaveBeenCalledWith('/teams/');
  });

  it('checks Page rendering with mailbox permission', () => {
    useAuthStore.setState({
      authenticated: true,
      userData: {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        abilities: {
          contacts: { can_view: false },
          teams: { can_view: false },
          mailboxes: { can_view: true },
        },
      },
    });

    useConfigStore.setState({
      config: {
        CRISP_WEBSITE_ID: 'wesh',
        RELEASE: '1.0.0',
        COMMIT: 'NA',
        FEATURES: { TEAMS_DISPLAY: true },
        LANGUAGES: [],
      },
    });

    render(<Page />, { wrapper: AppWrapper });

    expect(mockedPush).toHaveBeenCalledWith('/mail-domains/');
  });
});
