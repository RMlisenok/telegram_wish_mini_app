import { jest } from '@jest/globals';
import { get } from 'svelte/store';

import { initializeTelegram, initData, telegram, user } from '../telegram.ts';

function createTelegramWebApp(overrides = {}) {
  return {
    initData: 'init-data-123',
    initDataUnsafe: {
      user: { id: 7, first_name: 'Alice' }
    },
    themeParams: {
      bg_color: '#123456'
    },
    ready: jest.fn(),
    expand: jest.fn(),
    enableClosingConfirmation: jest.fn(),
    setHeaderColor: jest.fn(),
    setBackgroundColor: jest.fn(),
    ...overrides
  };
}

describe('lib/telegram', () => {
  beforeEach(() => {
    telegram.set(null);
    user.set(null);
    initData.set('');
    delete window.Telegram;
  });

  afterEach(() => {
    jest.restoreAllMocks();
    delete window.Telegram;
  });

  test('initializeTelegram returns null outside Telegram WebApp', () => {
    expect(initializeTelegram()).toBeNull();
    expect(get(telegram)).toBeNull();
    expect(get(user)).toBeNull();
    expect(get(initData)).toBe('');
  });

  test('initializeTelegram stores Telegram instance, init data and user', () => {
    const tg = createTelegramWebApp();
    window.Telegram = { WebApp: tg };

    const result = initializeTelegram();

    expect(result).toBe(tg);
    expect(get(telegram)).toBe(tg);
    expect(get(initData)).toBe('init-data-123');
    expect(get(user)).toEqual({ id: 7, first_name: 'Alice' });
    expect(tg.ready).toHaveBeenCalledTimes(1);
    expect(tg.expand).toHaveBeenCalledTimes(1);
    expect(tg.enableClosingConfirmation).toHaveBeenCalledTimes(1);
    expect(tg.setHeaderColor).toHaveBeenCalledWith('#123456');
    expect(tg.setBackgroundColor).toHaveBeenCalledWith('#123456');
  });

  test('initializeTelegram uses fallback colors when Telegram theme has no bg_color', () => {
    const tg = createTelegramWebApp({ themeParams: {}, initDataUnsafe: {} });
    window.Telegram = { WebApp: tg };

    initializeTelegram();

    expect(get(user)).toBeUndefined();
    expect(tg.setHeaderColor).toHaveBeenCalledWith('#2481cc');
    expect(tg.setBackgroundColor).toHaveBeenCalledWith('#ffffff');
  });
});
