import { useMutation } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import fetchMock from 'fetch-mock';
import React from 'react';

import { APIError } from '@/api';
import { AppWrapper } from '@/tests/utils';

import { CreateMailboxParams } from '../../api';
import { MailDomain } from '../../types';
import { ModalCreateMailbox } from '../ModalCreateMailbox';

const mockMailDomain: MailDomain = {
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
};

const mockOnSuccess = jest.fn();
jest.mock('../../api/useCreateMailbox', () => {
  const { createMailbox } = jest.requireActual('../../api/useCreateMailbox');

  return {
    useCreateMailbox: jest.fn().mockImplementation(({ onError }) =>
      useMutation<void, APIError, CreateMailboxParams>({
        mutationFn: createMailbox,
        onSuccess: mockOnSuccess,
        onError: (error) => onError(error),
      }),
    ),
  };
});

describe('ModalCreateMailbox', () => {
  const mockCloseModal = jest.fn();
  const renderModalCreateMailbox = () => {
    return render(
      <ModalCreateMailbox
        mailDomain={mockMailDomain}
        closeModal={mockCloseModal}
      />,
      { wrapper: AppWrapper },
    );
  };

  const getFormElements = () => ({
    formTag: screen.getByTitle('Mailbox creation form'),
    inputFirstName: screen.getByLabelText(/First name/i),
    inputLastName: screen.getByLabelText(/Last name/i),
    inputLocalPart: screen.getByLabelText(/Email address prefix/i),
    inputEmailAddress: screen.getByLabelText(/Secondary email address/i),
    buttonCancel: screen.getByRole('button', { name: /Cancel/i, hidden: true }),
    buttonSubmit: screen.getByRole('button', {
      name: /Create the mailbox/i,
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
    renderModalCreateMailbox();
    const {
      formTag,
      inputFirstName,
      inputLastName,
      inputLocalPart,
      inputEmailAddress,
      buttonCancel,
      buttonSubmit,
    } = getFormElements();

    expect(formTag).toBeVisible();
    expect(inputFirstName).toBeVisible();
    expect(inputLastName).toBeVisible();
    expect(inputLocalPart).toBeVisible();
    expect(screen.getByText(`@${mockMailDomain.name}`)).toBeVisible();
    expect(inputEmailAddress).toBeVisible();
    expect(buttonCancel).toBeVisible();
    expect(buttonSubmit).toBeVisible();
  });

  it('clicking on cancel button closes modal', async () => {
    const user = userEvent.setup();

    renderModalCreateMailbox();

    const { buttonCancel } = getFormElements();

    expect(buttonCancel).toBeVisible();

    await user.click(buttonCancel);

    expect(mockCloseModal).toHaveBeenCalled();
  });

  it('displays validation errors on empty submit', async () => {
    const user = userEvent.setup();

    renderModalCreateMailbox();

    const {
      inputFirstName,
      inputLastName,
      inputLocalPart,
      inputEmailAddress,
      buttonSubmit,
    } = getFormElements();

    // To bypass html form validation we need to fill and clear the fields
    await user.type(inputFirstName, 'John');
    await user.type(inputLastName, 'Doe');
    await user.type(inputLocalPart, 'john.doe');
    await user.type(inputEmailAddress, 'john.doe@mail.com');

    await user.clear(inputFirstName);
    await user.clear(inputLastName);
    await user.clear(inputLocalPart);
    await user.clear(inputEmailAddress);

    await user.click(buttonSubmit);

    expect(screen.getByText(`@${mockMailDomain.name}`)).toBeVisible();

    await waitFor(() => {
      expect(
        screen.getByText(/Please enter your first name/i),
      ).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(
        screen.getByText(/Please enter your last name/i),
      ).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(
        screen.getByText(/You must have minimum 1 character/i),
      ).toBeInTheDocument();
    });

    expect(fetchMock.lastUrl()).toBeFalsy();
    expect(buttonSubmit).toBeDisabled();
  });

  it('submits the form when validation passes', async () => {
    fetchMock.mock(`end:mail-domains/${mockMailDomain.slug}/mailboxes/`, 201);

    const user = userEvent.setup();

    renderModalCreateMailbox();

    const {
      inputFirstName,
      inputLastName,
      inputLocalPart,
      inputEmailAddress,
      buttonSubmit,
    } = getFormElements();

    await user.type(inputFirstName, 'John');
    await user.type(inputLastName, 'Doe');
    await user.type(inputLocalPart, 'john.doe');
    await user.type(inputEmailAddress, 'john.doe@mail.com');

    await user.click(buttonSubmit);

    await waitFor(() => {
      expect(
        screen.queryByText(/Please enter your first name/i),
      ).not.toBeInTheDocument();
    });
    await waitFor(() => {
      expect(
        screen.queryByText(/Please enter your last name/i),
      ).not.toBeInTheDocument();
    });

    await waitFor(() => {
      expect(
        screen.queryByText(/You must have minimum 1 character/i),
      ).not.toBeInTheDocument();
    });

    expect(fetchMock.lastOptions()).toEqual({
      body: JSON.stringify({
        first_name: 'John',
        last_name: 'Doe',
        local_part: 'john.doe',
        secondary_email: 'john.doe@mail.com',
      }),
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      method: 'POST',
    });

    expect(mockOnSuccess).toHaveBeenCalled();
  });

  it('submits the form on key enter press', async () => {
    fetchMock.mock(`end:mail-domains/${mockMailDomain.slug}/mailboxes/`, 201);
    const user = userEvent.setup();

    renderModalCreateMailbox();

    const {
      inputFirstName,
      inputLastName,
      inputLocalPart,
      inputEmailAddress,
      buttonSubmit,
    } = getFormElements();

    await user.type(inputFirstName, 'John');
    await user.type(inputLastName, 'Doe');
    await user.type(inputLocalPart, 'john.doe');

    await user.type(inputEmailAddress, 'john.doe@mail.com');

    await user.type(buttonSubmit, '{enter}');

    expect(fetchMock.lastOptions()).toEqual({
      body: JSON.stringify({
        first_name: 'John',
        last_name: 'Doe',
        local_part: 'john.doe',
        secondary_email: 'john.doe@mail.com',
      }),
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      method: 'POST',
    });

    expect(mockOnSuccess).toHaveBeenCalled();
  });

  it('displays right error message error when mailbox prefix is already used', async () => {
    // mockCreateMailbox.mockRejectedValueOnce(
    //   new APIError('Failed to create the mailbox', {
    //     status: 400,
    //     cause: ['Mailbox with this Local_part and Domain already exists.'],
    //   }),
    // );
    fetchMock.mock(`end:mail-domains/${mockMailDomain.slug}/mailboxes/`, {
      status: 400,
      body: {
        local_part: 'Mailbox with this Local_part and Domain already exists.',
      },
    });

    const user = userEvent.setup();

    renderModalCreateMailbox();

    const {
      inputFirstName,
      inputLastName,
      inputLocalPart,
      inputEmailAddress,
      buttonSubmit,
    } = getFormElements();

    await user.type(inputFirstName, 'John');
    await user.type(inputLastName, 'Doe');
    await user.type(inputLocalPart, 'john.doe');
    await user.type(inputEmailAddress, 'john.doe@mail.com');

    await user.click(buttonSubmit);

    await waitFor(() => {
      expect(
        screen.getByText(/This email prefix is already used./i),
      ).toBeInTheDocument();
    });

    expect(inputLocalPart).toHaveFocus();
  });

  it('displays right error message error when error 500 is received', async () => {
    fetchMock.mock(`end:mail-domains/${mockMailDomain.slug}/mailboxes/`, {
      status: 500,
    });

    const user = userEvent.setup();

    renderModalCreateMailbox();

    const {
      inputFirstName,
      inputLastName,
      inputLocalPart,
      inputEmailAddress,
      buttonSubmit,
    } = getFormElements();

    await user.type(inputFirstName, 'John');
    await user.type(inputLastName, 'Doe');
    await user.type(inputLocalPart, 'john.doe');
    await user.type(inputEmailAddress, 'john.doe@mail.com');

    await user.click(buttonSubmit);

    await waitFor(() => {
      expect(
        screen.getByText(
          'Your request cannot be processed because the server is experiencing an error. If the problem ' +
            'persists, please contact our support to resolve the issue: suiteterritoriale@anct.gouv.fr',
        ),
      ).toBeInTheDocument();
    });

    expect(inputFirstName).toHaveFocus();
    expect(buttonSubmit).toBeEnabled();
  });
});
