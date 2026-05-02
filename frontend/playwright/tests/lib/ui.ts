import { Page, expect } from '@playwright/test';

export async function expectAppLoaded(page: Page) {
  await expect(page.locator('body')).toBeVisible();
}

export async function fillByPossibleSelectors(page: Page, selectors: string[], value: string) {
  for (const selector of selectors) {
    const locator = page.locator(selector);
    if (await locator.count()) {
      await locator.first().fill(value);
      return true;
    }
  }
  return false;
}

export async function clickByPossibleSelectors(page: Page, selectors: string[]) {
  for (const selector of selectors) {
    const locator = page.locator(selector);
    if (await locator.count()) {
      await locator.first().click();
      return true;
    }
  }
  return false;
}
