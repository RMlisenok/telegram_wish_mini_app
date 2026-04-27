import { clickByAnyText, expectText, fillFirstMatchingInput, openApp } from './helpers.js';
import { defineScenarioSuite } from './scenarioRunner.js';

const settings = ['Настройки'];
const editProfile = ['Редактировать профиль'];
const save = ['Сохранить', 'Сохранить изменения'];

defineScenarioSuite('Profile E2E scenarios', [
  {
    number: 6,
    title: 'Редактирование профиля с валидными данными',
    requirements: ['FS-3.1'],
    requires: ['authenticated'],
    run: async ({ driver, By, until, baseUrl }) => {
      await openApp(driver, baseUrl);
      await clickByAnyText(driver, By, until, settings);
      await clickByAnyText(driver, By, until, editProfile);
      await fillFirstMatchingInput(driver, By, 'E2E Test User', ['input[aria-label*="Имя"]', 'input']);
      await fillFirstMatchingInput(driver, By, '01.01.1990', ['input[placeholder="ДД.ММ.ГГГГ"]', 'input[maxlength="10"]']);
      await clickByAnyText(driver, By, until, save);
      await expectText(driver, By, until, ['E2E Test User', 'Настройки']);
    },
  },
]);
