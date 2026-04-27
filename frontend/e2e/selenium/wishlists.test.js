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
  {
    number: 20,
    title: 'Управление вишлистом и желаниями внутри него',
    requirements: ['FS-7.1', 'FS-7.2', 'FS-7.3.2', 'FS-7.5.1', 'FS-7.5.2', 'FS-7.5.3', 'FS-6.4.2.3'],
    requires: ['authenticated'],
    run: async ({ driver, By, until, baseUrl }) => {
      await openApp(driver, baseUrl);
      await clickByAnyText(driver, By, until, ['Вишлисты', 'Все ваши вишлисты']);
      await clickByAnyText(driver, By, until, ['Создать вишлист', 'Добавить вишлист']);
      await fillFirstMatchingInput(driver, By, 'E2E wishlist', ['input']);
      await clickByAnyText(driver, By, until, ['Публичный', 'Виден всем']);
      await clickByAnyText(driver, By, until, ['Сохранить']);
      await expectText(driver, By, until, 'E2E wishlist');
      const openWishlistButton = await driver.findElement(By.xpath(
        "//div[contains(@class, 'wishlist-card')][.//*[contains(normalize-space(.), 'E2E wishlist')]]//button[contains(@aria-label, 'Открыть')]"
      ));
      await driver.executeScript("arguments[0].scrollIntoView({ block: 'center', inline: 'center' })", openWishlistButton);
      await openWishlistButton.click();
      await clickByAnyText(driver, By, until, ['Добавить существующее желание']);
      await clickByAnyText(driver, By, until, ['E2E existing wish']);
      await clickByAnyText(driver, By, until, ['Добавить выбранные']);
      await expectText(driver, By, until, 'E2E existing wish');
      const pinButton = await driver.wait(until.elementLocated(By.css('button[aria-label="Закрепить"]')), 10000)
        .catch(async (error) => {
          throw new Error(`${error.message}\n${await getPageDebug(driver, By)}`);
        });
      await driver.executeScript("arguments[0].scrollIntoView({ block: 'center', inline: 'center' })", pinButton);
      await pinButton.click();
      await driver.wait(until.elementLocated(By.css('button[aria-label="Открепить"]')), 10000);
    },
  },
]);
