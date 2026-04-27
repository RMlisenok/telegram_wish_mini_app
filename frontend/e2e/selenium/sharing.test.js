import { clickByAnyText, expectText, openApp } from './helpers.js';
import { defineScenarioSuite } from './scenarioRunner.js';

defineScenarioSuite('Sharing E2E scenarios', [
  {
    number: 11,
    title: 'Генерация и копирование ссылки на профиль',
    requirements: ['FS-4.1', 'FS-4.2'],
    requires: ['authenticated', 'clipboard'],
    run: async ({ driver, By, until, baseUrl }) => {
      await openApp(driver, baseUrl);
      await clickByAnyText(driver, By, until, ['Поделиться профилем']);
      await expectText(driver, By, until, ['Скопировать ссылку', 'Поделиться в Telegram', 'Другие способы']);
      await clickByAnyText(driver, By, until, ['Скопировать ссылку']);
      await expectText(driver, By, until, ['Ссылка скопирована', 'Ссылка на профиль скопирована']);
    },
  },
  {
    number: 12,
    title: 'Открытие публичного профиля по ссылке',
    requirements: ['FS-4.3', 'FS-3.2'],
    requires: ['multiUser'],
    run: async ({ driver, By, until, env }) => {
      await openApp(driver, env.E2E_PUBLIC_PROFILE_URL);
      await expectText(driver, By, until, ['Профиль', 'Анкета', 'Вишлисты']);
    },
  },
]);
