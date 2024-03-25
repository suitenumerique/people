import { useCallback, useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Options } from 'react-select';
import AsyncSelect from 'react-select/async';

import { Team } from '@/features/teams';
import { isValidEmail } from '@/utils';

import { KEY_LIST_USER, useUsers } from '../api/useUsers';
import { OptionSelect, OptionType } from '../types';

export type OptionsSelect = Options<OptionSelect>;

interface SearchMembersProps {
  team: Team;
  setSelectedMembers: (value: OptionsSelect) => void;
}

export const SearchMembers = ({
  team,
  setSelectedMembers,
}: SearchMembersProps) => {
  const { t } = useTranslation();
  const [input, setInput] = useState('');
  const [userQuery, setUserQuery] = useState('');
  const resolveOptionsRef = useRef<((value: OptionsSelect) => void) | null>(
    null,
  );
  const { data } = useUsers(
    { query: userQuery },
    {
      enabled: !!userQuery,
      queryKey: [KEY_LIST_USER, { query: userQuery }],
    },
  );

  const options = data?.results;

  useEffect(() => {
    if (!resolveOptionsRef.current || !options) {
      return;
    }

    let users: OptionsSelect = options.map((user) => ({
      value: user,
      label: user.name || user.email,
      type: OptionType.NEW_MEMBER,
    }));

    if (userQuery && isValidEmail(userQuery)) {
      const isFound = !!options.find((user) => user.email === userQuery);

      if (!isFound) {
        users = [
          {
            value: { email: userQuery },
            label: userQuery,
            type: OptionType.INVITATION,
          },
        ];
      }
    }

    resolveOptionsRef.current(users);
    resolveOptionsRef.current = null;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [options]);

  const loadOptions = (): Promise<OptionsSelect> => {
    return new Promise<OptionsSelect>((resolve) => {
      resolveOptionsRef.current = resolve;
    });
  };

  const timeout = useRef<NodeJS.Timeout | null>(null);
  const onInputChangeHandle = useCallback((newValue: string) => {
    setInput(newValue);
    if (timeout.current) {
      clearTimeout(timeout.current);
    }

    timeout.current = setTimeout(() => {
      setUserQuery(newValue);
    }, 1000);
  }, []);

  return (
    <AsyncSelect
      aria-label={t('Find a member to add to the team')}
      isMulti
      loadOptions={loadOptions}
      defaultOptions={[]}
      onInputChange={onInputChangeHandle}
      inputValue={input}
      placeholder={t('Search new members (name or email)')}
      noOptionsMessage={() =>
        t('Invite new members to {{teamName}}', { teamName: team.name })
      }
      onChange={(value) => {
        setInput('');
        setUserQuery('');
        setSelectedMembers(value);
      }}
    />
  );
};
