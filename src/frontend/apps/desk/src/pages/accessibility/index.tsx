import { PropsWithChildren, ReactElement } from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Text, TextStyled, TextType } from '@/components';
import { useCunninghamTheme } from '@/cunningham';
import { PageLayout } from '@/layouts';
import { NextPageWithLayout } from '@/types/next';

const Inline = ({ children, ...props }: PropsWithChildren<TextType>) => {
  return (
    <Text as="p" $display="inline" {...props}>
      {children}
    </Text>
  );
};

const Page: NextPageWithLayout = () => {
  const { t } = useTranslation();
  const { colorsTokens } = useCunninghamTheme();

  return (
    <Box $margin={{ top: '50px' }}>
      <Box
        as="h1"
        $background={colorsTokens()['primary-100']}
        $margin="none"
        $padding="large"
      >
        {t('Accessibility statement')}
      </Box>
      <Box $padding={{ horizontal: 'large', vertical: 'big' }}>
        <Inline>{t('Declaration established on June 25, 2024.')}</Inline>
        <Inline>
          {t(`The National Agency for Territorial Cohesion undertakes to make its
          service accessible, in accordance with article 47 of law no. 2005-102
          of February 11, 2005.`)}
          <br />
          {t(
            `This accessibility statement applies to La Régie (Suite Territoriale)`,
          )}{' '}
          (https://regie.numerique.gouv.fr/).
        </Inline>
        <Text as="h2" $margin={{ bottom: 'xtiny' }}>
          {t('Compliance status')}
        </Text>
        <Inline>
          {t(
            'La Régie (Suite Territoriale) is non-compliant with the RGAA. The site has not yet been audited.',
          )}
        </Inline>
        <Text as="h2" $margin={{ bottom: 'xtiny' }}>
          {t('Improvement and contact')}
        </Text>
        <Box $margin={{ top: '1rem' }}>
          {t(
            `If you are unable to access content or a service, you can contact the manager of La Régie (Suite Territoriale) 
            to be directed to an accessible alternative or obtain the content in another form.`,
          )}
          <ul>
            <li>
              {t(
                `Address: National Agency for Territorial Cohesion - 20, avenue de Ségur TSA 10717 75 334 Paris Cedex 07 Paris`,
              )}
            </li>
            <li>
              {t('E-mail:')}{' '}
              <TextStyled
                as="a"
                href="mailto:suiteterritoriale@anct.gouv.fr"
                $display="inline"
              >
                suiteterritoriale@anct.gouv.fr
              </TextStyled>
            </li>
          </ul>
        </Box>
        <Text as="h2" $margin={{ bottom: 'xtiny' }}>
          {t('Remedy')}
        </Text>
        <Inline>
          {t(
            `This procedure is to be used in the following case: you have reported to the website 
            manager an accessibility defect which prevents you from accessing content or one of the 
            portal's services and you have not obtained a satisfactory response.`,
          )}
        </Inline>
        <Box>
          {t('You can:')}
          <Box as="ul" $margin={{ top: 'tiny' }}>
            <li>
              <Trans t={t} i18nKey="accessibility-form-defenseurdesdroits">
                Write a message to the
                <TextStyled
                  as="a"
                  href="https://formulaire.defenseurdesdroits.fr/formulaire_saisine/"
                  $display="inline"
                  $margin={{ left: '4px' }}
                >
                  Defender of Rights
                </TextStyled>
              </Trans>
            </li>
            <li>
              <Trans t={t} i18nKey="accessibility-contact-defenseurdesdroits">
                Contact the delegate of the
                <TextStyled
                  as="a"
                  href="https://www.defenseurdesdroits.fr/carte-des-delegues"
                  $display="inline"
                  $margin={{ left: '4px' }}
                >
                  Defender of Rights in your region
                </TextStyled>
              </Trans>
            </li>
            <li>
              {t('Send a letter by post (free of charge, no stamp needed):')}{' '}
              <strong>
                {t(
                  'Defender of Rights - Free response - 71120 75342 Paris CEDEX 07',
                )}
              </strong>
            </li>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

Page.getLayout = function getLayout(page: ReactElement) {
  return <PageLayout>{page}</PageLayout>;
};

export default Page;
