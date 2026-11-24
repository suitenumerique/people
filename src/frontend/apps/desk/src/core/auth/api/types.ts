/**
 * Represents user retrieved from the API.
 * @interface User
 * @property {string} id - The id of the user.
 * @property {string} email - The email of the user.
 * @property {string} name - The name of the user.
 * @property {boolean} can_register_domains
 */
export interface User {
  id: string;
  email: string;
  name?: string;
  can_register_domains?: boolean;
  organization?: Organization;
  abilities?: {
    mailboxes: UserAbilities;
    contacts: UserAbilities;
  };
}

export interface Organization {
  id: string;
  name: string;
  registration_id_list: [string];
}

export type UserAbilities = {
  can_view?: boolean;
  can_create?: boolean;
};
