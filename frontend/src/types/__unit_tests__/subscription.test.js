import { jest } from '@jest/globals';
import { get } from 'svelte/store';
import {
  checkWishlistSubscription,
  getMyUserSubscriptions,
  isUserSubscription,
  isWishlistSubscription,
  subscribeToUser,
  checkUserSubscription,
  getMySubscribers,
  getMySubscriptions,
  getMyWishlistSubscriptions,
  getUserSubscriptions,
  subscribeToWishlist,
  subscribersStore,
  subscriptionsStore,
  unsubscribeFromUser,
  unsubscribeFromWishlist,
  userSubscriptionsStore,
  visitSubscribe,
  wishlistSubscriptionsStore
} from '../subscription.ts';

const jsonResponse = (data, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => data,
  text: async () => JSON.stringify(data)
});

const messageOk = { message: 'ok' };

describe('types/subscription', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    userSubscriptionsStore.set([]);
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('subscribeToUser posts target user id', async () => {
    global.fetch.mockResolvedValue(jsonResponse({ message: 'ok' }));

    await subscribeToUser('token-123', 77);

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/subscriptions/users',
      expect.objectContaining({ method: 'POST' })
    );
    expect(JSON.parse(global.fetch.mock.calls[0][1].body)).toEqual({ target_user_id: 77 });
  });

  test('getMyUserSubscriptions filters only user subscriptions into store', async () => {
    global.fetch.mockResolvedValue(
      jsonResponse({
        subscriptions: [
          { type: 'user', user_id: 10, name: 'Alice' },
          { type: 'wishlist', wishlist_id: 11, name: 'Books' }
        ],
        total: 2
      })
    );

    await getMyUserSubscriptions('token-123', 5);

    let currentValue;
    userSubscriptionsStore.subscribe((value) => {
      currentValue = value;
    })();

    expect(currentValue).toEqual([{ type: 'user', user_id: 10, name: 'Alice' }]);
  });

  test('checkWishlistSubscription returns false when request fails', async () => {
    global.fetch.mockResolvedValue(jsonResponse({}, false, 500));

    await expect(checkWishlistSubscription('token-123', 99)).resolves.toBe(false);
  });

  test('subscribeToUser throws specific message for status 400 and generic message otherwise', async () => {
    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 400));
    await expect(subscribeToUser('token-123', 77)).rejects.toThrow(
        'Невозможно подписаться на этого пользователя'
    );

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(subscribeToUser('token-123', 77)).rejects.toThrow('Ошибка подписки');
  });

  test('subscribeToWishlist posts target wishlist id and handles failures', async () => {
    global.fetch.mockResolvedValueOnce(jsonResponse(messageOk));

    await expect(subscribeToWishlist('token-123', 55)).resolves.toEqual(messageOk);
    expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/subscriptions/wishlists',
        expect.objectContaining({ method: 'POST' })
    );
    expect(JSON.parse(global.fetch.mock.calls[0][1].body)).toEqual({ target_wishlist_id: 55 });

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 400));
    await expect(subscribeToWishlist('token-123', 55)).rejects.toThrow(
        'Невозможно подписаться на этот вишлист'
    );

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(subscribeToWishlist('token-123', 55)).rejects.toThrow('Ошибка подписки');
  });

  test('visitSubscribe patches visit status and handles error statuses', async () => {
    const visitResult = { status: true, updated_at: '2026-01-01T00:00:00.000Z' };
    global.fetch.mockResolvedValueOnce(jsonResponse(visitResult));

    await expect(visitSubscribe('token-123', 9)).resolves.toEqual(visitResult);
    expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/subscriptions/visit/9',
        expect.objectContaining({ method: 'PATCH' })
    );

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 400));
    await expect(visitSubscribe('token-123', 9)).rejects.toThrow('Подписка не найдена');

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(visitSubscribe('token-123', 9)).rejects.toThrow('Ошибка обновления посещения');
  });

  test('unsubscribe functions send DELETE requests and expose not-found errors', async () => {
    global.fetch.mockResolvedValueOnce(jsonResponse(messageOk));
    await expect(unsubscribeFromUser('token-123', 12)).resolves.toEqual(messageOk);
    expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/subscriptions/users/12',
        expect.objectContaining({ method: 'DELETE' })
    );

    global.fetch.mockResolvedValueOnce(jsonResponse(messageOk));
    await expect(unsubscribeFromWishlist('token-123', 34)).resolves.toEqual(messageOk);
    expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/subscriptions/wishlists/34',
        expect.objectContaining({ method: 'DELETE' })
    );

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 404));
    await expect(unsubscribeFromUser('token-123', 12)).rejects.toThrow('Подписка не найдена');

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(unsubscribeFromUser('token-123', 12)).rejects.toThrow('Ошибка отписки');

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 404));
    await expect(unsubscribeFromWishlist('token-123', 34)).rejects.toThrow('Подписка не найдена');

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(unsubscribeFromWishlist('token-123', 34)).rejects.toThrow('Ошибка отписки');
  });

  test('getMySubscriptions fetches subscriptions into common store and resets it on failure', async () => {
    const payload = {
      subscriptions: [
        { type: 'user', user_id: 10, name: 'Alice' },
        { type: 'wishlist', wishlist_id: 11, name: 'Books' }
      ],
      total: 2
    };
    global.fetch.mockResolvedValueOnce(jsonResponse(payload));

    await expect(getMySubscriptions('token-123', 5)).resolves.toEqual(payload);

    expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/subscriptions/my?limit=5',
        expect.objectContaining({ method: 'GET' })
    );
    expect(get(subscriptionsStore)).toEqual(payload.subscriptions);

    subscriptionsStore.set(payload.subscriptions);
    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(getMySubscriptions('token-123')).rejects.toThrow('Ошибка загрузки подписок');
    expect(get(subscriptionsStore)).toEqual([]);
  });

  test('getMyWishlistSubscriptions filters only wishlist subscriptions into store and resets on error', async () => {
    global.fetch.mockResolvedValueOnce(
        jsonResponse({
          subscriptions: [
            { type: 'user', user_id: 10, name: 'Alice' },
            { type: 'wishlist', wishlist_id: 11, name: 'Books' }
          ],
          total: 2
        })
    );

    await getMyWishlistSubscriptions('token-123', 7);

    expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/subscriptions/my/wishlists?limit=7',
        expect.objectContaining({ method: 'GET' })
    );
    expect(get(wishlistSubscriptionsStore)).toEqual([
      { type: 'wishlist', wishlist_id: 11, name: 'Books' }
    ]);

    wishlistSubscriptionsStore.set([{ type: 'wishlist', wishlist_id: 2, name: 'Old' }]);
    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(getMyWishlistSubscriptions('token-123')).rejects.toThrow(
        'Ошибка загрузки подписок на вишлисты'
    );
    expect(get(wishlistSubscriptionsStore)).toEqual([]);
  });

  test('getUserSubscriptions returns public user subscriptions and handles privacy error', async () => {
    const payload = { subscriptions: [{ type: 'user', user_id: 3, name: 'Sam' }], total: 1 };
    global.fetch.mockResolvedValueOnce(jsonResponse(payload));

    await expect(getUserSubscriptions('token-123', 3, 4)).resolves.toEqual(payload);
    expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/subscriptions/users/3?limit=4',
        expect.objectContaining({ method: 'GET' })
    );

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 403));
    await expect(getUserSubscriptions('token-123', 3)).rejects.toThrow(
        'Подписки этого пользователя приватны'
    );

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(getUserSubscriptions('token-123', 3)).rejects.toThrow(
        'Ошибка загрузки подписок пользователя'
    );
  });

  test('check subscription helpers return backend boolean and fall back to false on errors', async () => {
    global.fetch.mockResolvedValueOnce(jsonResponse({ is_subscribed: true }));
    await expect(checkUserSubscription('token-123', 99)).resolves.toBe(true);
    expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/subscriptions/check/user/99',
        expect.objectContaining({ method: 'GET' })
    );

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(checkUserSubscription('token-123', 99)).resolves.toBe(false);

    global.fetch.mockResolvedValueOnce(jsonResponse({ is_subscribed: false }));
    await expect(checkWishlistSubscription('token-123', 88)).resolves.toBe(false);
    expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/subscriptions/check/wishlist/88',
        expect.objectContaining({ method: 'GET' })
    );

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(checkWishlistSubscription('token-123', 88)).resolves.toBe(false);
  });

  test('getMySubscribers fetches and stores subscribers and resets store on failure', async () => {
    const payload = { subscribers: [{ type: 'user', sub_id: 1, name: 'Alice', user_id: 10 }], total: 1 };
    global.fetch.mockResolvedValueOnce(jsonResponse(payload));

    await expect(getMySubscribers('token-123', false, 5)).resolves.toEqual(payload);

    expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/subscriptions/my/subscribers?is_desc=false&limit=5',
        expect.objectContaining({ method: 'GET' })
    );
    expect(get(subscribersStore)).toEqual(payload.subscribers);

    subscribersStore.set(payload.subscribers);
    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(getMySubscribers('token-123')).rejects.toThrow('Ошибка загрузки подписчиков');
    expect(get(subscribersStore)).toEqual([]);
  });

  test('type guards detect user and wishlist subscription items', async () => {
    expect(isUserSubscription({ type: 'user', user_id: 1, name: 'Alice' })).toBe(true);
    expect(isUserSubscription({ type: 'wishlist', wishlist_id: 2, name: 'Books' })).toBe(false);
    expect(isWishlistSubscription({ type: 'wishlist', wishlist_id: 2, name: 'Books' })).toBe(true);
    expect(isWishlistSubscription({ type: 'user', user_id: 1, name: 'Alice' })).toBe(false);
  });
});
