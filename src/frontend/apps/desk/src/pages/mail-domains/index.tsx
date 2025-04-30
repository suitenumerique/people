import { Button, Input, Tooltip } from '@openfun/cunningham-react';
import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

import { useAuthStore } from '@/core/auth';
import { useCunninghamTheme } from '@/cunningham';
import { ModalAddMailDomain } from '@/features/mail-domains/domains/components/ModalAddMailDomain';
import { MailDomainsListView } from '@/features/mail-domains/domains/components/panel/MailDomainsListView';
import { MainLayout } from '@/layouts';
import { NextPageWithLayout } from '@/types/next';

const Page: NextPageWithLayout = () => {
  const { t } = useTranslation();
  const { userData } = useAuthStore();
  const can_create = userData?.abilities?.mailboxes.can_create;
  const [isModalOpen, setIsModalOpen] = React.useState(false);
  const [searchValue, setSearchValue] = React.useState('');
  const { colorsTokens } = useCunninghamTheme();
  const colors = colorsTokens();

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchValue(event.target.value);
  };

  const clearInput = () => {
    setSearchValue('');
  };

  const openModal = () => {
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  return (
    <div aria-label="Mail Domains panel" className="container">
      <div
        data-testid="regie-grid"
        style={{
          height: '100%',
          justifyContent: 'center',
          width: '100%',
          padding: '16px',
          overflowX: 'hidden',
          overflowY: 'auto',
          background: 'white',
          borderRadius: '4px',
          border: `1px solid ${colorsTokens()['greyscale-200']}`,
        }}
      >
        <h2
          style={{ fontWeight: 700, fontSize: '1.5rem', marginBottom: '20px' }}
        >
          {t('Areas of the organization')}
        </h2>

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
              label={t('Search a mail domain')}
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
            {can_create ? (
              <Button data-testid="button-new-domain" onClick={openModal}>
                {t('Add a mail domain')}
              </Button>
            ) : (
              <Tooltip content="You don't have the correct access right">
                <div>
                  <Button
                    data-testid="button-new-domain"
                    onClick={openModal}
                    disabled={!can_create}
                  >
                    {t('Add a mail domain')}
                  </Button>
                </div>
              </Tooltip>
            )}
          </div>
        </div>

        {!can_create && (
          <p style={{ textAlign: 'center' }}>
            {t('Click on mailbox to view details')}
          </p>
        )}

        <MailDomainsListView querySearch={searchValue} />
        {isModalOpen && <ModalAddMailDomain closeModal={closeModal} />}
      </div>
    </div>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <MainLayout backgroundColor="grey">{page}</MainLayout>;
};

export default Page;
