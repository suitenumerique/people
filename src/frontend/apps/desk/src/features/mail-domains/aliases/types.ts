import { UUID } from 'crypto';

export interface Alias {
  id: UUID;
  local_part: string;
  destination: string;
}

export interface ViewAlias {
  id: string;
  email: string;
  local_part: string;
  destination: string;
  alias: Alias;
}

export interface AliasGroup {
  id: string;
  email: string;
  local_part: string;
  destinations: string[];
  destinationIds: Record<string, string>;
  count_destinations: number;
}
