import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import fetchMock from 'fetch-mock';
import React from 'react';

import { AppWrapper } from '@/tests/utils';

import { ModalAddMailDomain } from '../components';

const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: jest.fn().mockImplementation(() => ({
    push: mockPush,
  })),
}));

describe('ModalAddMailDomain', () => {
  const getElements = () => ({
    modalElement: screen.getByText('Add a mail domain'),
    formTag: screen.getByTitle('Mail domain addition form'),
    inputName: screen.getByLabelText(/Domain name/i),
    inputSupportEmail: screen.getByLabelText(/Support email address/i),
    buttonCancel: screen.getByRole('button', { name: /Cancel/i, hidden: true }),
    buttonSubmit: screen.getByRole('button', {
      name: /Add the domain/i,
      hidden: true,
    }),
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    fetchMock.restore();
  });

  it('renders all the elements', () => {
    render(<ModalAddMailDomain />, { wrapper: AppWrapper });

    const {
      modalElement,
      formTag,
      inputName,
      inputSupportEmail,
      buttonCancel,
      buttonSubmit,
    } = getElements();

    expect(modalElement).toBeVisible();
    expect(formTag).toBeVisible();
    expect(inputName).toBeVisible();
    expect(inputSupportEmail).toBeVisible();
    expect(screen.getByText('Example: saint-laurent.fr')).toBeVisible();
    expect(buttonCancel).toBeVisible();
    expect(buttonSubmit).toBeVisible();
  });

  it('should disable submit button when no field is filled', () => {
    render(<ModalAddMailDomain />, { wrapper: AppWrapper });

    const { buttonSubmit } = getElements();

    expect(buttonSubmit).toBeDisabled();
  });

  it('displays validation error on empty submit', async () => {
    fetchMock.mock(`end:mail-domains/`, 201);

    const user = userEvent.setup();

    render(<ModalAddMailDomain />, { wrapper: AppWrapper });

    const { inputName, buttonSubmit } = getElements();

    await user.type(inputName, 'domain.fr');
    await user.clear(inputName);

    await user.click(buttonSubmit);

    await waitFor(() => {
      expect(
        screen.getByText(/Example: saint-laurent.fr/i),
      ).toBeInTheDocument();
    });

    expect(fetchMock.lastUrl()).toBeFalsy();
  });

  it('submits the form when validation passes', async () => {
    fetchMock.mock(`end:mail-domains/`, {
      status: 201,
      body: {
        name: 'domain.fr',
        id: '456ac6ca-0402-4615-8005-69bc1efde43f',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        slug: 'domainfr',
        status: 'enabled',
        abilities: {
          get: true,
          patch: true,
          put: true,
          post: true,
          delete: true,
          manage_accesses: true,
        },
      },
    });

    const user = userEvent.setup();

    render(<ModalAddMailDomain />, { wrapper: AppWrapper });

    const { inputName, inputSupportEmail, buttonSubmit } = getElements();

    await user.type(inputName, 'domain.fr');
    await user.type(inputSupportEmail, 'support@domain.fr');

    await user.click(buttonSubmit);

    expect(fetchMock.lastUrl()).toContain('/mail-domains/');
    expect(fetchMock.lastOptions()).toEqual({
      body: JSON.stringify({
        name: 'domain.fr',
        support_email: 'support@domain.fr',
      }),
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      method: 'POST',
    });

    expect(mockPush).toHaveBeenCalledWith(`/mail-domains/domainfr`);
  });

  it('displays right error message error when maildomain name is already used', async () => {
    fetchMock.mock(`end:mail-domains/`, {
      status: 400,
      body: {
        name: 'Mail domain with this name already exists.',
      },
    });

    const user = userEvent.setup();

    render(<ModalAddMailDomain />, { wrapper: AppWrapper });

    const { inputName, inputSupportEmail, buttonSubmit } = getElements();

    await user.type(inputName, 'domain.fr');
    await user.type(inputSupportEmail, 'support@domain.fr');
    await user.click(buttonSubmit);

    await waitFor(() => {
      expect(
        screen.getByText(
          /This mail domain is already used. Please, choose another one./i,
        ),
      ).toBeInTheDocument();
    });

    expect(inputName).toHaveFocus();

    await user.type(inputName, 'domain2.fr');

    expect(buttonSubmit).toBeEnabled();
  });

  it('displays right error message error when maildomain slug is already used', async () => {
    fetchMock.mock(`end:mail-domains/`, {
      status: 400,
      body: {
        name: 'Mail domain with this Slug already exists.',
      },
    });

    const user = userEvent.setup();

    render(<ModalAddMailDomain />, { wrapper: AppWrapper });

    const { inputName, inputSupportEmail, buttonSubmit } = getElements();

    await user.type(inputName, 'domainfr');
    await user.type(inputSupportEmail, 'support@domain.fr');

    await user.click(buttonSubmit);

    await waitFor(() => {
      expect(
        screen.getByText(
          /This mail domain is already used. Please, choose another one./i,
        ),
      ).toBeInTheDocument();
    });

    expect(inputName).toHaveFocus();

    await user.type(inputName, 'domain2fr');

    expect(buttonSubmit).toBeEnabled();
  });

  it('displays right error message error when error 500 is received', async () => {
    fetchMock.mock(`end:mail-domains/`, {
      status: 500,
    });

    const user = userEvent.setup();

    render(<ModalAddMailDomain />, { wrapper: AppWrapper });

    const { inputName, inputSupportEmail, buttonSubmit } = getElements();

    await user.type(inputName, 'domain.fr');
    await user.type(inputSupportEmail, 'support@domain.fr');

    await user.click(buttonSubmit);

    await waitFor(() => {
      expect(
        screen.getByText(
          'Your request cannot be processed because the server is experiencing an error. If the problem ' +
            'persists, please contact our support to resolve the issue: suiteterritoriale@anct.gouv.fr',
        ),
      ).toBeInTheDocument();
    });

    expect(inputName).toHaveFocus();
    expect(buttonSubmit).toBeEnabled();
  });
});
