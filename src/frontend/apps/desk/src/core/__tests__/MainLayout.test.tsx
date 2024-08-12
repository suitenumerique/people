import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';

import { AppWrapper } from '@/tests/utils';

import { MainLayout } from '../MainLayout';

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  usePathname: () => '/',
}));

describe('MainLayout', () => {
  it('checks menu rendering', () => {
    render(<MainLayout />, { wrapper: AppWrapper });

    expect(
      screen.getByRole('link', {
        name: /Teams button/i,
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole('link', {
        name: /Mail Domains button/i,
      }),
    ).toBeInTheDocument();
  });

  it('checks menu rendering without team feature', () => {
    process.env.NEXT_PUBLIC_FEATURE_TEAM = 'false';

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
