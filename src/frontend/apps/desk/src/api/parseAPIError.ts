import { APIError } from '@/api/index';

type ErrorCallback = () => void;

// Type for the error tuple format [causes, message, handleError]
type ErrorTuple = [string[], string, ErrorCallback | undefined];

// Server error tuple [defaultMessage, handleError]
type ServerErrorTuple = [string, ErrorCallback | undefined];

/**
 * @function parseAPIError
 * @description function to centralize APIError handling to treat discovered errors
 * and error type 500 with default behavior using a simplified tuple structure.
 * @param error - APIError object
 * @param errorParams - Array of tuples: each contains an array of causes, a message, and an optional callback function.
 * @param serverErrorParams - A tuple for server error handling: [defaultMessage, handleError]
 * @returns Array of error messages or undefined
 */
export const parseAPIError = ({
  error,
  errorParams,
  serverErrorParams,
}: {
  error: APIError | null;
  errorParams?: ErrorTuple[];
  serverErrorParams?: ServerErrorTuple;
}): string[] | undefined => {
  if (!error) {
    return;
  }

  // Parse known error causes using the tuple structure
  const errorCauses =
    error.cause?.length && errorParams
      ? parseAPIErrorCause(error, errorParams)
      : undefined;

  // Check if it's a server error (500) and handle that case
  const serverErrorCause =
    (error?.status === 500 || !error?.status) && serverErrorParams
      ? parseServerAPIError(serverErrorParams)
      : undefined;

  // Combine the causes and return
  const causes: string[] = errorCauses ? [...errorCauses] : [];
  if (serverErrorCause) {
    causes.unshift(serverErrorCause);
  }

  return causes.length ? causes : undefined;
};

/**
 * @function parseAPIErrorCause
 * @description Processes known API error causes using the tuple structure.
 * @param error - APIError object
 * @param errorParams - Array of tuples: each contains an array of causes, a message, and an optional callback function.
 * @returns Array of error messages
 */
export const parseAPIErrorCause = (
  error: APIError,
  errorParams: ErrorTuple[],
): string[] | undefined => {
  if (!error.cause) {
    return;
  }

  return error.cause.reduce((causes: string[], cause: string) => {
    // Find the matching error tuple
    const matchedError = errorParams.find(([errorCauses]) =>
      errorCauses.some((knownCause) => new RegExp(knownCause, 'i').test(cause)),
    );

    if (matchedError) {
      const [, message, handleError] = matchedError;
      causes.push(message);

      if (handleError) {
        handleError();
      }
    } else {
      // If no match is found, add the original cause
      causes.push(cause);
    }

    return causes;
  }, []);
};

/**
 * @function parseServerAPIError
 * @description Handles server errors (500) and adds the default message.
 * @param serverErrorParams - Tuple [defaultMessage, handleError]
 * @returns Server error message
 */
export const parseServerAPIError = ([
  defaultMessage,
  handleError,
]: ServerErrorTuple): string => {
  if (handleError) {
    handleError();
  }

  return defaultMessage;
};
