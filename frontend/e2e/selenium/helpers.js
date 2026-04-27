export function escapeXpathText(text) {
  if (!text.includes("'")) {
    return `'${text}'`;
  }

  return `concat('${text.split("'").join(`', "'", '`)}')`;
}

export function textLocator(By, text) {
  return By.xpath(`//*[contains(normalize-space(.), ${escapeXpathText(text)})]`);
}

export async function findByAnyText(driver, By, until, texts, timeout = 10000) {
  const normalizedTexts = Array.isArray(texts) ? texts : [texts];
  const xpath = normalizedTexts
    .map((text) => `contains(normalize-space(.), ${escapeXpathText(text)})`)
    .join(' or ');
  const locator = By.xpath(`//*[${xpath}]`);
  await driver.wait(until.elementLocated(locator), timeout);
  return driver.findElement(locator);
}

export async function clickByAnyText(driver, By, until, texts, timeout = 10000) {
  const normalizedTexts = Array.isArray(texts) ? texts : [texts];
  const xpath = normalizedTexts
    .map((text) => `contains(normalize-space(.), ${escapeXpathText(text)})`)
    .join(' or ');
  const locator = By.xpath(`//*[self::button or self::a or self::label or @role='button'][${xpath}]`);
  try {
    await driver.wait(until.elementLocated(locator), timeout);
  } catch (error) {
    const debug = await getPageDebug(driver, By);
    throw new Error(`${error.message}\n${debug}`);
  }
  const element = await driver.wait(async () => {
    const elements = await driver.findElements(locator);
    for (const candidate of elements) {
      if (await candidate.isDisplayed().catch(() => false)) {
        return candidate;
      }
    }
    return false;
  }, timeout);
  await driver.executeScript("arguments[0].scrollIntoView({ block: 'center', inline: 'center' })", element);
  await driver.sleep(100);
  try {
    await element.click();
  } catch (error) {
    if (!String(error.name || error.message).includes('ElementClickIntercepted')) {
      throw error;
    }
    await driver.executeScript('arguments[0].click()', element);
  }
  return element;
}

export async function fillFirstMatchingInput(driver, By, value, selectors, timeout = 10000) {
  const element = await driver.wait(async () => {
    for (const selector of selectors) {
      const elements = await driver.findElements(By.css(selector));
      for (const candidate of elements) {
        if (await candidate.isDisplayed().catch(() => false)) {
          return candidate;
        }
      }
    }
    return false;
  }, timeout).catch(async () => {
    const debug = await getPageDebug(driver, By);
    throw new Error(`Input not found for selectors: ${selectors.join(', ')}\n${debug}`);
  });

  await driver.executeScript("arguments[0].scrollIntoView({ block: 'center', inline: 'center' })", element);
  await element.clear();
  await driver.executeScript("arguments[0].dispatchEvent(new Event('input', { bubbles: true }))", element);
  if (value) {
    await element.sendKeys(value);
  }
  return element;
}

export async function expectText(driver, By, until, texts, timeout = 10000) {
  try {
    await findByAnyText(driver, By, until, texts, timeout);
  } catch (error) {
    const debug = await getPageDebug(driver, By);
    throw new Error(`${error.message}\n${debug}`);
  }
}

export async function getPageDebug(driver, By) {
  const body = await driver.findElement(By.css('body')).getText().catch(() => '');
  const source = await driver.getPageSource().catch(() => '');
  const logs = await driver.manage().logs().get('browser')
    .then((items) => items.map((item) => `${item.level.name}: ${item.message}`).join('\n'))
    .catch(() => '');
  return `Page text:\n${body}\nBrowser logs:\n${logs}\nPage source excerpt:\n${source.slice(0, 1000)}`;
}

export async function openApp(driver, baseUrl) {
  await driver.get(baseUrl);
}
