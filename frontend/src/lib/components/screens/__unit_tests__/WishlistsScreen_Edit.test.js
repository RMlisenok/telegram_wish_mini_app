import { jest } from '@jest/globals';
import { cleanup, fireEvent, render, waitFor } from '@testing-library/svelte';

import WishlistsScreenEdit from '../WishlistsScreen_Edit.svelte';
import { wishlistsStore } from '../../../../types/wishlists.ts';

const jsonResponse = (data, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => data
});

describe('WishlistsScreen_Edit', () => {
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

    const { container } = render(WishlistsScreenEdit, {
      token: 'token-123',
      wishlistId: 'unknown-id',
      onGoBack
    });

    const saveButton = container.querySelectorAll('.form-actions .ui-button')[1];
    await fireEvent.click(saveButton);

    expect(container.querySelector('.field-error')).toBeTruthy();
    expect(global.fetch).not.toHaveBeenCalled();
    expect(onGoBack).not.toHaveBeenCalled();
  });

  test('loads existing wishlist data from store and saves mapped payload', async () => {
    wishlistsStore.set([
      {
        id: 'wl-1',
        title: 'Old title',
        description: 'Old description',
        photo: '',
        privacy: 'private',
        count: 0
      }
    ]);

    global.fetch.mockResolvedValue(jsonResponse({ id: 'wl-1' }));
    const onGoBack = jest.fn();

    const { container } = render(WishlistsScreenEdit, {
      token: 'token-123',
      wishlistId: 'wl-1',
      onGoBack
    });

    await waitFor(() => {
      expect(container.querySelector('input[type="text"]').value).toBe('Old title');
    });

    expect(container.querySelector('#description').value).toBe('Old description');

    await fireEvent.input(container.querySelector('input[type="text"]'), {
      target: { value: '  Updated title  ' }
    });
    await fireEvent.input(container.querySelector('#description'), {
      target: { value: '  Updated description  ' }
    });
    await fireEvent.click(container.querySelector('input[name="privacy"][value="restricted"]'));

    const saveButton = container.querySelectorAll('.form-actions .ui-button')[1];
    await fireEvent.click(saveButton);

    await waitFor(() => {
      expect(onGoBack).toHaveBeenCalledTimes(1);
    });

    const updateCall = global.fetch.mock.calls.find(
      ([url, options]) => url === '/api/v1/wishlists/wl-1' && options.method === 'PUT'
    );

    expect(updateCall).toBeTruthy();

    const payload = JSON.parse(updateCall[1].body);
    expect(payload).toMatchObject({
      name: 'Updated title',
      description: 'Updated description',
      typeprivacy: 'protected',
      photo: ''
    });
  });
});
