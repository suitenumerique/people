import {
  Button,
  ModalSize,
  VariantType,
  useToastProvider,
} from '@openfun/cunningham-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { APIError } from '@/api';
import { Box, Text } from '@/components';
import { Modal } from '@/components/Modal';
import { useCreateMailDomainAccess } from '@/features/mail-domains/access-management';
import { useCreateInvitation } from '@/features/mail-domains/access-management/api';
import {
  OptionSelect,
  OptionType,
  isOptionNewMember,
} from '@/features/teams/member-add/types';

import { MailDomain, Role } from '../../domains';

import { AccessesList } from './AccessesList';
import { ChooseRole } from './ChooseRole';
import { OptionsSelect, SearchMembers } from './SearchMembers';

interface ModalDomainAccessesManagementProps {
  mailDomain: MailDomain;
  currentRole: Role;
  onClose: () => void;
}

type APIErrorMember = APIError<{
  value: string;
  type: OptionType;
}>;

export const ModalDomainAccessesManagement = ({
  mailDomain,
  currentRole,
  onClose,
}: ModalDomainAccessesManagementProps) => {
  const { t } = useTranslation();
  const { toast } = useToastProvider();
  const [selectedMembers, setSelectedMembers] = useState<OptionsSelect>([]);
  const [role, setRole] = useState<Role>(Role.VIEWER);

  const createInvitation = useCreateInvitation();
  const { mutateAsync: createMailDomainAccess } = useCreateMailDomainAccess();

  const onSuccess = (option: OptionSelect) => {
    const message = !isOptionNewMember(option)
      ? t('Invitation sent to {{email}}', {
          email: option.value.email,
        })
      : t('Access added to {{name}}', {
          name: option.value.name,
        });

    toast(message, VariantType.SUCCESS);
  };

  const onError = (dataError: APIErrorMember['data']) => {
    const messageError =
      dataError?.type === OptionType.INVITATION
        ? t('Failed to create the invitation')
        : t('Failed to add access');
    toast(messageError, VariantType.ERROR);
  };

  const switchActions = (selectedMembers: OptionsSelect) =>
    selectedMembers.map(async (selectedMember) => {
      switch (selectedMember.type) {
        case OptionType.INVITATION:
          await createInvitation.mutateAsync({
            email: selectedMember.value.email,
            mailDomainSlug: mailDomain.slug,
            role,
          });
          break;

        default:
          await createMailDomainAccess({
            slug: mailDomain.slug,
            user: selectedMember.value.id,
            role,
          });
          break;
      }

      return selectedMember;
    });

  const handleValidate = async () => {
    const settledPromises = await Promise.allSettled(
      switchActions(selectedMembers),
    );

    let hasInvitation = false;
    let hasError = false;

    settledPromises.forEach((settledPromise) => {
      switch (settledPromise.status) {
        case 'rejected':
          onError((settledPromise.reason as APIErrorMember).data);
          hasError = true;
          break;

        case 'fulfilled':
          const option = settledPromise.value;
          onSuccess(option);
          if (!isOptionNewMember(option)) {
            hasInvitation = true;
          }
          break;
      }
    });

    if (hasInvitation && !hasError) {
      setSelectedMembers([]);
      setRole(Role.VIEWER);
    } else if (!hasInvitation) {
      onClose();
    }
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
      size={ModalSize.MEDIUM}
      title={
        <Box $align="left" $gap="1rem">
          <Text $size="small" $margin="none">
            {t('Administration rights of {{name}}', {
              name: mailDomain.name,
            })}
          </Text>
        </Box>
      }
    >
      <Box
        $margin={{ bottom: 'base', top: 'base' }}
        $padding={{ horizontal: 'md' }}
      >
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
            <ChooseRole
              roleAccess={currentRole}
              disabled={false}
              availableRoles={[Role.VIEWER, Role.ADMIN, Role.OWNER]}
              currentRole={currentRole}
              setRole={setRole}
            />
            <Box $align="end">
              <Button
                color="primary"
                size="medium"
                disabled={!selectedMembers.length}
                onClick={() => void handleValidate()}
              >
                {t('OK')}
              </Button>
            </Box>
          </Box>
        )}
      </Box>
      <AccessesList mailDomain={mailDomain} currentRole={currentRole} />
    </Modal>
  );
};
