export const baseApiUrl = (apiVersion: string = '1.0') => {
  const origin =
    process.env.NEXT_PUBLIC_API_ORIGIN ||
    (typeof window !== 'undefined' ? window.location.origin : '');

  return `${origin}/api/v${apiVersion}/`;
};
