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
  {
    number: 7,
    title: 'Валидация обязательных полей профиля',
    requirements: ['FS-3.1'],
    requires: ['authenticated'],
    run: async ({ driver, By, until, baseUrl }) => {
      await openApp(driver, baseUrl);
      await clickByAnyText(driver, By, until, settings);
      await clickByAnyText(driver, By, until, editProfile);
      await fillFirstMatchingInput(driver, By, '', ['input[aria-label*="Имя"]', 'input']);
      await fillFirstMatchingInput(driver, By, '', ['input[placeholder="ДД.ММ.ГГГГ"]', 'input[maxlength="10"]']);
      await clickByAnyText(driver, By, until, save);
      await expectText(driver, By, until, ['обязательна', 'должно содержать']);
    },
  },
  {
    number: 8,
    title: 'Загрузка и удаление фотографии профиля',
    requirements: ['FS-3.1', 'FS-1.3'],
    requires: ['authenticated', 'fileUpload'],
    run: async ({ driver, By, until, baseUrl, env }) => {
      await openApp(driver, baseUrl);
      await clickByAnyText(driver, By, until, settings);
      await clickByAnyText(driver, By, until, editProfile);
      await clickByAnyText(driver, By, until, ['Загрузить фото']);
      const input = await driver.findElement(By.css('input[type="file"]'));
      await input.sendKeys(env.E2E_UPLOAD_IMAGE_PATH);
      await clickByAnyText(driver, By, until, ['Удалить']);
      await clickByAnyText(driver, By, until, save);
      await expectText(driver, By, until, ['Настройки', 'Изменения успешно сохранены']);
    },
  },
]);
