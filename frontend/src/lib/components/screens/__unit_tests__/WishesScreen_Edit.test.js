import { jest } from '@jest/globals';
import { cleanup, fireEvent, render, waitFor } from '@testing-library/svelte';

import WishesScreenEdit from '../WishesScreen_Edit.svelte';
import { wishlistsStore } from '../../../../types/wishlists.ts';

const jsonResponse = (data, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => data,
  text: async () => JSON.stringify(data)
});

describe('WishesScreen_Edit', () => {
  beforeEach(() => {
    wishlistsStore.set([]);
    global.fetch = jest.fn();
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
  });

  test('shows validation error and does not save when title is empty', async () => {
    const onGoBack = jest.fn();

    const { container } = render(WishesScreenEdit, {
      token: '',
      wishId: '42',
      onGoBack
    });

    const saveButton = container.querySelectorAll('.form-actions .ui-button')[1];
    await fireEvent.click(saveButton);

    expect(container.querySelector('.field-error')).toBeTruthy();
    expect(global.fetch).not.toHaveBeenCalled();
    expect(onGoBack).not.toHaveBeenCalled();
  });

  test('loads wishlists and pre-fills form with existing wish data', async () => {
    global.fetch.mockImplementation(async (url, options = {}) => {
      const method = options.method || 'GET';

      if (url === '/api/v1/wishlists/' && method === 'GET') {
        return jsonResponse([
          {
            id: 1,
            name: 'Birthday',
            description: '',
            photo: '',
            typeprivacy: 'public',
            wishes_count: 2
          }
        ]);
      }

      if (url === '/api/v1/wishes/42' && method === 'GET') {
        return jsonResponse({
          id: 42,
          name: 'Old Lamp',
          description: 'Old description',
          url_gift: 'https://example.com/old',
          price: 500,
          currency: 'EUR',
          photo: 'https://example.com/photo.jpg',
          wishlists: [{ id: 1 }]
        });
      }

      throw new Error(`Unexpected fetch call: ${url} (${method})`);
    });

    const { container } = render(WishesScreenEdit, {
      token: 'token-123',
      wishId: '42',
      onGoBack: jest.fn()
    });

    await waitFor(() => {
      expect(container.querySelector('input[type="text"]').value).toBe('Old Lamp');
    });

    expect(container.querySelector('input[type="url"]').value).toBe('https://example.com/old');
    expect(container.querySelector('#price').value).toBe('500');
    expect(container.querySelector('#currency').value).toBe('EUR');
    expect(container.querySelector('#description').value).toBe('Old description');

    const firstWishlistCheckbox = container.querySelector('.wishlist-checkbox[value="1"]');
    expect(firstWishlistCheckbox).toBeTruthy();
    expect(firstWishlistCheckbox.checked).toBe(true);
  });

  test('saves edits and synchronizes wishlist connections', async () => {
    global.fetch.mockImplementation(async (url, options = {}) => {
      const method = options.method || 'GET';

      if (url === '/api/v1/wishlists/' && method === 'GET') {
        return jsonResponse([
          {
            id: 1,
            name: 'Birthday',
            description: '',
            photo: '',
            typeprivacy: 'public',
            wishes_count: 2
          },
          {
            id: 2,
            name: 'Travel',
            description: '',
            photo: '',
            typeprivacy: 'private',
            wishes_count: 5
          }
        ]);
      }

      if (url === '/api/v1/wishes/42' && method === 'GET') {
        return jsonResponse({
          id: 42,
          name: 'Old Lamp',
          description: 'Old description',
          url_gift: 'https://example.com/old',
          price: 500,
          currency: 'EUR',
          photo: '',
          wishlists: [{ id: 1 }]
        });
      }

      if (url === '/api/v1/wishes/42' && method === 'PUT') {
        return jsonResponse({ id: 42 });
      }

      if (url === '/api/v1/wishlists/2/wishes' && method === 'POST') {
        return jsonResponse({
          id: 100,
          wish_id: 42,
          wishlist_id: 2,
          is_pinned: false,
          order_position: 0,
          created_at: '2026-04-14T10:00:00.000Z',
          updated_at: '2026-04-14T10:00:00.000Z'
        });
      }

      if (url === '/api/v1/wishlists/1/wishes/42' && method === 'DELETE') {
        return jsonResponse({ success: true });
      }

      throw new Error(`Unexpected fetch call: ${url} (${method})`);
    });

    const onGoBack = jest.fn();

    const { container } = render(WishesScreenEdit, {
      token: 'token-123',
      wishId: '42',
      onGoBack
    });

    await waitFor(() => {
      expect(container.querySelector('input[type="text"]').value).toBe('Old Lamp');
    });

    await fireEvent.input(container.querySelector('input[type="text"]'), {
      target: { value: '  Updated Lamp  ' }
    });

    const checkboxOne = container.querySelector('.wishlist-checkbox[value="1"]');
    const checkboxTwo = container.querySelector('.wishlist-checkbox[value="2"]');

    await fireEvent.click(checkboxTwo);
    await fireEvent.click(checkboxOne);

    const saveButton = container.querySelectorAll('.form-actions .ui-button')[1];
    await fireEvent.click(saveButton);

    await waitFor(() => {
      expect(onGoBack).toHaveBeenCalledTimes(1);
    });

    const updateWishCall = global.fetch.mock.calls.find(
      ([url, opts]) => url === '/api/v1/wishes/42' && opts.method === 'PUT'
    );

    expect(updateWishCall).toBeTruthy();

    const updateWishPayload = JSON.parse(updateWishCall[1].body);
    expect(updateWishPayload.name).toBe('Updated Lamp');

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/wishlists/2/wishes',
      expect.objectContaining({ method: 'POST' })
    );

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/wishlists/1/wishes/42',
      expect.objectContaining({ method: 'DELETE' })
    );
  });
});
