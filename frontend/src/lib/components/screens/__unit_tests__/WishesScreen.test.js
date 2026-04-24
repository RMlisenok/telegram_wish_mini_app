import { jest } from '@jest/globals';
import { cleanup, fireEvent, render, waitFor } from '@testing-library/svelte';

import WishesScreen from '../WishesScreen.svelte';
import WishesScreenEventHarness from './WishesScreenEventHarness.svelte';
import { wishesStore } from '../../../../types/wishes.ts';
import { wishlistsStore } from '../../../../types/wishlists.ts';
import { wishWishlistsStore } from '../../../../types/wish_wishlist.ts';

const okJson = (data) => ({
  ok: true,
  status: 200,
  json: async () => data,
  text: async () => JSON.stringify(data)
});

function renderScreen(props = {}) {
  return render(WishesScreen, {
    token: '',
    wishlistId: null,
    isExternalWishlist: false,
    currentUserId: null,
    onNavigateToCreateWishes: jest.fn(),
    ...props
  });
}

describe('WishesScreen', () => {
  beforeEach(() => {
    wishesStore.set([]);
    wishlistsStore.set([]);
    wishWishlistsStore.set([]);

    global.fetch = jest.fn();
    global.alert = jest.fn();
    global.confirm = jest.fn(() => true);
    global.open = jest.fn();

    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
  });

  test('shows empty mode and triggers create + finished navigation', async () => {
    const onNavigateToCreateWishes = jest.fn();
    const { container } = render(WishesScreenEventHarness, {
      token: '',
      wishlistId: null,
      isExternalWishlist: false,
      currentUserId: null,
      onNavigateToCreateWishes
    });

    expect(container.querySelector('.empty-note')).toBeTruthy();

    await fireEvent.click(container.querySelector('.finished-button'));
    await fireEvent.click(container.querySelector('.ui-button.full'));

    const eventNames = Array.from(container.querySelectorAll('[data-testid="events-log"] li')).map(
      (node) => node.textContent
    );
    expect(eventNames).toEqual(['openFinishedWishes']);
    expect(onNavigateToCreateWishes).toHaveBeenCalledTimes(1);
  });
});
