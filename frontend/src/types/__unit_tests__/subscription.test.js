import { jest } from '@jest/globals';
import {
  checkWishlistSubscription,
  getMyUserSubscriptions,
  isUserSubscription,
  isWishlistSubscription,
  subscribeToUser,
  userSubscriptionsStore
} from '../subscription.ts';

const jsonResponse = (data, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => data,
  text: async () => JSON.stringify(data)
});

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

  test('type guards detect user and wishlist subscription items', async () => {
    expect(isUserSubscription({ type: 'user', user_id: 1, name: 'Alice' })).toBe(true);
    expect(isUserSubscription({ type: 'wishlist', wishlist_id: 2, name: 'Books' })).toBe(false);
    expect(isWishlistSubscription({ type: 'wishlist', wishlist_id: 2, name: 'Books' })).toBe(true);
    expect(isWishlistSubscription({ type: 'user', user_id: 1, name: 'Alice' })).toBe(false);
  });
});
