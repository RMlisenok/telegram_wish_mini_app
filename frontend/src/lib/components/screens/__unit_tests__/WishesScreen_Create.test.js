import { jest } from '@jest/globals';
import { cleanup, fireEvent, render, waitFor } from '@testing-library/svelte';

import WishesScreenCreate from '../WishesScreen_Create.svelte';
import { wishlistsStore } from '../../../../types/wishlists.ts';

const jsonResponse = (data, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => data
});

describe('WishesScreen_Create', () => {
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

    const { container } = render(WishesScreenCreate, {
      token: '',
      onGoBack
    });

    const actionButtons = container.querySelectorAll('.form-actions .ui-button');
    const saveButton = actionButtons[1];

    await fireEvent.click(saveButton);

    expect(container.querySelector('.field-error')).toBeTruthy();
    expect(global.fetch).not.toHaveBeenCalled();
    expect(onGoBack).not.toHaveBeenCalled();
  });
  
  test('loads wishlists on mount when token is provided', async () => {
    global.fetch.mockResolvedValue(
      jsonResponse([
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
          wishes_count: 1
        }
      ])
    );

    const { container } = render(WishesScreenCreate, {
      token: 'token-123',
      onGoBack: jest.fn()
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/wishlists/',
        expect.objectContaining({ method: 'GET' })
      );
    });

    await waitFor(() => {
      expect(container.querySelectorAll('.wishlist-checkbox')).toHaveLength(2);
    });
  });
});
