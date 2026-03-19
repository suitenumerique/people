import {
  Button,
  ModalSize,
  VariantType,
  useToastProvider,
} from '@gouvfr-lasuite/cunningham-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { createGlobalStyle } from 'styled-components';

import { APIError } from '@/api';
import { Box, Text } from '@/components';
import { Modal } from '@/components/Modal';
import { useCunninghamTheme } from '@/cunningham';
import { ChooseRole } from '@/features/teams/member-management';
import { Role, Team } from '@/features/teams/team-management';

import { useCreateInvitation, useCreateTeamAccess } from '../api';
import IconAddMember from '../assets/add-member.svg';
import {
  OptionInvitation,
  OptionNewMember,
  OptionSelect,
  OptionType,
  isOptionNewMember,
} from '../types';

import { OptionsSelect, SearchMembers } from './SearchMembers';

const GlobalStyle = createGlobalStyle`
  .c__modal {
    overflow: visible;
  }
`;

type APIErrorMember = APIError<{
  value: string;
  type: OptionType;
}>;

interface ModalAddMembersProps {
  currentRole: Role;
  onClose: () => void;
  team: Team;
}

export const ModalAddMembers = ({
  currentRole,
  onClose,
  team,
}: ModalAddMembersProps) => {
  const { colorsTokens } = useCunninghamTheme();
  const { t } = useTranslation();
  const [selectedMembers, setSelectedMembers] = useState<OptionsSelect>([]);
  const [selectedRole, setSelectedRole] = useState<Role>(Role.MEMBER);
  const { toast } = useToastProvider();
  const { mutateAsync: createInvitation } = useCreateInvitation();
  const { mutateAsync: createTeamAccess } = useCreateTeamAccess();

  const [isPending, setIsPending] = useState<boolean>(false);

  const switchActions = (selectedMembers: OptionsSelect) =>
    selectedMembers.map(async (selectedMember) => {
      switch (selectedMember.type) {
        case OptionType.INVITATION:
          await createInvitation({
            email: selectedMember.value.email,
            role: selectedRole,
            teamId: team.id,
          });
          break;

        case OptionType.NEW_MEMBER:
          await createTeamAccess({
            name: selectedMember.value.name,
            role: selectedRole,
            teamId: team.id,
            userId: selectedMember.value.id,
          });
          break;
      }

      return selectedMember;
    });

  const toastOptions = {
    duration: 4000,
  };

  const onError = (dataError: APIErrorMember['data']) => {
    const messageError =
      dataError?.type === OptionType.INVITATION
        ? t(`Failed to create the invitation for {{email}}`, {
            email: dataError?.value,
          })
        : t(`Failed to add {{name}} in the team`, {
            name: dataError?.value,
          });

    toast(messageError, VariantType.ERROR, toastOptions);
  };

  const onSuccess = (option: OptionSelect) => {
    const message = !isOptionNewMember(option)
      ? t('Invitation sent to {{email}}', {
          email: option.value.email,
        })
      : t('Member {{name}} added to the team', {
          name: option.value.name,
        });

    toast(message, VariantType.SUCCESS, toastOptions);
  };

  const handleValidate = async () => {
    setIsPending(true);

    const settledPromises = await Promise.allSettled<
      OptionInvitation | OptionNewMember
    >(switchActions(selectedMembers));

    onClose();
    setIsPending(false);

    settledPromises.forEach((settledPromise) => {
      switch (settledPromise.status) {
        case 'rejected':
          onError((settledPromise.reason as APIErrorMember).data);
          break;

        case 'fulfilled':
          onSuccess(settledPromise.value);
          break;
      }
    });
  };

  return (
    <Modal
      isOpen
      leftActions={
        <Button
          color="neutral"
          variant="secondary"
          fullWidth
          onClick={onClose}
          disabled={isPending}
        >
          {t('Cancel')}
        </Button>
      }
      onClose={onClose}
      closeOnClickOutside
      hideCloseButton
      rightActions={
        <Button
          color="brand"
          fullWidth
          disabled={!selectedMembers.length || isPending}
          onClick={() => void handleValidate()}
        >
          {t('Add to group')}
        </Button>
      }
      size={ModalSize.MEDIUM}
      title={
        <Box $align="center" $gap="1rem">
          <IconAddMember
            width={48}
            color={colorsTokens()['brand-600']}
            aria-hidden="true"
          />
          <Text $size="h3" $margin="none">
            {t('Add a member')}
          </Text>
        </Box>
      }
    >
      <GlobalStyle />
      <Box $margin={{ bottom: 'xl', top: 'large' }}>
        <SearchMembers
          team={team}
          setSelectedMembers={setSelectedMembers}
          selectedMembers={selectedMembers}
          disabled={isPending}
        />
        {selectedMembers.length > 0 && (
          <Box $margin={{ top: 'small' }}>
            <Text as="h4" $textAlign="left" $margin={{ bottom: 'tiny' }}>
              {t('Choose a role')}
            </Text>
            <ChooseRole
              currentRole={currentRole}
              disabled={isPending}
              defaultRole={Role.MEMBER}
              setRole={setSelectedRole}
            />
          </Box>
        )}
      </Box>
    </Modal>
  );
};
