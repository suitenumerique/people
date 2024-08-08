import MailDomains from './mail-domains';
import Teams from './teams';

export default process.env.NEXT_PUBLIC_FEATURE_TEAM === 'true'
  ? Teams
  : MailDomains;
