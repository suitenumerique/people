import { fetchAPI } from '@/api';

/**
 * Represents user data retrieved from the API.
 * This interface is incomplete, and will be
 * refactored in a near future.
 *
 * @interface UserData
 * @property {string} email - The email of the user.
 */
export interface UserData {
  email: string;
}

/**
 * Asynchronously retrieves the current user's data from the API.
 * This function is called during frontend initialization to check
 * the user's authentication status through a session cookie.
 *
 * @async
 * @function getMe
 * @throws {Error} Throws an error if the API request fails.
 * @returns {Promise<UserData>} A promise that resolves to the user data.
 */
export const getMe = async (): Promise<UserData> => {
  const response = await fetchAPI(`users/me/`);
  if (!response.ok) {
    throw new Error(`Couldn't fetch user data: ${response.statusText}`);
  }
  return response.json() as Promise<UserData>;
};
