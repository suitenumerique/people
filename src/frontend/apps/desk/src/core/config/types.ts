export interface Config {
  CRISP_WEBSITE_ID: string;
  LANGUAGES: [string, string][];
  RELEASE: string;
  COMMIT: string;
  FEATURES: {
    TEAMS_DISPLAY: boolean;
  };
}
