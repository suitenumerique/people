import { useCallback, useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { InputText, Select } from '@openfun/cunningham-react';

import { MailDomain } from '@/features/mail-domains/domains/types';
import { OptionSelect, OptionType } from '@/features/teams/member-add/types';
import { isValidEmail } from '@/utils';
import { useUsers } from '../api/useUsers';

interface SearchMembersProps {
  mailDomain: MailDomain;
  selectedMembers: OptionSelect[];
  setSelectedMembers: (value: OptionSelect[]) => void;
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
  const [options, setOptions] = useState<OptionSelect[]>([]);
  const timeout = useRef<NodeJS.Timeout | null>(null);

  const { data: usersData } = useUsers({
    query: input,
    mailDomain: mailDomain.slug,
  });

  const handleChange = (newValue: OptionSelect[]) => {
    setSelectedMembers(newValue);
  };

  const onInputChange = useCallback((value: string) => {
    setInput(value);
    if (timeout.current) clearTimeout(timeout.current);
    timeout.current = setTimeout(() => {
      // le hook useUsers va se mettre à jour automatiquement avec `input`
    }, 400);
  }, []);

  useEffect(() => {
    if (!usersData) return;

    const filtered = usersData.filter(
      (user) => !selectedMembers.find((s) => s.value.email === user.email)
    );

    let formatted: OptionSelect[] = filtered.map((user) => ({
      value: user,
      label: user.name || user.email,
      type: OptionType.NEW_MEMBER,
    }));

    if (input && isValidEmail(input)) {
      const alreadyListed = formatted.find((u) => u.value.email === input);
      const alreadySelected = selectedMembers.find((s) => s.value.email === input);

      if (!alreadyListed && !alreadySelected) {
        formatted.push({
          value: { email: input },
          label: input,
          type: OptionType.INVITATION,
        });
      }
    }

    setOptions(formatted);
  }, [usersData, input, selectedMembers]);

  return (
    <div className="flex flex-col gap-4">
      <InputText
        value={input}
        onChange={(e) => onInputChange(e.target.value)}
        placeholder={t('Search for members (name or email)')}
        label={t('Search a member')}
        disabled={disabled}
      />

      <Select
        isMulti
        isDisabled={disabled}
        options={options}
        value={selectedMembers}
        onChange={handleChange}
        placeholder={t('Select members')}
        noOptionsMessage={() =>
          t('Invite new members with roles', { name: mailDomain.name })
        }
      />
    </div>
  );
};
