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

  test('saves wish and connects it to selected wishlists', async () => {
    wishlistsStore.set([
      {
        id: '1',
        title: 'Birthday',
        privacy: 'public',
        count: 3
      }
    ]);

    global.fetch.mockImplementation(async (url, options = {}) => {
      if (url === '/api/v1/wishes/' && options.method === 'POST') {
        return jsonResponse({ id: 77, name: 'Fancy Lamp' });
      }

      if (url === '/api/v1/wishlists/1/wishes' && options.method === 'POST') {
        return jsonResponse({ id: 9001 });
      }

      throw new Error(`Unexpected fetch call: ${url} (${options.method || 'GET'})`);
    });

    const onGoBack = jest.fn();

    const { container } = render(WishesScreenCreate, {
      token: '',
      onGoBack
    });

    await fireEvent.input(container.querySelector('input[type="text"]'), {
      target: { value: '  Fancy Lamp  ' }
    });

    await fireEvent.input(container.querySelector('input[type="url"]'), {
      target: { value: '  https://example.com/gift  ' }
    });

    await fireEvent.input(container.querySelector('#price'), {
      target: { value: '1999.50' }
    });

    await fireEvent.change(container.querySelector('#currency'), {
      target: { value: 'USD' }
    });

    await fireEvent.input(container.querySelector('#description'), {
      target: { value: '  Warm bedside light  ' }
    });

    await fireEvent.click(container.querySelector('.wishlist-checkbox'));

    const saveButton = container.querySelectorAll('.form-actions .ui-button')[1];
    await fireEvent.click(saveButton);

    await waitFor(() => {
      expect(onGoBack).toHaveBeenCalledTimes(1);
    });

    const createWishCall = global.fetch.mock.calls.find(
      ([url, opts]) => url === '/api/v1/wishes/' && opts.method === 'POST'
    );

    expect(createWishCall).toBeTruthy();

    const createWishPayload = JSON.parse(createWishCall[1].body);
    expect(createWishPayload).toMatchObject({
      name: 'Fancy Lamp',
      description: 'Warm bedside light',
      price: 1999.5,
      currency: 'USD',
      url_gift: 'https://example.com/gift',
      photo: ''
    });

    const connectCall = global.fetch.mock.calls.find(
      ([url, opts]) => url === '/api/v1/wishlists/1/wishes' && opts.method === 'POST'
    );

    expect(connectCall).toBeTruthy();

    const connectPayload = JSON.parse(connectCall[1].body);
    expect(connectPayload).toMatchObject({
      wish_id: 77,
      wishlist_id: 1,
      is_pinned: false
    });
  });
});
