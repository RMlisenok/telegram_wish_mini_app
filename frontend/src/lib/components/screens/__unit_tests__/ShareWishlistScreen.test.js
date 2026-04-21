import { jest } from '@jest/globals';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/svelte';

import ShareWishlistScreen from '../ShareWishlistScreen.svelte';
import ShareWishlistScreenEventHarness from './ShareWishlistScreenEventHarness.svelte';

const baseUser = {
  fullName: 'John Doe',
  avatarUrl: ''
};

const baseWishlist = {
  id: 77,
  title: 'Birthday Gifts',
  photo: '',
  typeprivacy: 'public',
  count: 3,
  isExternalWishlist: false,
  isCurrentUserOwner: true
};

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

describe('ShareWishlistScreen', () => {
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

  test('renders wishlist information, count and privacy text', async () => {
    setTelegramWebApp();

    const { container } = render(ShareWishlistScreen, {
      user: baseUser,
      wishlist: baseWishlist
    });

    expect(screen.getByText('Birthday Gifts')).toBeInTheDocument();
    expect(screen.getByText('Желаний: 3')).toBeInTheDocument();
    expect(screen.getByText('Публичный')).toBeInTheDocument();
    expect(container.querySelector('.wishlist-placeholder')?.textContent?.trim()).toBe('B');
  });

  test('shows external wishlist helper text for non-owner external wishlist', async () => {
    setTelegramWebApp();

    render(ShareWishlistScreen, {
      user: baseUser,
      wishlist: {
        ...baseWishlist,
        isExternalWishlist: true,
        isCurrentUserOwner: false
      }
    });

    expect(
      screen.getByText(
        'Отправьте ссылку на этот вишлист, чтобы другие могли видеть желания и выбирать подарки.'
      )
    ).toBeInTheDocument();
  });

  test('copies wishlist link and shows popup success message', async () => {
    const tg = setTelegramWebApp();
    const writeText = setClipboard();

    render(ShareWishlistScreen, {
      user: baseUser,
      wishlist: baseWishlist
    });

    await fireEvent.click(screen.getByText('Скопировать ссылку'));

    await waitFor(() => {
      expect(writeText).toHaveBeenCalledWith(
        'https://t.me/testworkwishbot/?startapp=wishlist_77'
      );
      expect(tg.showPopup).toHaveBeenCalledWith(
        expect.objectContaining({ message: 'Ссылка на вишлист скопирована' })
      );
    });
  });

  test('shares wishlist in telegram using openTelegramLink', async () => {
    const tg = setTelegramWebApp();

    render(ShareWishlistScreen, {
      user: baseUser,
      wishlist: baseWishlist
    });

    await fireEvent.click(screen.getByText('Поделиться в Telegram'));

    expect(tg.openTelegramLink).toHaveBeenCalledWith(
      'https://t.me/share/url?url=https%3A%2F%2Ft.me%2Ftestworkwishbot%2F%3Fstartapp%3Dwishlist_77&text=%D0%92%D0%B8%D1%88%D0%BB%D0%B8%D1%81%D1%82%3A%20Birthday%20Gifts'
    );
  });

  test('shares wishlist through Web Share API and shows completion popup', async () => {
    const tg = setTelegramWebApp();
    Object.defineProperty(window.navigator, 'share', {
      configurable: true,
      value: jest.fn().mockResolvedValue(undefined)
    });

    render(ShareWishlistScreen, {
      user: baseUser,
      wishlist: baseWishlist
    });

    await fireEvent.click(screen.getByText('Другие способы'));

    await waitFor(() => {
      expect(window.navigator.share).toHaveBeenCalledWith({
        title: 'Подари мне — вишлист',
        text: 'Вишлист: Birthday Gifts',
        url: 'https://t.me/testworkwishbot/?startapp=wishlist_77'
      });
      expect(tg.showPopup).toHaveBeenCalledWith(
        expect.objectContaining({ message: 'Готово' })
      );
    });
  });

  test('falls back to copying wishlist link when Web Share API is unavailable', async () => {
    const tg = setTelegramWebApp();
    const writeText = setClipboard();

    render(ShareWishlistScreen, {
      user: baseUser,
      wishlist: baseWishlist
    });

    await fireEvent.click(screen.getByText('Другие способы'));

    await waitFor(() => {
      expect(writeText).toHaveBeenCalledWith(
        'https://t.me/testworkwishbot/?startapp=wishlist_77'
      );
      expect(tg.showPopup).toHaveBeenCalledWith(
        expect.objectContaining({ message: 'Ссылка на вишлист скопирована' })
      );
    });
  });

  test('dispatches backToWishlist event with wishlist id', async () => {
    setTelegramWebApp();

    render(ShareWishlistScreenEventHarness, {
      user: baseUser,
      wishlist: baseWishlist
    });

    await fireEvent.click(screen.getByText('Вернуться к вишлисту'));

    const events = Array.from(screen.getByTestId('events-log').querySelectorAll('li')).map(
      (node) => node.textContent
    );

    expect(events).toEqual(['backToWishlist:77']);
  });
});
