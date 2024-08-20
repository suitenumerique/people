import '@testing-library/jest-dom';
import { render } from '@testing-library/react';

import { useConfigStore } from '@/core';
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
    useConfigStore.setState({
      config: { FEATURES: { TEAMS: true }, LANGUAGES: [] },
    });

    render(<Page />, { wrapper: AppWrapper });

    expect(mockedPush).toHaveBeenCalledWith('/teams/');
  });

  it('checks Page rendering without team feature', () => {
    useConfigStore.setState({
      config: { FEATURES: { TEAMS: false }, LANGUAGES: [] },
    });

    render(<Page />, { wrapper: AppWrapper });

    expect(mockedPush).toHaveBeenCalledWith('/mail-domains/');
  });
});
