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
      errorParams: {
        name: {
          causes: ['Mail domain with this name already exists.'],
          handleError: handleErrorMock,
        },
      },
      serverErrorParams: {
        defaultMessage: 'Server error',
        handleError: handleServerErrorMock,
      },
    });

    expect(handleErrorMock).toHaveBeenCalled();
    expect(result).toEqual([]);
  });

  it('should return unhandled causes when no match is found', () => {
    const error = new APIError('client error', {
      cause: ['Unhandled error'],
      status: 400,
    });

    const result = parseAPIError({
      error,
      errorParams: {
        name: {
          causes: ['Mail domain with this name already exists.'],
          handleError: handleErrorMock,
        },
      },
      serverErrorParams: {
        defaultMessage: 'Server error',
        handleError: handleServerErrorMock,
      },
    });

    expect(handleErrorMock).not.toHaveBeenCalled();
    expect(result).toEqual(['Unhandled error']);
  });

  it('should handle server errors correctly and prepend server error message', () => {
    const error = new APIError('server error', { status: 500 });

    const result = parseAPIError({
      error,
      errorParams: undefined,
      serverErrorParams: {
        defaultMessage: 'Server error occurred',
        handleError: handleServerErrorMock,
      },
    });

    expect(handleServerErrorMock).toHaveBeenCalled();
    expect(result).toEqual(['Server error occurred']);
  });

  it('should handle absence of errors gracefully', () => {
    const result = parseAPIError({
      error: null,
      errorParams: {
        name: {
          causes: ['Mail domain with this name already exists.'],
          handleError: handleErrorMock,
        },
      },
      serverErrorParams: {
        defaultMessage: 'Server error',
        handleError: handleServerErrorMock,
      },
    });

    expect(result).toBeUndefined();
  });
});

describe('parseAPIErrorCause', () => {
  it('should handle specific errors and call handleError', () => {
    const handleErrorMock = jest.fn();
    const causes = ['Mail domain with this name already exists.'];

    const errorParams = {
      name: {
        causes: ['Mail domain with this name already exists.'],
        handleError: handleErrorMock,
      },
    };

    const result = parseAPIErrorCause({ causes, errorParams });

    expect(handleErrorMock).toHaveBeenCalled();
    expect(result).toEqual([]);
  });

  it('should handle multiple causes and return unhandled causes', () => {
    const handleErrorMock = jest.fn();
    const causes = [
      'Mail domain with this name already exists.',
      'Unhandled error',
    ];

    const errorParams = {
      name: {
        causes: ['Mail domain with this name already exists.'],
        handleError: handleErrorMock,
      },
    };

    const result = parseAPIErrorCause({ causes, errorParams });

    expect(handleErrorMock).toHaveBeenCalled();
    expect(result).toEqual(['Unhandled error']);
  });
});

describe('parseServerAPIError', () => {
  it('should prepend the server error message when there are other causes', () => {
    const causes = ['Some other error'];
    const serverErrorParams = {
      defaultMessage: 'Server error',
    };

    const result = parseServerAPIError({ causes, serverErrorParams });

    expect(result).toEqual(['Server error', 'Some other error']);
  });

  it('should only return server error message when no other causes exist', () => {
    const causes: string[] = [];
    const serverErrorParams = {
      defaultMessage: 'Server error',
    };

    const result = parseServerAPIError({ causes, serverErrorParams });

    expect(result).toEqual(['Server error']);
  });

  it('should call handleError when provided as a param', () => {
    const handleErrorMock = jest.fn();
    const causes: string[] = [];
    const serverErrorParams = {
      defaultMessage: 'Server error',
      handleError: handleErrorMock,
    };

    parseServerAPIError({ causes, serverErrorParams });

    expect(handleErrorMock).toHaveBeenCalled();
  });
});
