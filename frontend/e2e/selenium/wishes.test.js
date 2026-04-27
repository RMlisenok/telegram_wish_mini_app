import { clickByAnyText, expectText, fillFirstMatchingInput, openApp } from './helpers.js';
import { defineScenarioSuite } from './scenarioRunner.js';

async function openCreateWish(driver, By, until, baseUrl) {
  await openApp(driver, baseUrl);
  await clickByAnyText(driver, By, until, ['Желания', 'Ваши желания']);
  await clickByAnyText(driver, By, until, ['Создать желание', 'Добавить желание', '+ Новое желание', 'Новое желание']);
}

defineScenarioSuite('Wishes E2E scenarios', [
  {
    number: 17,
    title: 'Создание желания с обязательным названием',
    requirements: ['FS-6.1', 'FS-6.2', 'NFS-6.1'],
    requires: ['authenticated'],
    run: async ({ driver, By, until, baseUrl }) => {
      await openCreateWish(driver, By, until, baseUrl);
      await clickByAnyText(driver, By, until, ['Сохранить']);
      await expectText(driver, By, until, ['Название', 'обязательно']);
      await fillFirstMatchingInput(driver, By, 'E2E wish', ['input']);
      await clickByAnyText(driver, By, until, ['Сохранить']);
      await expectText(driver, By, until, 'E2E wish');
    },
  },
  {
    number: 18,
    title: 'Создание желания с дополнительными полями и валидацией',
    requirements: ['FS-6.1', 'NFS-6.3', 'NFS-6.4', 'NFS-6.5'],
    requires: ['authenticated'],
    run: async ({ driver, By, until, baseUrl }) => {
      await openCreateWish(driver, By, until, baseUrl);
      await fillFirstMatchingInput(driver, By, 'E2E validated wish', ['input']);
      await fillFirstMatchingInput(driver, By, 'invalid-url', ['input[type="url"]', 'input[name="link"]']);
      await clickByAnyText(driver, By, until, ['Сохранить']);
      await expectText(driver, By, until, ['http://', 'https://', 'URL']);
    },
  },
]);
