import { clickByAnyText, expectText, openApp } from './helpers.js';
import { defineScenarioSuite } from './scenarioRunner.js';

defineScenarioSuite('Settings E2E scenarios', [
  {
    number: 9,
    title: 'Настройка приватности "Показывать мои подписки"',
    requirements: ['FS-3.2', 'FS-4.3'],
    requires: ['authenticated', 'multiUser'],
    run: async ({ driver, By, until, baseUrl }) => {
      await openApp(driver, baseUrl);
      await clickByAnyText(driver, By, until, ['Настройки']);
      await clickByAnyText(driver, By, until, ['Настройки приватности']);
      await clickByAnyText(driver, By, until, ['Показывать мои подписки']);
      await clickByAnyText(driver, By, until, ['Сохранить', 'Сохранить изменения']);
      await expectText(driver, By, until, ['Сохранено', 'Изменения успешно сохранены']);
    },
  },
]);
