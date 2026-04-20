import { jest } from '@jest/globals';
import { cleanup, fireEvent, render, waitFor } from '@testing-library/svelte';

import WishlistsScreenCreate from '../WishlistsScreen_Create.svelte';

const jsonResponse = (data, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => data
});

describe('WishlistsScreen_Create', () => {
  beforeEach(() => {
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
    const { container } = render(WishlistsScreenCreate, {
      token: 'token-123',
      onGoBack
    });

    const saveButton = container.querySelectorAll('.form-actions .ui-button')[1];
    await fireEvent.click(saveButton);

    expect(container.querySelector('.field-error')).toBeTruthy();
    expect(global.fetch).not.toHaveBeenCalled();
    expect(onGoBack).not.toHaveBeenCalled();
  });

  test('saves wishlist with trimmed values and mapped privacy', async () => {
    global.fetch.mockResolvedValue(jsonResponse({ id: 'wl-10' }));
    const onGoBack = jest.fn();

    const { container } = render(WishlistsScreenCreate, {
      token: 'token-123',
      onGoBack
    });

    await fireEvent.input(container.querySelector('input[type="text"]'), {
      target: { value: '  Birthday Gifts  ' }
    });

    await fireEvent.input(container.querySelector('#description'), {
      target: { value: '  For birthday party  ' }
    });

    await fireEvent.click(container.querySelector('input[name="privacy"][value="restricted"]'));

    const saveButton = container.querySelectorAll('.form-actions .ui-button')[1];
    await fireEvent.click(saveButton);

    await waitFor(() => {
      expect(onGoBack).toHaveBeenCalledTimes(1);
    });

    const createCall = global.fetch.mock.calls.find(
      ([url, options]) => url === '/api/v1/wishlists/' && options.method === 'POST'
    );

    expect(createCall).toBeTruthy();

    const payload = JSON.parse(createCall[1].body);
    expect(payload).toMatchObject({
      name: 'Birthday Gifts',
      description: 'For birthday party',
      typeprivacy: 'protected',
      photo: ''
    });
  });
});
