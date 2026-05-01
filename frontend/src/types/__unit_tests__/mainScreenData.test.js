import { jest } from '@jest/globals';
import { get } from 'svelte/store';

import {
  formatDateToDDMMYYYY,
  loadMainScreenData,
  mainSubscribersStore,
  mainSubscriptionsStore,
  mainWishlistsStore,
  totalSubscribersStore,
  totalSubscriptionsStore,
  totalWishesStore,
  totalWishlistsStore
} from '../mainScreenData.ts';

const subscribersKey = 'subsсribers';

const jsonResponse = (data, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => data,
  text: async () => JSON.stringify(data)
});

function resetStores() {
  mainWishlistsStore.set([]);
  mainSubscriptionsStore.set([]);
  mainSubscribersStore.set([]);
  totalWishesStore.set(0);
  totalWishlistsStore.set(0);
  totalSubscribersStore.set(0);
  totalSubscriptionsStore.set(0);
}

function createMainScreenPayload() {
  return {
    wishlist_last_update: [
      {
        id: 1,
        name: 'Public wishlist',
        description: 'Open list',
        photo: 'public.png',
        typeprivacy: 'public',
        created_at: '2026-01-01T00:00:00.000Z',
        updated_at: '2026-01-02T00:00:00.000Z',
        wishes_count: 3
      },
      {
        id: 2,
        name: 'Protected wishlist',
        description: 'Restricted list',
        photo: 'protected.png',
        typeprivacy: 'protected',
        created_at: '2026-01-03T00:00:00.000Z',
        updated_at: '2026-01-04T00:00:00.000Z',
        wishes_count: 5
      },
      {
        id: 3,
        name: 'Unknown privacy wishlist',
        description: 'Fallback list',
        photo: 'unknown.png',
        typeprivacy: 'secret',
        created_at: '2026-01-05T00:00:00.000Z',
        updated_at: '2026-01-06T00:00:00.000Z',
        wishes_count: 1
      }
    ],
    subscription: {
      subscription: {
        total: 2,
        subscriptions: [
          {
            type: 'user',
            name: 'Alice',
            photo: 'alice.png',
            user_id: 10,
            birth_date: '1998-02-03'
          },
          {
            type: 'wishlist',
            name: 'Books',
            photo: 'books.png',
            description: 'Book gifts',
            typeprivacy: 'private',
            owner_name: 'Bob',
            id: 20
          }
        ]
      }
    },
    [subscribersKey]: {
      total: 1,
      subscribers: [
        {
          name: 'Subscriber One',
          photo: 'sub.png',
          birth_date: '2000-12-31'
        }
      ]
    },
    total_wish: 9,
    total_wishlist: 3
  };
}

describe('types/mainScreenData', () => {
  beforeEach(() => {
    resetStores();
    global.fetch = jest.fn();
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('formatDateToDDMMYYYY formats valid date and keeps invalid values safely', () => {
    expect(formatDateToDDMMYYYY('2026-05-01')).toBe('01.05.2026');
    expect(formatDateToDDMMYYYY('2026-05')).toBe('2026-05');
    expect(formatDateToDDMMYYYY('')).toBe('');
  });

  test('loadMainScreenData stops early when token is missing', async () => {
    await expect(loadMainScreenData('')).resolves.toBeUndefined();

    expect(global.fetch).not.toHaveBeenCalled();
    expect(console.error).toHaveBeenCalledWith('Токен не предоставлен');
  });

  test('loadMainScreenData maps profile payload into stores and totals', async () => {
    global.fetch.mockResolvedValue(jsonResponse(createMainScreenPayload()));

    const result = await loadMainScreenData('token-123');

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/users/me',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({ Authorization: 'Bearer token-123' })
      })
    );

    expect(result).toMatchObject({
      totalWish: 9,
      totalWishlist: 3,
      totalSubscribers: 1,
      totalSubscription: 2
    });

    expect(get(mainWishlistsStore)).toEqual([
      expect.objectContaining({ id: '1', typeprivacy: 'public', count: 3 }),
      expect.objectContaining({ id: '2', typeprivacy: 'restricted', count: 5 }),
      expect.objectContaining({ id: '3', typeprivacy: 'private', count: 1 })
    ]);
    expect(get(mainSubscriptionsStore)).toEqual([
      expect.objectContaining({
        type_sub: true,
        user: expect.objectContaining({ name: 'Alice', birth_date: '03.02.1998' })
      }),
      expect.objectContaining({
        type_sub: false,
        wishlist: expect.objectContaining({ name: 'Books', typeprivacy: 'private' })
      })
    ]);
    expect(get(mainSubscribersStore)).toEqual([
      expect.objectContaining({ name: 'Subscriber One', birth_date: '31.12.2000' })
    ]);
    expect(get(totalWishesStore)).toBe(9);
    expect(get(totalWishlistsStore)).toBe(3);
    expect(get(totalSubscribersStore)).toBe(1);
    expect(get(totalSubscriptionsStore)).toBe(2);
  });

  test('loadMainScreenData uses zero totals when optional counters are missing', async () => {
    const payload = createMainScreenPayload();
    delete payload.total_wish;
    delete payload.total_wishlist;
    payload[subscribersKey].total = undefined;
    payload.subscription.subscription.total = undefined;
    global.fetch.mockResolvedValue(jsonResponse(payload));

    await loadMainScreenData('token-123');

    expect(get(totalWishesStore)).toBe(0);
    expect(get(totalWishlistsStore)).toBe(0);
    expect(get(totalSubscribersStore)).toBe(0);
    expect(get(totalSubscriptionsStore)).toBe(0);
  });

  test('loadMainScreenData throws when backend request fails', async () => {
    global.fetch.mockResolvedValue(jsonResponse({}, false, 500));

    await expect(loadMainScreenData('token-123')).rejects.toThrow('HTTP error! status: 500');
  });
});
