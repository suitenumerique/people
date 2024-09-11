import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';

import { AppWrapper } from '@/tests/utils';

import { MainLayout } from '../MainLayout';
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
      config: { FEATURES: { TEAMS: true }, LANGUAGES: [] },
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

  it('checks menu rendering without team feature', () => {
    useConfigStore.setState({
      config: { FEATURES: { TEAMS: false }, LANGUAGES: [] },
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
