import { Loader } from '@gouvfr-lasuite/cunningham-react';
import React, { useMemo, useRef } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Text } from '@/components';
import { InfiniteScroll } from '@/components/InfiniteScroll';
import {
  MailDomain,
  useMailDomains,
  useMailDomainsStore,
} from '@/features/mail-domains/domains';

import { PanelMailDomains } from './PanelItem';

interface PanelMailDomainsStateProps {
  isLoading: boolean;
  isError: boolean;
  mailDomains?: MailDomain[];
}

export const ItemList = () => {
  const { ordering } = useMailDomainsStore();
  const {
    data,
    isError,
    isLoading,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useMailDomains({ ordering });
  const containerRef = useRef<HTMLDivElement>(null);
  const mailDomains = useMemo(() => {
    return data?.pages.reduce((acc, page) => {
      return acc.concat(page.results);
    }, [] as MailDomain[]);
  }, [data?.pages]);

  return (
    <Box $css="overflow-y: auto; overflow-x: hidden;" ref={containerRef}>
      <InfiniteScroll
        hasMore={hasNextPage}
        isLoading={isFetchingNextPage}
        next={() => {
          void fetchNextPage();
        }}
        scrollContainer={containerRef.current}
        as="ul"
        $margin={{ top: 'none' }}
        $padding="none"
        role="listbox"
      >
        <ItemListState
          isLoading={isLoading}
          isError={isError}
          mailDomains={mailDomains}
        />
      </InfiniteScroll>
    </Box>
  );
};

const ItemListState = ({
  isLoading,
  isError,
  mailDomains,
}: PanelMailDomainsStateProps) => {
  const { t } = useTranslation();

  if (isError) {
    return (
      <Box $justify="center" $margin={{ bottom: 'big' }}>
        <Text $theme="danger" $align="center" $textAlign="center">
          {t('Something wrong happened, please refresh the page.')}
        </Text>
      </Box>
    );
  }

  if (isLoading) {
    return (
      <Box $align="center" $margin="large">
        <Loader aria-label={t('mail domains list loading')} />
      </Box>
    );
  }

  if (!mailDomains?.length) {
    return (
      <Box $justify="center" $margin="small">
        <Text as="p" $margin={{ vertical: 'none' }}>
          {t(`No domains exist.`)}
        </Text>
      </Box>
    );
  }

  return mailDomains.map((mailDomain) => (
    <PanelMailDomains mailDomain={mailDomain} key={mailDomain.id} />
  ));
};
