import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { AppWrapper } from '@/tests/utils';

import { InputUserEmail } from '../components/InputUserEmail';

describe('InputUserEmail', () => {
  const mockSetEmail = jest.fn();
  const defaultProps = {
    label: 'Email Address',
    email: '',
    setEmail: mockSetEmail,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderInput = (props = defaultProps) => {
    render(<InputUserEmail {...props} />, { wrapper: AppWrapper });
  };

  it('renders the email input with correct label', () => {
    renderInput();
    expect(screen.getByLabelText('Email Address')).toBeInTheDocument();
  });

  it('calls setEmail when input value changes', async () => {
    renderInput();
    const input = screen.getByLabelText('Email Address');
    await userEvent.type(input, 'test@example.com');
    expect(mockSetEmail).toHaveBeenCalledWith('test@example.com');
  });

  it('displays the current email value', () => {
    renderInput({ ...defaultProps, email: 'test@example.com' });
    const input: HTMLInputElement = screen.getByLabelText('Email Address');
    expect(input.value).toBe('test@example.com');
  });

  it('has required attribute', () => {
    renderInput();
    const input = screen.getByLabelText('Email Address');
    expect(input).toHaveAttribute('required');
  });

  it('has correct type and autocomplete attributes', () => {
    renderInput();
    const input = screen.getByLabelText('Email Address');
    expect(input).toHaveAttribute('type', 'email');
    expect(input).toHaveAttribute('autocomplete', 'username');
  });
});
