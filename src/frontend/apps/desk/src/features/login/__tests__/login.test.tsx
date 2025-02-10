import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { AppWrapper } from '@/tests/utils';

import { LoginForm } from '../components/LoginForm';

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock('next/router', () => ({
  useRouter: jest.fn(),
}));

describe('LoginForm', () => {
  const mockHandleSubmit = jest.fn((e) => e.preventDefault());
  const mockSetEmail = jest.fn();
  const mockSetPassword = jest.fn();

  const defaultProps = {
    title: 'Login',
    labelEmail: 'Email',
    labelPassword: 'Password',
    labelSignIn: 'Sign In',
    email: '',
    setEmail: mockSetEmail,
    setPassword: mockSetPassword,
    error: '',
    handleSubmit: mockHandleSubmit,
    blockingError: '',
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderLoginForm = () => {
    render(<LoginForm {...defaultProps} />, { wrapper: AppWrapper });
  };

  it('should render the login form', async () => {
    renderLoginForm();

    await waitFor(() => {
      expect(screen.getByText('Login')).toBeInTheDocument();
    });

    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByText('Sign In')).toBeInTheDocument();
  });

  it('should handle email input', async () => {
    renderLoginForm();

    await waitFor(() => {
      expect(screen.getByLabelText('Email')).toBeInTheDocument();
    });

    const emailInput = screen.getByLabelText('Email');
    await userEvent.type(emailInput, 'test@example.com');

    expect(mockSetEmail).toHaveBeenCalledWith('test@example.com');
  });

  it('should handle password input', async () => {
    renderLoginForm();

    await waitFor(() => {
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
    });

    const passwordInput = screen.getByLabelText('Password');
    await userEvent.type(passwordInput, 'password123');

    expect(mockSetPassword).toHaveBeenCalledWith('password123');
  });

  it('should submit the form', async () => {
    renderLoginForm();

    await waitFor(() => {
      expect(screen.getByText('Sign In')).toBeInTheDocument();
    });

    const form = screen.getByTestId('login-form');
    fireEvent.submit(form);

    expect(mockHandleSubmit).toHaveBeenCalled();
  });

  it('should display error message when provided', async () => {
    const errorMessage = 'Invalid credentials';
    render(<LoginForm {...defaultProps} error={errorMessage} />, {
      wrapper: AppWrapper,
    });

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('should display blocking error and hide form when provided', async () => {
    const blockingError = 'Service unavailable';
    render(<LoginForm {...defaultProps} blockingError={blockingError} />, {
      wrapper: AppWrapper,
    });

    await waitFor(() => {
      expect(screen.getByText(blockingError)).toBeInTheDocument();
    });

    expect(screen.queryByLabelText('Email')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Password')).not.toBeInTheDocument();
  });
});
