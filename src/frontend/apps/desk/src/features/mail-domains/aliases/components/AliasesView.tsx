import {
  Button,
  Input,
  Tooltip,
} from '@openfun/cunningham-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Text } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import { ModalCreateAlias } from '@/features/mail-domains/aliases/components';
import { AliasesListView } from '@/features/mail-domains/aliases/components/panel';

import { MailDomain } from '../../domains/types';

export function AliasesView({ mailDomain }: { mailDomain: MailDomain }) {
  const [searchValue, setSearchValue] = useState('');

  const [isCreateAliasFormVisible, setIsCreateAliasFormVisible] =
    useState(false);

  const { t } = useTranslation();

  const { colorsTokens } = useCunninghamTheme();
  const colors = colorsTokens();

  const canCreateAlias =
    mailDomain.status === 'enabled' || mailDomain.status === 'pending';

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchValue(event.target.value);
  };

  const clearInput = () => {
    setSearchValue('');
  };

  const openModal = () => {
    setIsCreateAliasFormVisible(true);
  };

  return (
    <>
      <div aria-label="Aliases panel" className="container">
        <h3 style={{ fontWeight: 700, fontSize: '18px', marginBottom: 'base' }}>
          {t('Aliases')}
        </h3>
        <div
          className="sm:block md:flex"
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px',
            gap: '1em',
          }}
        >
          <div
            style={{ width: 'calc(100% - 245px)' }}
            className="c__input__wrapper__mobile"
          >
            <Input
              style={{ width: '100%' }}
              label={t('Search for an alias')}
              icon={<span className="material-icons">search</span>}
              rightIcon={
                searchValue && (
                  <span
                    className="material-icons"
                    onClick={clearInput}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        clearInput();
                      }
                    }}
                    role="button"
                    tabIndex={0}
                    style={{ cursor: 'pointer' }}
                  >
                    close
                  </span>
                )
              }
              value={searchValue}
              onChange={handleInputChange}
            />
          </div>

          <div
            className="hidden md:flex"
            style={{
              background: colors['greyscale-200'],
              height: '32px',
              width: '1px',
            }}
          ></div>

          <div
            className="block md:hidden"
            style={{ marginBottom: '10px' }}
          ></div>

          <div>
            {mailDomain?.abilities.post ? (
              <Button
                data-testid="button-new-alias"
                aria-label={t('Create an alias in {{name}} domain', {
                  name: mailDomain?.name,
                })}
                disabled={!canCreateAlias}
                onClick={() => setIsCreateAliasFormVisible(true)}
              >
                {t('New alias')}
              </Button>
            ) : (
              <Tooltip content={t("You don't have the correct access right")}>
                <div>
                  <Button
                    data-testid="button-new-alias"
                    onClick={openModal}
                    disabled={!isCreateAliasFormVisible}
                  >
                    {t('New alias')}
                  </Button>
                </div>
              </Tooltip>
            )}
          </div>
        </div>

        <AliasesListView mailDomain={mailDomain} querySearch={searchValue} />
        {!mailDomain.count_mailboxes && (
          <Text $align="center" $size="small">
            {t('No alias was created with this mail domain.')}
          </Text>
        )}
        {isCreateAliasFormVisible && mailDomain ? (
          <ModalCreateAlias
            mailDomain={mailDomain}
            closeModal={() => setIsCreateAliasFormVisible(false)}
          />
        ) : null}
      </div>
    </>
  );
}


