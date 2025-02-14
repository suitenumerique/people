import { useCallback, useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Options } from 'react-select';
import AsyncSelect from 'react-select/async';

import { MailDomain } from '@/features/mail-domains/domains/types';
import { OptionSelect, OptionType } from '@/features/teams/member-add/types';
import { isValidEmail } from '@/utils';

import { useUsers } from '../api/useUsers';

export type OptionsSelect = Options<OptionSelect>;

interface SearchMembersProps {
  mailDomain: MailDomain;
  selectedMembers: OptionsSelect;
  setSelectedMembers: (value: OptionsSelect) => void;
  disabled?: boolean;
}

export const SearchMembers = ({
  mailDomain,
  selectedMembers,
  setSelectedMembers,
  disabled,
}: SearchMembersProps) => {
  const { t } = useTranslation();
  const [input, setInput] = useState('');
  const [userQuery, setUserQuery] = useState('');
  const resolveOptionsRef = useRef<((value: OptionsSelect) => void) | null>(
    null,
  );
  const { data } = useUsers({
    query: userQuery,
    mailDomain: mailDomain.slug,
  });

  const options = data?.results;

  useEffect(() => {
    if (!resolveOptionsRef.current || !options) {
      return;
    }

    const optionsFiltered = options.filter(
      (user) =>
        !selectedMembers?.find(
          (selectedUser) => selectedUser.value.email === user.email,
        ),
    );

    let users: OptionsSelect = optionsFiltered.map((user) => ({
      value: user,
      label: user.name || user.email,
      type: OptionType.NEW_MEMBER,
    }));

    if (userQuery && isValidEmail(userQuery)) {
      const isFoundUser = !!optionsFiltered.find(
        (user) => user.email === userQuery,
      );
      const isFoundEmail = !!selectedMembers.find(
        (selectedMember) => selectedMember.value.email === userQuery,
      );

      if (!isFoundUser && !isFoundEmail) {
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
  }, [options, selectedMembers]);

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
      isDisabled={disabled}
      aria-label={t('Find a member to add to the domain')}
      isMulti
      loadOptions={loadOptions}
      defaultOptions={[]}
      onInputChange={onInputChangeHandle}
      inputValue={input}
      placeholder={t(
        'Search for members to assign them a role (name or email)',
        {},
      )}
      noOptionsMessage={() =>
        t('Invite new members with roles', { name: mailDomain.name })
      }
      onChange={(value) => {
        setInput('');
        setUserQuery('');
        setSelectedMembers(value);
      }}
    />
  );
};
