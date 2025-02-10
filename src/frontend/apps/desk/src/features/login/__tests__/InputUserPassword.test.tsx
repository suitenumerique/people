import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { AppWrapper } from '@/tests/utils';

import { InputUserPassword } from '../components/InputUserPassword';

describe('InputUserPassword', () => {
  const mockSetPassword = jest.fn();
  const defaultProps = {
    label: 'Password',
    setPassword: mockSetPassword,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderInput = (props = defaultProps) => {
    render(<InputUserPassword {...props} />, { wrapper: AppWrapper });
  };

  it('renders the password input with correct label', () => {
    renderInput();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
  });

  it('calls setPassword when input value changes', async () => {
    renderInput();
    const input = screen.getByLabelText('Password');
    await userEvent.type(input, 'mypassword123');
    expect(mockSetPassword).toHaveBeenCalledWith('mypassword123');
  });

  it('has required attribute', () => {
    renderInput();
    const input = screen.getByLabelText('Password');
    expect(input).toHaveAttribute('required');
  });

  it('has correct type and autocomplete attributes', () => {
    renderInput();
    const input = screen.getByLabelText('Password');
    expect(input).toHaveAttribute('type', 'password');
    expect(input).toHaveAttribute('autocomplete', 'current-password');
  });
});
