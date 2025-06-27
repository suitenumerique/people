import {
  Button,
  ModalSize,
  VariantType,
  useToastProvider,
} from '@openfun/cunningham-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { createGlobalStyle } from 'styled-components';

import { APIError } from '@/api';
import { Box, Text } from '@/components';
import { CustomModal } from '@/components/modal/CustomModal';
import { ChooseRole } from '@/features/teams/member-management';
import { Role, Team } from '@/features/teams/team-management';

import { useCreateInvitation, useCreateTeamAccess } from '../api';
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

  const step = 0;
  const steps = [
    {
      title: t('Add a member'),
      content: (
        <>
          <GlobalStyle />
          <Box
            $padding={{ horizontal: 'md', bottom: 'md' }}
            $margin={{ bottom: 'xl', top: 'large' }}
          >
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
        </>
      ),
      leftAction: (
        <Button
          color="secondary"
          fullWidth
          onClick={onClose}
          disabled={isPending}
        >
          {t('Cancel')}
        </Button>
      ),
      rightAction: (
        <Button
          color="primary"
          fullWidth
          disabled={!selectedMembers.length || isPending}
          onClick={() => void handleValidate()}
        >
          {t('Add to team')}
        </Button>
      ),
    },
  ];

  return (
    <CustomModal
      isOpen
      leftActions={steps[step].leftAction}
      rightActions={steps[step].rightAction}
      onClose={onClose}
      closeOnClickOutside
      hideCloseButton
      size={ModalSize.MEDIUM}
      title={steps[step].title}
      step={step}
      totalSteps={steps.length}
      closeOnEsc
    >
      {steps[step].content}
    </CustomModal>
  );
};
