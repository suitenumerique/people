import { execSync } from 'child_process';
import fs from 'fs';

describe('checks all the frontend translation are made', () => {
  it('checks missing translation. If this test fails, go to https://crowdin.com/', () => {
    // Extract the translations
    execSync(
      'yarn extract-translation:desk -c ./i18next-parser.config.jest.mjs',
    );
    const outputCrowdin = './locales/desk/translations-crowdin.json';
    const jsonCrowdin = JSON.parse(fs.readFileSync(outputCrowdin, 'utf8'));
    const listKeysCrowdin = Object.keys(jsonCrowdin).sort();

    // Check the translations in the app Desk
    const outputDesk = '../../apps/desk/src/i18n/translations.json';
    const jsonDesk = JSON.parse(fs.readFileSync(outputDesk, 'utf8'));

    // Our keys are in english, so we don't need to check the english translation
    Object.keys(jsonDesk)
      .filter((key) => key !== 'en')
      .forEach((key) => {
        const listKeysDesk = Object.keys(jsonDesk[key].translation).sort();
        expect(
          listKeysCrowdin.every((element) => listKeysDesk.includes(element)),
        ).toBeTruthy();
      });
  });
});
