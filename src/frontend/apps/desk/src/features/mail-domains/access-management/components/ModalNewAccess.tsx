import {
  Button,
  ModalSize,
  VariantType,
  useToastProvider,
} from '@openfun/cunningham-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, TextErrors, Text } from '@/components';
import { Modal } from '@/components/Modal';
import { usePostMailDomainAccess } from '@/features/mail-domains/access-management';
import { useCreateInvitation } from '../api';
import { OptionsSelect, SearchMembers } from './SearchMembers';

import { MailDomain, Role } from '../../domains';
import { Access } from '../types';

import { ChooseRoleNewAccess } from './ChooseRoleNewAccess';

interface ModalNewAccessProps {
  mailDomain: MailDomain;
  currentRole: Role;
  onClose: () => void;
}

export enum OptionType {
  INVITATION = 'invitation',
  NEW_MEMBER = 'new_member',
}

export const ModalNewAccess = ({
  mailDomain,
  currentRole,
  onClose,
}: ModalNewAccessProps) => {
  const { t } = useTranslation();
  const { toast } = useToastProvider();
  const [selectedMembers, setSelectedMembers] = useState<OptionsSelect>([]);
  const [role, setRole] = useState<Role>(Role.VIEWER);
  const [isPending, setIsPending] = useState<boolean>(false);

  const createInvitation = useCreateInvitation();

  const { mutateAsync: postMailDomainAccess} = usePostMailDomainAccess();

  const onSuccess = (option: OptionSelect) => {
    console.log(option);
    const message = !isOptionNewMember(option)
      ? t('Invitation sent to {{email}}', {
          email: option.value.email,
        })
      : t('Member {{name}} added to the team', {
          name: option.value.name,
        });

    toast(message, VariantType.SUCCESS, toastOptions);
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

    toast(messageError, VariantType.ERROR);
  };

  const switchActions = (members: OptionsSelect) => {
    console.log(mailDomain, role);
    return members.map((member) => {
      if (member.type === OptionType.INVITATION) {
        return createInvitation.mutateAsync({ email: member.value, teamId: mailDomain.id });
      } else {
        return postMailDomainAccess({
          slug: mailDomain.slug,
          user: member.value.id,
          role: role
        });
      }
    });
  };

  const handleValidate = async () => {
    const settledPromises = await Promise.allSettled(switchActions(selectedMembers));

    onClose();

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
        <Button color="secondary" fullWidth onClick={onClose}>
          {t('Cancel')}
        </Button>
      }
      onClose={onClose}
      closeOnClickOutside
      hideCloseButton
      rightActions={
        <Button
          color="primary"
          fullWidth
          disabled={!selectedMembers.length || isPending}
          onClick={() => void handleValidate()}
        >
          {t('Add to domain')}
        </Button>
      }
      size={ModalSize.MEDIUM}
      title={
        <Box $align="center" $gap="1rem">
          <Text $size="h3" $margin="none">
            {t('Add a new access')}
          </Text>
        </Box>
      }
    >
      <Box $margin={{ bottom: 'xl', top: 'large' }}>
        <SearchMembers
          mailDomain={mailDomain}
          setSelectedMembers={setSelectedMembers}
          selectedMembers={selectedMembers}
        />
        {selectedMembers.length > 0 && (
          <Box $margin={{ top: 'small' }}>
            <Text as="h4" $textAlign="left" $margin={{ bottom: 'tiny' }}>
              {t('Choose a role')}
            </Text>
            <ChooseRoleNewAccess 
              defaultRole={Role.VIEWER} 
              disabled={false} 
              currentRole={Role.ADMIN} 
              setRole={setRole} 
            />
          </Box>
        )}
      </Box>
    </Modal>
  );
};
