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

  test('loads wish details and dispatches edit event in default mode', async () => {
    global.fetch.mockImplementation(async (url, options = {}) => {
      const method = options.method || 'GET';

      if (url === '/api/v1/wishes/finish?is_finish=false' && method === 'GET') {
        return okJson([
          {
            id: 1,
            name: 'Lamp',
            photo: '',
            url_gift: 'https://shop/lamp',
            price: 99,
            currency: 'USD',
            is_booked: false
          }
        ]);
      }

      if (url === '/api/v1/wishes/1' && method === 'GET') {
        return okJson({
          id: 1,
          name: 'Lamp',
          photo: '',
          description: 'Warm light',
          price: 99,
          currency: 'USD',
          url_gift: 'https://shop/lamp',
          wishlists: [{ id: 10, name: 'Home' }],
          is_booked: false,
          status_is_finished: false,
          created_at: '2026-01-01T00:00:00.000Z',
          updated_at: '2026-01-01T00:00:00.000Z',
          user_id: 100
        });
      }

      throw new Error(`Unexpected fetch call: ${url} (${method})`);
    });

    const { container } = render(WishesScreenEventHarness, {
      token: 'token-123',
      wishlistId: null,
      isExternalWishlist: false,
      currentUserId: '100',
      onNavigateToCreateWishes: jest.fn()
    });

    await waitFor(() => {
      expect(container.querySelector('.wish-card')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.wish-card'));

    await waitFor(() => {
      expect(container.querySelector('.detail-panel')).toBeTruthy();
    });

    await fireEvent.click(container.querySelectorAll('.panel-actions .ui-button')[0]);

    const eventNames = Array.from(container.querySelectorAll('[data-testid="events-log"] li')).map(
      (node) => node.textContent
    );
    expect(eventNames).toContain('openEditWishes:{"id":1}');
  });

  test('marks wish as finished and removes it from all wishlists', async () => {
    let wishesLoadCount = 0;

    global.fetch.mockImplementation(async (url, options = {}) => {
      const method = options.method || 'GET';

      if (url === '/api/v1/wishes/finish?is_finish=false' && method === 'GET') {
        wishesLoadCount += 1;
        if (wishesLoadCount === 1) {
          return okJson([
            {
              id: 1,
              name: 'To Finish',
              photo: '',
              url_gift: '',
              price: 10,
              currency: 'USD',
              is_booked: false
            }
          ]);
        }

        return okJson([]);
      }

      if (url === '/api/v1/wishes/1' && method === 'GET') {
        return okJson({
          id: 1,
          name: 'To Finish',
          photo: '',
          description: 'desc',
          price: 10,
          currency: 'USD',
          url_gift: '',
          wishlists: [{ id: 10, name: 'A' }],
          is_booked: false,
          status_is_finished: false,
          created_at: '2026-01-01T00:00:00.000Z',
          updated_at: '2026-01-01T00:00:00.000Z',
          user_id: 1
        });
      }

      if (url === '/api/v1/wishes/1' && method === 'PUT') {
        return okJson({ id: 1 });
      }

      if (url === '/api/v1/wishes/wishlists/1' && method === 'DELETE') {
        return okJson({ success: true });
      }

      throw new Error(`Unexpected fetch call: ${url} (${method})`);
    });

    const { container } = renderScreen({
      token: 'token-123',
      currentUserId: '1'
    });

    await waitFor(() => {
      expect(container.querySelector('.wish-card')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.wish-card'));

    await waitFor(() => {
      expect(container.querySelector('.detail-panel')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.detail-section .ui-button.full'));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/wishes/1',
        expect.objectContaining({ method: 'PUT' })
      );
    });

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/wishes/wishlists/1',
      expect.objectContaining({ method: 'DELETE' })
    );
  });

  test('opens and confirms full wish deletion', async () => {
    let wishesLoadCount = 0;

    global.fetch.mockImplementation(async (url, options = {}) => {
      const method = options.method || 'GET';

      if (url === '/api/v1/wishes/finish?is_finish=false' && method === 'GET') {
        wishesLoadCount += 1;
        if (wishesLoadCount === 1) {
          return okJson([
            {
              id: 1,
              name: 'Delete Me',
              photo: '',
              url_gift: '',
              price: 5,
              currency: 'USD',
              is_booked: false
            }
          ]);
        }

        return okJson([]);
      }

      if (url === '/api/v1/wishes/1' && method === 'GET') {
        return okJson({
          id: 1,
          name: 'Delete Me',
          photo: '',
          description: 'desc',
          price: 5,
          currency: 'USD',
          url_gift: '',
          wishlists: [],
          is_booked: false,
          status_is_finished: false,
          created_at: '2026-01-01T00:00:00.000Z',
          updated_at: '2026-01-01T00:00:00.000Z',
          user_id: 1
        });
      }

      if (url === '/api/v1/wishes/1' && method === 'DELETE') {
        return okJson({ success: true });
      }

      throw new Error(`Unexpected fetch call: ${url} (${method})`);
    });

    const { container } = renderScreen({
      token: 'token-123',
      currentUserId: '1'
    });

    await waitFor(() => {
      expect(container.querySelector('.wish-card')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.wish-card'));

    await waitFor(() => {
      expect(container.querySelector('.detail-panel')).toBeTruthy();
    });

    await fireEvent.click(container.querySelectorAll('.panel-actions .ui-button')[1]);

    await waitFor(() => {
      expect(container.querySelector('.confirm-delete-modal')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.confirm-delete-modal .ui-button.danger'));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/wishes/1',
        expect.objectContaining({ method: 'DELETE' })
      );
    });
  });

  test('blocks pinning when pinned wishes limit is reached', async () => {
    const wishlistWishes = [
      {
        id: 1,
        name: 'Pinned 1',
        photo: '',
        url_gift: '',
        price: 1,
        currency: 'USD',
        description: '',
        is_booked: false,
        status_is_finished: false,
        created_at: '2026-01-01T00:00:00.000Z',
        updated_at: '2026-01-01T00:00:00.000Z',
        connection_id: 101,
        is_pinned: true,
        order_position: 0,
        added_at: '2026-01-01T00:00:00.000Z'
      },
      {
        id: 2,
        name: 'Pinned 2',
        photo: '',
        url_gift: '',
        price: 2,
        currency: 'USD',
        description: '',
        is_booked: false,
        status_is_finished: false,
        created_at: '2026-01-01T00:00:00.000Z',
        updated_at: '2026-01-01T00:00:00.000Z',
        connection_id: 102,
        is_pinned: true,
        order_position: 0,
        added_at: '2026-01-01T00:00:00.000Z'
      },
      {
        id: 3,
        name: 'Pinned 3',
        photo: '',
        url_gift: '',
        price: 3,
        currency: 'USD',
        description: '',
        is_booked: false,
        status_is_finished: false,
        created_at: '2026-01-01T00:00:00.000Z',
        updated_at: '2026-01-01T00:00:00.000Z',
        connection_id: 103,
        is_pinned: true,
        order_position: 0,
        added_at: '2026-01-01T00:00:00.000Z'
      },
      {
        id: 4,
        name: 'Pinned 4',
        photo: '',
        url_gift: '',
        price: 4,
        currency: 'USD',
        description: '',
        is_booked: false,
        status_is_finished: false,
        created_at: '2026-01-01T00:00:00.000Z',
        updated_at: '2026-01-01T00:00:00.000Z',
        connection_id: 104,
        is_pinned: true,
        order_position: 0,
        added_at: '2026-01-01T00:00:00.000Z'
      },
      {
        id: 5,
        name: 'Pinned 5',
        photo: '',
        url_gift: '',
        price: 5,
        currency: 'USD',
        description: '',
        is_booked: false,
        status_is_finished: false,
        created_at: '2026-01-01T00:00:00.000Z',
        updated_at: '2026-01-01T00:00:00.000Z',
        connection_id: 105,
        is_pinned: true,
        order_position: 0,
        added_at: '2026-01-01T00:00:00.000Z'
      },
      {
        id: 6,
        name: 'Not Pinned',
        photo: '',
        url_gift: '',
        price: 6,
        currency: 'USD',
        description: '',
        is_booked: false,
        status_is_finished: false,
        created_at: '2026-01-01T00:00:00.000Z',
        updated_at: '2026-01-01T00:00:00.000Z',
        connection_id: 106,
        is_pinned: false,
        order_position: 0,
        added_at: '2026-01-01T00:00:00.000Z'
      }
    ];

    global.fetch.mockImplementation(async (url, options = {}) => {
      const method = options.method || 'GET';

      if (url === '/api/v1/wishes/finish?is_finish=false' && method === 'GET') {
        return okJson([]);
      }

      if (url === '/api/v1/wishlists/10/wishes?limit=50' && method === 'GET') {
        return okJson(wishlistWishes);
      }

      if (url === '/api/v1/wishlists/10' && method === 'GET') {
        return okJson({
          id: 10,
          owner_id: 1,
          owner_name: 'Owner',
          owner_photo: '',
          name: 'Wishlist 10',
          photo: '',
          description: '',
          typeprivacy: 'public',
          wishes_count: 6
        });
      }

      if (url === '/api/v1/users/me' && method === 'GET') {
        return okJson({ id: 1 });
      }

      throw new Error(`Unexpected fetch call: ${url} (${method})`);
    });

    const { container } = renderScreen({
      token: 'token-123',
      wishlistId: '10',
      isExternalWishlist: false
    });

    await waitFor(() => {
      expect(container.querySelectorAll('.wish-card')).toHaveLength(6);
    });

    const unpinnedButton = Array.from(container.querySelectorAll('.pin-button')).find(
      (button) => !button.classList.contains('pinned')
    );

    await fireEvent.click(unpinnedButton);

    await waitFor(() => {
      expect(container.querySelector('.notification-overlay')).toBeTruthy();
    });

    const pinUpdateCall = global.fetch.mock.calls.find(
      ([url]) => typeof url === 'string' && url.includes('/api/v1/wishlists/connections/')
    );
    expect(pinUpdateCall).toBeUndefined();
  });

  test('opens add-existing modal and adds selected wish to wishlist', async () => {
    let wishlistLoadCount = 0;

    global.fetch.mockImplementation(async (url, options = {}) => {
      const method = options.method || 'GET';

      if (url === '/api/v1/wishes/finish?is_finish=false' && method === 'GET') {
        return okJson([
          {
            id: 100,
            name: 'Available Wish',
            photo: '',
            url_gift: '',
            price: 77,
            currency: 'USD',
            is_booked: false
          }
        ]);
      }

      if (url === '/api/v1/wishlists/10/wishes?limit=50' && method === 'GET') {
        wishlistLoadCount += 1;
        if (wishlistLoadCount >= 3) {
          return okJson([
            {
              id: 100,
              name: 'Available Wish',
              photo: '',
              url_gift: '',
              price: 77,
              currency: 'USD',
              description: '',
              is_booked: false,
              status_is_finished: false,
              created_at: '2026-01-01T00:00:00.000Z',
              updated_at: '2026-01-01T00:00:00.000Z',
              connection_id: 300,
              is_pinned: false,
              order_position: 0,
              added_at: '2026-01-01T00:00:00.000Z'
            }
          ]);
        }
        return okJson([]);
      }

      if (url === '/api/v1/wishlists/10' && method === 'GET') {
        return okJson({
          id: 10,
          owner_id: 1,
          owner_name: 'Owner',
          owner_photo: '',
          name: 'Wishlist 10',
          photo: '',
          description: '',
          typeprivacy: 'public',
          wishes_count: 0
        });
      }

      if (url === '/api/v1/users/me' && method === 'GET') {
        return okJson({ id: 1 });
      }

      if (url === '/api/v1/wishlists/10/wishes' && method === 'POST') {
        return okJson({
          id: 500,
          wish_id: 100,
          wishlist_id: 10,
          is_pinned: false,
          order_position: 0,
          created_at: '2026-01-01T00:00:00.000Z',
          updated_at: '2026-01-01T00:00:00.000Z'
        });
      }

      throw new Error(`Unexpected fetch call: ${url} (${method})`);
    });

    const { container } = renderScreen({
      token: 'token-123',
      wishlistId: '10',
      isExternalWishlist: false
    });

    await waitFor(() => {
      expect(container.querySelector('.ui-button.full')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.ui-button.full'));

    await waitFor(() => {
      expect(container.querySelector('.modal-content')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.wish-selection-item'));
    await fireEvent.click(container.querySelectorAll('.modal-footer .ui-button')[1]);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/wishlists/10/wishes',
        expect.objectContaining({ method: 'POST' })
      );
    });
  });

  test('handles external wishlist actions: share, reserve, subscribe and unsubscribe', async () => {
    let subscriptionState = false;
    wishlistsStore.set([
      {
        id: '20',
        title: 'External Public',
        privacy: 'public',
        count: 1,
        photo: '',
        description: ''
      }
    ]);

    global.fetch.mockImplementation(async (url, options = {}) => {
      const method = options.method || 'GET';

      if (url === '/api/v1/wishes/finish?is_finish=false' && method === 'GET') {
        return okJson([]);
      }

      if (url === '/api/v1/wishlists/20/wishes?limit=50' && method === 'GET') {
        return okJson([
          {
            id: 1,
            name: 'External Wish',
            photo: '',
            url_gift: '',
            price: 30,
            currency: 'USD',
            description: '',
            is_booked: false,
            status_is_finished: false,
            created_at: '2026-01-01T00:00:00.000Z',
            updated_at: '2026-01-01T00:00:00.000Z',
            connection_id: 555,
            is_pinned: false,
            order_position: 0,
            added_at: '2026-01-01T00:00:00.000Z'
          }
        ]);
      }

      if (url === '/api/v1/subscriptions/check/wishlist/20' && method === 'GET') {
        return okJson({ is_subscribed: subscriptionState });
      }

      if (url === '/api/v1/wishlists/20' && method === 'GET') {
        return okJson({
          id: 20,
          owner_id: 2,
          owner_name: 'Owner',
          owner_photo: '',
          name: 'External Public',
          photo: '',
          description: 'desc',
          typeprivacy: 'public',
          wishes_count: 1
        });
      }

      if (url === '/api/v1/users/me' && method === 'GET') {
        return okJson({ id: 1 });
      }

      if (url === '/api/v1/reservations/' && method === 'POST') {
        return okJson({
          wish_wishlist_id: 555,
          reserved_by_id: 99,
          created_at: '2026-01-01T00:00:00.000Z'
        });
      }

      if (url === '/api/v1/subscriptions/wishlists' && method === 'POST') {
        subscriptionState = true;
        return okJson({ message: 'subscribed' });
      }

      if (url === '/api/v1/subscriptions/wishlists/20' && method === 'DELETE') {
        subscriptionState = false;
        return okJson({ message: 'unsubscribed' });
      }

      throw new Error(`Unexpected fetch call: ${url} (${method})`);
    });

    const { container } = render(WishesScreenEventHarness, {
      token: 'token-123',
      wishlistId: '20',
      isExternalWishlist: true,
      currentUserId: '1',
      onNavigateToCreateWishes: jest.fn()
    });

    await waitFor(() => {
      expect(container.querySelector('.reservation-button')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.share-button'));
    const eventNames = Array.from(container.querySelectorAll('[data-testid="events-log"] li')).map(
      (node) => node.textContent
    );
    expect(eventNames[0]).toContain('shareWishlist:');
    expect(eventNames[0]).toContain('"id":20');

    await fireEvent.click(container.querySelector('.reservation-button'));

    await waitFor(() => {
      expect(container.querySelector('.reservation-button.reserved')).toBeTruthy();
    });

    const subscribeButton = container.querySelector('.ui-button.full');

    await fireEvent.click(subscribeButton);
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/subscriptions/wishlists',
        expect.objectContaining({ method: 'POST' })
      );
    });

    await fireEvent.click(subscribeButton);
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/subscriptions/wishlists/20',
        expect.objectContaining({ method: 'DELETE' })
      );
    });
  });

  test('opens remove-from-wishlist modal and confirms removal', async () => {
    global.fetch.mockImplementation(async (url, options = {}) => {
      const method = options.method || 'GET';

      if (url === '/api/v1/wishes/finish?is_finish=false' && method === 'GET') {
        return okJson([]);
      }

      if (url === '/api/v1/wishlists/10/wishes?limit=50' && method === 'GET') {
        return okJson([
          {
            id: 1,
            name: 'Wish In WL',
            photo: '',
            url_gift: '',
            price: 20,
            currency: 'USD',
            description: '',
            is_booked: false,
            status_is_finished: false,
            created_at: '2026-01-01T00:00:00.000Z',
            updated_at: '2026-01-01T00:00:00.000Z',
            connection_id: 333,
            is_pinned: false,
            order_position: 0,
            added_at: '2026-01-01T00:00:00.000Z'
          }
        ]);
      }

      if (url === '/api/v1/wishlists/10' && method === 'GET') {
        return okJson({
          id: 10,
          owner_id: 1,
          owner_name: 'Owner',
          owner_photo: '',
          name: 'Wishlist 10',
          photo: '',
          description: '',
          typeprivacy: 'public',
          wishes_count: 1
        });
      }

      if (url === '/api/v1/users/me' && method === 'GET') {
        return okJson({ id: 1 });
      }

      if (url === '/api/v1/wishes/1' && method === 'GET') {
        return okJson({
          id: 1,
          name: 'Wish In WL',
          photo: '',
          description: 'desc',
          price: 20,
          currency: 'USD',
          url_gift: '',
          wishlists: [{ id: 10, name: 'Wishlist 10' }],
          is_booked: false,
          status_is_finished: false,
          created_at: '2026-01-01T00:00:00.000Z',
          updated_at: '2026-01-01T00:00:00.000Z',
          user_id: 1
        });
      }

      if (url === '/api/v1/wishlists/10/wishes/1' && method === 'DELETE') {
        return okJson({ success: true });
      }

      throw new Error(`Unexpected fetch call: ${url} (${method})`);
    });

    const { container } = renderScreen({
      token: 'token-123',
      wishlistId: '10',
      isExternalWishlist: false,
      currentUserId: '1'
    });

    await waitFor(() => {
      expect(container.querySelector('.wish-card')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.wish-card'));

    await waitFor(() => {
      expect(container.querySelector('.detail-panel')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.panel-actions .ui-button.danger'));

    await waitFor(() => {
      expect(container.querySelector('.confirm-delete-modal')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.confirm-delete-modal .ui-button.danger'));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/wishlists/10/wishes/1',
        expect.objectContaining({ method: 'DELETE' })
      );
    });
  });

  test('toggles pin state in wishlist mode when pin limit is not exceeded', async () => {
    let wishlistFetchCount = 0;

    global.fetch.mockImplementation(async (url, options = {}) => {
      const method = options.method || 'GET';

      if (url === '/api/v1/wishes/finish?is_finish=false' && method === 'GET') {
        return okJson([]);
      }

      if (url === '/api/v1/wishlists/10/wishes?limit=50' && method === 'GET') {
        wishlistFetchCount += 1;
        return okJson([
          {
            id: 1,
            name: 'Pin Candidate',
            photo: '',
            url_gift: '',
            price: 20,
            currency: 'USD',
            description: '',
            is_booked: false,
            status_is_finished: false,
            created_at: '2026-01-01T00:00:00.000Z',
            updated_at: '2026-01-01T00:00:00.000Z',
            connection_id: 321,
            is_pinned: wishlistFetchCount > 1,
            order_position: 0,
            added_at: '2026-01-01T00:00:00.000Z'
          }
        ]);
      }

      if (url === '/api/v1/wishlists/10' && method === 'GET') {
        return okJson({
          id: 10,
          owner_id: 1,
          owner_name: 'Owner',
          owner_photo: '',
          name: 'Wishlist 10',
          photo: '',
          description: '',
          typeprivacy: 'public',
          wishes_count: 1
        });
      }

      if (url === '/api/v1/users/me' && method === 'GET') {
        return okJson({ id: 1 });
      }

      if (url === '/api/v1/wishlists/connections/321' && method === 'PUT') {
        return okJson({
          id: 321,
          wish_id: 1,
          wishlist_id: 10,
          is_pinned: true,
          order_position: 0,
          created_at: '2026-01-01T00:00:00.000Z',
          updated_at: '2026-01-01T00:00:00.000Z'
        });
      }

      throw new Error(`Unexpected fetch call: ${url} (${method})`);
    });

    const { container } = renderScreen({
      token: 'token-123',
      wishlistId: '10',
      isExternalWishlist: false
    });

    await waitFor(() => {
      expect(container.querySelector('.pin-button')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.pin-button'));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/wishlists/connections/321',
        expect.objectContaining({ method: 'PUT' })
      );
    });
  });

  test('shows notification when external wishlist subscription request fails', async () => {
    global.fetch.mockImplementation(async (url, options = {}) => {
      const method = options.method || 'GET';

      if (url === '/api/v1/wishes/finish?is_finish=false' && method === 'GET') {
        return okJson([]);
      }

      if (url === '/api/v1/wishlists/20/wishes?limit=50' && method === 'GET') {
        return okJson([]);
      }

      if (url === '/api/v1/subscriptions/check/wishlist/20' && method === 'GET') {
        return okJson({ is_subscribed: false });
      }

      if (url === '/api/v1/wishlists/20' && method === 'GET') {
        return okJson({
          id: 20,
          owner_id: 2,
          owner_name: 'Owner',
          owner_photo: '',
          name: 'External Public',
          photo: '',
          description: 'desc',
          typeprivacy: 'public',
          wishes_count: 0
        });
      }

      if (url === '/api/v1/users/me' && method === 'GET') {
        return okJson({ id: 1 });
      }

      if (url === '/api/v1/subscriptions/wishlists' && method === 'POST') {
        return {
          ok: false,
          status: 500,
          json: async () => ({}),
          text: async () => 'server error'
        };
      }

      throw new Error(`Unexpected fetch call: ${url} (${method})`);
    });

    const { container } = renderScreen({
      token: 'token-123',
      wishlistId: '20',
      isExternalWishlist: true
    });

    await waitFor(() => {
      expect(container.querySelector('.ui-button.full')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.ui-button.full'));

    await waitFor(() => {
      expect(container.querySelector('.notification-overlay')).toBeTruthy();
    });
  });

  test('does not mark wish as finished when confirmation is cancelled', async () => {
    global.confirm.mockReturnValue(false);

    global.fetch.mockImplementation(async (url, options = {}) => {
      const method = options.method || 'GET';

      if (url === '/api/v1/wishes/finish?is_finish=false' && method === 'GET') {
        return okJson([
          {
            id: 1,
            name: 'Cancelable Finish',
            photo: '',
            url_gift: '',
            price: 10,
            currency: 'USD',
            is_booked: false
          }
        ]);
      }

      if (url === '/api/v1/wishes/1' && method === 'GET') {
        return okJson({
          id: 1,
          name: 'Cancelable Finish',
          photo: '',
          description: '',
          price: 10,
          currency: 'USD',
          url_gift: '',
          wishlists: [],
          is_booked: false,
          status_is_finished: false,
          created_at: '2026-01-01T00:00:00.000Z',
          updated_at: '2026-01-01T00:00:00.000Z',
          user_id: 1
        });
      }

      throw new Error(`Unexpected fetch call: ${url} (${method})`);
    });

    const { container } = renderScreen({
      token: 'token-123',
      currentUserId: '1'
    });

    await waitFor(() => {
      expect(container.querySelector('.wish-card')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.wish-card'));

    await waitFor(() => {
      expect(container.querySelector('.detail-panel')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.detail-section .ui-button.full'));

    expect(global.confirm).toHaveBeenCalled();

    const updateCalls = global.fetch.mock.calls.filter(
      ([url, options = {}]) => url === '/api/v1/wishes/1' && (options.method || 'GET') === 'PUT'
    );
    expect(updateCalls).toHaveLength(0);
  });

  test('does not open add-existing modal without token in wishlist mode', async () => {
    wishlistsStore.set([
      {
        id: '10',
        title: 'Wishlist 10',
        privacy: 'public',
        count: 0,
        photo: ''
      }
    ]);

    const { container } = renderScreen({
      token: '',
      wishlistId: '10',
      isExternalWishlist: false
    });

    await waitFor(() => {
      expect(container.querySelector('.ui-button.full')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.ui-button.full'));

    expect(console.error).toHaveBeenCalled();
    expect(container.querySelector('.modal-content')).toBeNull();
  });
});
