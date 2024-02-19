interface IAPIError {
  status: number;
  cause?: string[];
}

export class APIError extends Error implements IAPIError {
  public status: number;
  public cause?: string[];

  constructor(message: string, { status, cause }: IAPIError) {
    super(message);

    this.name = 'APIError';
    this.status = status;
    this.cause = cause;
  }
}
