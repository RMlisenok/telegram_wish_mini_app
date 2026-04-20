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

  test('uploads selected photo before creating wishlist', async () => {
    const originalFileReader = global.FileReader;

    class MockFileReader {
      readAsDataURL() {
        if (this.onload) {
          this.onload({ target: { result: 'data:image/png;base64,mock' } });
        }
      }
    }

    global.FileReader = MockFileReader;
    try {
      global.fetch.mockImplementation(async (url, options = {}) => {
        if (url === '/api/v1/s3/file/' && options.method === 'POST') {
          return jsonResponse({
            message: 'uploaded',
            filename: 'photo.png',
            file_url: 'https://selstorage.ru/files/photo.png',
            content_type: 'image/png',
            size: 4
          });
        }

        if (url === '/api/v1/wishlists/' && options.method === 'POST') {
          return jsonResponse({ id: 'wl-11' });
        }

        throw new Error(`Unexpected fetch call: ${url} (${options.method || 'GET'})`);
      });

      const onGoBack = jest.fn();

      const { container } = render(WishlistsScreenCreate, {
        token: 'token-123',
        onGoBack
      });

      await fireEvent.input(container.querySelector('input[type="text"]'), {
        target: { value: 'Wishlist with image' }
      });

      const fileInput = container.querySelector('.photo-upload-input');
      const file = new File(['test'], 'photo.png', { type: 'image/png' });
      await fireEvent.change(fileInput, { target: { files: [file] } });

      const saveButton = container.querySelectorAll('.form-actions .ui-button')[1];
      await fireEvent.click(saveButton);

      await waitFor(() => {
        expect(onGoBack).toHaveBeenCalledTimes(1);
      });

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/s3/file/',
        expect.objectContaining({ method: 'POST' })
      );

      const createCall = global.fetch.mock.calls.find(
        ([url, options]) => url === '/api/v1/wishlists/' && options.method === 'POST'
      );
      const payload = JSON.parse(createCall[1].body);
      expect(payload.photo).toBe('https://selstorage.ru/files/photo.png');
    } finally {
      global.FileReader = originalFileReader;
    }
  });
});
