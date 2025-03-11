import React, { ReactElement} from "react";
import { Button, Input } from "@openfun/cunningham-react";
import { useCunninghamTheme } from '@/cunningham';

import { useTranslation } from "react-i18next";
import styled from "styled-components";
import { Box, Text, Card } from "@/components";
import { useAuthStore } from "@/core/auth";
import { MainLayout } from "@/layouts";
import { NextPageWithLayout } from "@/types/next";
import { MailDomainsListView } from "@/features/mail-domains/domains/components/MailDomainsListView";
import { ModalAddMailDomain } from "@/features/mail-domains/domains/components/ModalAddMailDomain"; // Import de la modale

const StyledButton = styled(Button)`
  @media (max-width: 768px) {
    margin-top: 10px;
  }
`;

const Page: NextPageWithLayout = () => {
  const { t } = useTranslation();
  const { userData } = useAuthStore();
  const can_create = userData?.abilities?.mailboxes.can_create;
  const [isModalOpen, setIsModalOpen] = React.useState(false);

  const [searchValue, setSearchValue] = React.useState("");
  const { colorsTokens } = useCunninghamTheme();
  const colors = colorsTokens();

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchValue(event.target.value);
  };

  const clearInput = () => {
    setSearchValue("");
  };

  const openModal = () => {
    setIsModalOpen(true); 
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  return (
    <Box
      $position="relative"
      $width="100%"
      $direction="row"
      $maxWidth="960px"
      $maxHeight="calc(100vh - 52px - 1rem)"
      $align="center"
      $margin="20px auto"
      $padding="0 10px"
      $css={`
        overflow-x: hidden;
        overflow-y: auto;
      `}
    >
      <Card
        data-testid="regie-grid"
        $height="100%"
        $justify="center"
        $width="100%"
        $css={`
          overflow-x: hidden;
          overflow-y: auto;
        `}
        $padding={{
          top: "md",
          bottom: "md",
          horizontal: "md",
        }}
      >
        <Text
          as="h2"
          $weight="700"
          $size="h4"
          $variation="1000"
          $margin={{ top: "0px", bottom: "20px" }}
        >
          Domaines de l’organisation
        </Text>

        <Box 
          className="sm:block md:flex"
          $margin={{ top: "0px", bottom: "20px" }}
          $direction="row"
          $align="center"
          $justify="space-between"
          $gap="1em"
          >
            <Box $minWidth="72%">
              <Input
                label={t('Search a mail domain')}
                icon={<span className="material-icons">search</span>}
                rightIcon={
                  searchValue && (
                    <span className="material-icons" onClick={clearInput} style={{ cursor: "pointer" }}>
                      close
                    </span>
                  )
                }
                value={searchValue}
                onChange={handleInputChange}
              />
            </Box>

            <Box
              className="hidden md:flex"
              $background={colors['greyscale-200']} 
              $height="32px"
              $width="1px"
            >
            </Box>

          {can_create && (
            <StyledButton onClick={openModal}>
              {t("Add a mail domain")}
            </StyledButton>
          )}
        </Box>

        {!can_create && <Text>{t("Click on mailbox to view details")}</Text>}
        <MailDomainsListView querySearch={searchValue} />
        
        {/* Affiche la modale si l'état est true */}
        {isModalOpen && <ModalAddMailDomain closeModal={closeModal} />}
      </Card>
    </Box>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <MainLayout backgroundColor="grey">{page}</MainLayout>;
};

export default Page;
