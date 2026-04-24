import { jest } from '@jest/globals';
import { cleanup, fireEvent, render, waitFor } from '@testing-library/svelte';

import SubscriptionsScreen from '../SubscriptionsScreen.svelte';
import SubscriptionsScreenEventHarness from './SubscriptionsScreenEventHarness.svelte';
import { subscriptionsStore } from '../../../../types/subscription.ts';

const okJson = (data) => ({
  ok: true,
  status: 200,
  json: async () => data,
  text: async () => JSON.stringify(data)
});

const failJson = (status = 500, data = { detail: 'error' }) => ({
  ok: false,
  status,
  json: async () => data,
  text: async () => JSON.stringify(data)
});

function renderScreen(props = {}) {
  return render(SubscriptionsScreen, {
    token: 'token-123',
    ...props
  });
}

describe('SubscriptionsScreen', () => {
  beforeEach(() => {
    subscriptionsStore.set([]);
    global.fetch = jest.fn();
    global.alert = jest.fn();
    global.confirm = jest.fn(() => true);

    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
  });

  test('shows auth error when token is missing', async () => {
    const { container } = renderScreen({ token: '' });

    await waitFor(() => {
      expect(container.querySelector('.error-message')).toBeTruthy();
    });

    expect(global.fetch).not.toHaveBeenCalled();
  });

  test('loads and renders user and wishlist subscriptions', async () => {
    global.fetch.mockResolvedValue(
      okJson({
        subscriptions: [
          {
            type: 'user',
            sub_id: 1,
            user_id: 11,
            name: 'Alice Wonder',
            birth_date: '1990-03-05',
            photo: ''
          },
          {
            type: 'wishlist',
            sub_id: 2,
            wishlist_id: 77,
            name: 'Travel Wishlist',
            owner_name: 'Max Owner',
            total_wishes: 1,
            photo: ''
          }
        ]
      })
    );

    const { container } = renderScreen();

    await waitFor(() => {
      expect(container.querySelectorAll('.subscription-card')).toHaveLength(2);
    });

    expect(container.textContent).toContain('Alice Wonder');
    expect(container.textContent).toContain('Travel Wishlist');
    expect(container.textContent).toContain('05.03.1990');

    expect(container.querySelector('.cover-placeholder')).toBeTruthy();
  });

  test('filters by search and sorts by selected mode', async () => {
    global.fetch.mockResolvedValue(
      okJson({
        subscriptions: [
          {
            type: 'user',
            sub_id: 1,
            user_id: 101,
            name: 'Old User',
            birth_date: '1980-01-01',
            photo: ''
          },
          {
            type: 'user',
            sub_id: 2,
            user_id: 102,
            name: 'Young User',
            birth_date: '2000-01-01',
            photo: ''
          },
          {
            type: 'user',
            sub_id: 3,
            user_id: 103,
            name: 'No Date User',
            birth_date: null,
            photo: ''
          },
          {
            type: 'wishlist',
            sub_id: 4,
            wishlist_id: 201,
            name: 'Wishlist Y',
            owner_name: 'Owner Y',
            total_wishes: 2,
            photo: ''
          }
        ]
      })
    );

    const { container } = renderScreen();

    await waitFor(() => {
      expect(container.querySelectorAll('.subscription-card')).toHaveLength(4);
    });

    const searchInput = container.querySelector('input[type="text"]');
    await fireEvent.input(searchInput, { target: { value: 'owner y' } });

    await waitFor(() => {
      expect(container.querySelectorAll('.subscription-card')).toHaveLength(1);
    });

    await fireEvent.input(searchInput, { target: { value: '' } });

    await fireEvent.click(container.querySelector('input[value="users"]'));
    await waitFor(() => {
      expect(container.querySelectorAll('.subscription-card')).toHaveLength(3);
    });

    await fireEvent.click(container.querySelector('input[value="wishlists"]'));
    await waitFor(() => {
      expect(container.querySelectorAll('.subscription-card')).toHaveLength(1);
    });

    await fireEvent.click(container.querySelector('input[value="birth_date_asc"]'));
    await waitFor(() => {
      const names = Array.from(container.querySelectorAll('.subscription-title')).map((node) =>
        node.textContent.trim()
      );
      expect(names.slice(0, 3)).toEqual(['Old User', 'Young User', 'No Date User']);
    });

    await fireEvent.click(container.querySelector('input[value="birth_date_desc"]'));
    await waitFor(() => {
      const names = Array.from(container.querySelectorAll('.subscription-title')).map((node) =>
        node.textContent.trim()
      );
      expect(names.slice(0, 3)).toEqual(['Young User', 'Old User', 'No Date User']);
    });
  });

  test('dispatches open-profile and openWishlistDetail events', async () => {
    global.fetch.mockResolvedValue(
      okJson({
        subscriptions: [
          {
            type: 'user',
            sub_id: 1,
            user_id: 31,
            name: 'Event User',
            birth_date: '1991-01-01',
            photo: ''
          },
          {
            type: 'wishlist',
            sub_id: 2,
            wishlist_id: 91,
            name: 'Event Wishlist',
            owner_name: 'Owner',
            total_wishes: 5,
            photo: ''
          }
        ]
      })
    );

    const { container } = render(SubscriptionsScreenEventHarness, {
      token: 'token-123'
    });

    await waitFor(() => {
      expect(container.querySelectorAll('.subscription-card')).toHaveLength(2);
    });

    const cards = container.querySelectorAll('.subscription-card');
    const arrows = container.querySelectorAll('.arrow-button');

    await fireEvent.click(cards[0]);
    await fireEvent.click(arrows[1]);

    const eventNames = Array.from(container.querySelectorAll('[data-testid="events-log"] li')).map(
      (node) => node.textContent
    );

    expect(eventNames).toEqual([
      'open-profile:{"profileId":31}',
      'openWishlistDetail:{"wishlistId":91}'
    ]);
  });

  test('handles unsubscribe actions for user and wishlist', async () => {
    global.fetch.mockImplementation(async (url, options = {}) => {
      const method = options.method || 'GET';

      if (url === '/api/v1/subscriptions/my?limit=100' && method === 'GET') {
        return okJson({
          subscriptions: [
            {
              type: 'user',
              sub_id: 1,
              user_id: 11,
              name: 'User For Delete',
              birth_date: '1990-01-01',
              photo: ''
            },
            {
              type: 'wishlist',
              sub_id: 2,
              wishlist_id: 22,
              name: 'Wishlist For Delete',
              owner_name: 'Owner',
              total_wishes: 3,
              photo: ''
            }
          ]
        });
      }

      if (url === '/api/v1/subscriptions/users/11' && method === 'DELETE') {
        return okJson({ message: 'ok' });
      }

      if (url === '/api/v1/subscriptions/wishlists/22' && method === 'DELETE') {
        return okJson({ message: 'ok' });
      }

      throw new Error(`Unexpected fetch call: ${url} (${method})`);
    });

    const { container } = renderScreen();

    await waitFor(() => {
      expect(container.querySelectorAll('.unsubscribe-button')).toHaveLength(2);
    });

    const [userUnsubscribe, wishlistUnsubscribe] = container.querySelectorAll('.unsubscribe-button');

    global.confirm.mockReturnValueOnce(false);
    await fireEvent.click(userUnsubscribe);

    expect(global.fetch).not.toHaveBeenCalledWith(
      '/api/v1/subscriptions/users/11',
      expect.objectContaining({ method: 'DELETE' })
    );

    global.confirm.mockReturnValueOnce(true);
    await fireEvent.click(userUnsubscribe);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/subscriptions/users/11',
        expect.objectContaining({ method: 'DELETE' })
      );
    });

    global.confirm.mockReturnValueOnce(true);
    await fireEvent.click(wishlistUnsubscribe);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/subscriptions/wishlists/22',
        expect.objectContaining({ method: 'DELETE' })
      );
    });
  });

  test('shows error message when loading fails', async () => {
    global.fetch.mockResolvedValue(failJson(500));
    const { container } = renderScreen();

    await waitFor(() => {
      expect(container.querySelector('.error-message')).toBeTruthy();
    });
  });
});
