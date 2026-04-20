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
});
