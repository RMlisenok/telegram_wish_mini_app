import { jest } from '@jest/globals';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/svelte';

import ShareProfileScreen from '../ShareProfileScreen.svelte';
import ShareProfileScreenEventHarness from './ShareProfileScreenEventHarness.svelte';

const baseUser = {
  id: 42,
  fullName: 'John Doe',
  avatarUrl: '',
  birthDate: '01.01.1990'
};

function makeJwtLikeId(sub) {
  const header = Buffer.from(JSON.stringify({ alg: 'none', typ: 'JWT' })).toString('base64url');
  const payload = Buffer.from(JSON.stringify({ sub })).toString('base64url');
  return `${header}.${payload}.signature`;
}

function setTelegramWebApp(overrides = {}) {
  window.Telegram = {
    WebApp: {
      showPopup: jest.fn(),
      showAlert: jest.fn(),
      openTelegramLink: jest.fn(),
      openLink: jest.fn(),
      ...overrides
    }
  };

  return window.Telegram.WebApp;
}

function setClipboard(writeTextImpl = jest.fn().mockResolvedValue(undefined)) {
  Object.defineProperty(window.navigator, 'clipboard', {
    configurable: true,
    value: { writeText: writeTextImpl }
  });

  return writeTextImpl;
}

describe('ShareProfileScreen', () => {
  beforeEach(() => {
    global.alert = jest.fn();
    delete window.Telegram;
    delete window.navigator.share;
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
  });

  test('renders decoded user id from JWT-like other profile id', async () => {
    setTelegramWebApp();

    render(ShareProfileScreen, {
      user: baseUser,
      otherProfile: {
        id: makeJwtLikeId(456),
        fullName: 'Alice Wonder',
        avatarUrl: ''
      }
    });

    expect(screen.getByText('Alice Wonder')).toBeInTheDocument();
    expect(screen.getByText('ID: 456')).toBeInTheDocument();
  });

  test('falls back to current user when other profile has no id', async () => {
    setTelegramWebApp();

    render(ShareProfileScreen, {
      user: baseUser,
      otherProfile: { fullName: 'Ghost Profile' }
    });

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('ID: 42')).toBeInTheDocument();
  });

  test('copies profile link and shows popup success message', async () => {
    const tg = setTelegramWebApp();
    const writeText = setClipboard();

    render(ShareProfileScreen, { user: baseUser });

    await fireEvent.click(screen.getByText('Скопировать ссылку'));

    await waitFor(() => {
      expect(writeText).toHaveBeenCalledWith(
        'https://t.me/testworkwishbot/?startapp=profile_42'
      );
      expect(tg.showPopup).toHaveBeenCalledWith(
        expect.objectContaining({ message: 'Ссылка на профиль скопирована' })
      );
    });
  });

  test('shows copy failure message through telegram alert', async () => {
    const tg = setTelegramWebApp({ showPopup: undefined, showAlert: jest.fn() });
    const writeText = setClipboard(jest.fn().mockRejectedValue(new Error('copy failed')));

    render(ShareProfileScreen, { user: baseUser });

    await fireEvent.click(screen.getByText('Скопировать ссылку'));

    await waitFor(() => {
      expect(writeText).toHaveBeenCalled();
      expect(tg.showAlert).toHaveBeenCalledWith('Не удалось скопировать ссылку');
    });
  });

  test('shares profile in telegram using openTelegramLink', async () => {
    const tg = setTelegramWebApp();

    render(ShareProfileScreen, { user: baseUser });

    await fireEvent.click(screen.getByText('Поделиться в Telegram'));

    expect(tg.openTelegramLink).toHaveBeenCalledWith(
      'https://t.me/share/url?url=https%3A%2F%2Ft.me%2Ftestworkwishbot%2F%3Fstartapp%3Dprofile_42&text=%D0%9F%D1%80%D0%BE%D1%84%D0%B8%D0%BB%D1%8C%3A%20John%20Doe'
    );
  });

  test('shares using Web Share API and shows completion popup', async () => {
    const tg = setTelegramWebApp();
    Object.defineProperty(window.navigator, 'share', {
      configurable: true,
      value: jest.fn().mockResolvedValue(undefined)
    });

    render(ShareProfileScreen, { user: baseUser });

    await fireEvent.click(screen.getByText('Другие способы'));

    await waitFor(() => {
      expect(window.navigator.share).toHaveBeenCalledWith({
        title: 'Подари мне — профиль',
        text: 'Профиль: John Doe',
        url: 'https://t.me/testworkwishbot/?startapp=profile_42'
      });
      expect(tg.showPopup).toHaveBeenCalledWith(
        expect.objectContaining({ message: 'Готово' })
      );
    });
  });

  test('falls back to copying link when Web Share API is unavailable', async () => {
    const tg = setTelegramWebApp();
    const writeText = setClipboard();

    render(ShareProfileScreen, { user: baseUser });

    await fireEvent.click(screen.getByText('Другие способы'));

    await waitFor(() => {
      expect(writeText).toHaveBeenCalledWith(
        'https://t.me/testworkwishbot/?startapp=profile_42'
      );
      expect(tg.showPopup).toHaveBeenCalledWith(
        expect.objectContaining({ message: 'Ссылка на профиль скопирована' })
      );
    });
  });

});
