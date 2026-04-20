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

  test('uploads a new photo and saves updated wishlist with uploaded URL', async () => {
    const originalFileReader = global.FileReader;

    class MockFileReader {
      readAsDataURL() {
        if (this.onload) {
          this.onload({ target: { result: 'data:image/png;base64,new' } });
        }
      }
    }

    global.FileReader = MockFileReader;
    try {
      wishlistsStore.set([
        {
          id: 'wl-2',
          title: 'Travel',
          description: 'Trips',
          photo: 'https://selstorage.ru/files/wishlist-photo.png',
          privacy: 'public',
          count: 0
        }
      ]);

      global.fetch.mockImplementation(async (url, options = {}) => {
        if (url === '/api/v1/s3/file/' && options.method === 'POST') {
          return jsonResponse({
            message: 'uploaded',
            filename: 'new-photo.png',
            file_url: 'https://selstorage.ru/files/new-photo.png',
            content_type: 'image/png',
            size: 4
          });
        }

        if (url === '/api/v1/wishlists/wl-2' && options.method === 'PUT') {
          return jsonResponse({ id: 'wl-2' });
        }

        throw new Error(`Unexpected fetch call: ${url} (${options.method || 'GET'})`);
      });

      const onGoBack = jest.fn();

      const { container } = render(WishlistsScreenEdit, {
        token: 'token-123',
        wishlistId: 'wl-2',
        onGoBack
      });

      await waitFor(() => {
        expect(container.querySelector('.photo-preview img')).toBeTruthy();
      });

      await fireEvent.click(container.querySelector('.photo-preview .ui-button'));

      const file = new File(['new'], 'new-photo.png', { type: 'image/png' });
      await waitFor(() => {
        expect(container.querySelector('.photo-upload-input')).toBeTruthy();
      });

      const fileInput = container.querySelector('.photo-upload-input');
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

      const updateCall = global.fetch.mock.calls.find(
        ([url, options]) => url === '/api/v1/wishlists/wl-2' && options.method === 'PUT'
      );
      expect(updateCall).toBeTruthy();
      expect(JSON.parse(updateCall[1].body).photo).toBe(
        'https://selstorage.ru/files/new-photo.png'
      );
    } finally {
      global.FileReader = originalFileReader;
    }
  });
});
