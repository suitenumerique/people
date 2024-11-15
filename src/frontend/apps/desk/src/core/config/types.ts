export interface Config {
  LANGUAGES: [string, string][];
  RELEASE: string;
  COMMIT: string;
  FEATURES: {
    TEAMS_DISPLAY: boolean;
  };
}
