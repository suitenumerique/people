import { Box } from '@/components';
import { HEADER_HEIGHT, Header, Menu } from '@/features/';

export default function InnerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <Box as="main" $height="100vh" $css="overflow:hidden;">
      <Header />
      <Box $css="flex: 1;" $direction="row">
        <Menu />
        <Box $height={`calc(100vh - ${HEADER_HEIGHT})`} $width="100%">
          {children}
        </Box>
      </Box>
    </Box>
  );
}
