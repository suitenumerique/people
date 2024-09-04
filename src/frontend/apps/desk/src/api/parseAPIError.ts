import { APIError } from '@/api/index';

type ErrorParams = {
  [fieldName: string]: {
    causes: string[];
    causeShown?: string;
    handleError: () => void;
  };
};

type ServerErrorParams = {
  defaultMessage: string;
  handleError?: () => void;
};

export type parseAPIErrorParams = {
  error: APIError | null;
  errorParams?: ErrorParams;
  serverErrorParams: ServerErrorParams;
};
export const parseAPIError = ({
  error,
  errorParams,
  serverErrorParams,
}: parseAPIErrorParams) => {
  if (!error || !serverErrorParams?.defaultMessage) {
    return;
  }

  let causes: string[] =
    error.cause?.length && errorParams
      ? parseAPIErrorCause({ causes: error.cause, errorParams })
      : [];

  if (error?.status === 500 || !error?.status) {
    causes = parseServerAPIError({ causes, serverErrorParams });
  }

  return causes;
};

export const parseAPIErrorCause = ({
  causes,
  errorParams,
}: {
  causes: string[];
  errorParams: ErrorParams;
}): string[] =>
  causes.reduce((arrayCauses, cause) => {
    const foundErrorParams = Object.values(errorParams).find((params) =>
      params.causes.find((knownCause) =>
        new RegExp(knownCause, 'i').test(cause),
      ),
    );

    if (!foundErrorParams) {
      arrayCauses.push(cause);
    }

    if (foundErrorParams?.causeShown) {
      arrayCauses.push(foundErrorParams.causeShown);
    }

    if (typeof foundErrorParams?.handleError === 'function') {
      foundErrorParams.handleError();
    }

    return arrayCauses;
  }, [] as string[]);

export const parseServerAPIError = ({
  causes,
  serverErrorParams,
}: {
  causes: string[];
  serverErrorParams: ServerErrorParams;
}): string[] => {
  causes.unshift(serverErrorParams.defaultMessage);

  if (typeof serverErrorParams?.handleError === 'function') {
    serverErrorParams.handleError();
  }

  return causes;
};
