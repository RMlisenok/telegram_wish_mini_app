import { clickByAnyText, expectText, fillFirstMatchingInput, openApp } from './helpers.js';
import { defineScenarioSuite } from './scenarioRunner.js';

const start = ['Мой профиль', 'My Profile', 'Начать'];
const main = ['Профиль', 'Главная'];
const save = ['Сохранить', 'Сохранить изменения'];

defineScenarioSuite('Registration E2E scenarios', [
  {
    number: 1,
    title: 'Регистрация нового пользователя через Telegram',
    requirements: ['FS-1.1', 'FS-1.2', 'FS-1.3', 'FS-1.4'],
    requires: ['telegram'],
    run: async ({ driver, By, until, baseUrl }) => {
      await openApp(driver, baseUrl);
      await clickByAnyText(driver, By, until, start);
      await expectText(driver, By, until, main);
    },
  },
  {
      number: 2,
      title: 'Авторизация уже зарегистрированного пользователя',
      requirements: ['FS-1.5'],
      requires: ['telegram'],
      run: async ({ driver, By, until, baseUrl }) => {
        await openApp(driver, baseUrl);
        await clickByAnyText(driver, By, until, start);
        await expectText(driver, By, until, main);
      },
    },
]);
