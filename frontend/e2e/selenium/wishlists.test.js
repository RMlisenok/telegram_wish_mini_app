import { clickByAnyText, expectText, fillFirstMatchingInput, getPageDebug, openApp } from './helpers.js';
import { defineScenarioSuite } from './scenarioRunner.js';

defineScenarioSuite('Wishlists E2E scenarios', [
  {
    number: 19,
    title: 'Привязка желания к вишлистам и сохранение без выбора',
    requirements: ['FS-6.3.1', 'FS-6.3.3'],
    requires: ['authenticated'],
    run: async ({ driver, By, until, baseUrl }) => {
      await openApp(driver, baseUrl);
      await clickByAnyText(driver, By, until, ['Желания', 'Ваши желания']);
      await clickByAnyText(driver, By, until, ['Создать желание', 'Добавить желание', '+ Новое желание', 'Новое желание']);
      await fillFirstMatchingInput(driver, By, 'E2E wishlist-bound wish', ['input']);
      await clickByAnyText(driver, By, until, ['Сохранить']);
      await expectText(driver, By, until, 'E2E wishlist-bound wish');
    },
  },
]);
