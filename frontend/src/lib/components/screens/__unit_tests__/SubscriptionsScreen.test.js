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
});
