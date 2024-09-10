import { APIError } from '@/api';

import {
  parseAPIError,
  parseAPIErrorCause,
  parseServerAPIError,
} from '../parseAPIError';

describe('parseAPIError', () => {
  const handleErrorMock = jest.fn();
  const handleServerErrorMock = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should handle specific API error and return no unhandled causes', () => {
    const error = new APIError('client error', {
      cause: ['Mail domain with this name already exists.'],
      status: 400,
    });

    const result = parseAPIError({
      error,
      errorParams: [
        [
          ['Mail domain with this name already exists.'],
          'This domain already exists.',
          handleErrorMock,
        ],
      ],
      serverErrorParams: ['Server error', handleServerErrorMock],
    });

    expect(handleErrorMock).toHaveBeenCalled();
    expect(result).toEqual(['This domain already exists.']);
  });

  it('should return unhandled causes when no match is found', () => {
    const error = new APIError('client error', {
      cause: ['Unhandled error'],
      status: 400,
    });

    const result = parseAPIError({
      error,
      errorParams: [
        [
          ['Mail domain with this name already exists.'],
          'This domain already exists.',
          handleErrorMock,
        ],
      ],
      serverErrorParams: ['Server error', handleServerErrorMock],
    });

    expect(handleErrorMock).not.toHaveBeenCalled();
    expect(result).toEqual(['Unhandled error']);
  });

  it('should handle server errors correctly and prepend server error message', () => {
    const error = new APIError('server error', { status: 500 });

    const result = parseAPIError({
      error,
      errorParams: undefined,
      serverErrorParams: ['Server error occurred', handleServerErrorMock],
    });

    expect(handleServerErrorMock).toHaveBeenCalled();
    expect(result).toEqual(['Server error occurred']);
  });

  it('should handle absence of errors gracefully', () => {
    const result = parseAPIError({
      error: null,
      errorParams: [
        [
          ['Mail domain with this name already exists.'],
          'This domain already exists.',
          handleErrorMock,
        ],
      ],
      serverErrorParams: ['Server error', handleServerErrorMock],
    });

    expect(result).toBeUndefined();
  });
});

describe('parseAPIErrorCause', () => {
  it('should handle specific errors and call handleError', () => {
    const handleErrorMock = jest.fn();
    const causes = ['Mail domain with this name already exists.'];

    const errorParams: [string[], string, () => void][] = [
      [
        ['Mail domain with this name already exists.'],
        'This domain already exists.',
        handleErrorMock,
      ],
    ];

    const result = parseAPIErrorCause(
      new APIError('client error', { cause: causes, status: 400 }),
      errorParams,
    );

    expect(handleErrorMock).toHaveBeenCalled();
    expect(result).toEqual(['This domain already exists.']);
  });

  it('should handle multiple causes and return unhandled causes', () => {
    const handleErrorMock = jest.fn();
    const causes = [
      'Mail domain with this name already exists.',
      'Unhandled error',
    ];

    const errorParams: [string[], string, () => void][] = [
      [
        ['Mail domain with this name already exists.'],
        'This domain already exists.',
        handleErrorMock,
      ],
    ];

    const result = parseAPIErrorCause(
      new APIError('client error', { cause: causes, status: 400 }),
      errorParams,
    );

    expect(handleErrorMock).toHaveBeenCalled();
    expect(result).toEqual(['This domain already exists.', 'Unhandled error']);
  });
});

describe('parseServerAPIError', () => {
  const handleServerErrorMock = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should return the server error message and handle callback', () => {
    const result = parseServerAPIError(['Server error', handleServerErrorMock]);

    expect(result).toEqual('Server error');
    expect(handleServerErrorMock).toHaveBeenCalled();
  });

  it('should return only the server error message when no callback is provided', () => {
    const result = parseServerAPIError(['Server error', undefined]);

    expect(result).toEqual('Server error');
  });
});
