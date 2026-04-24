import { jest } from '@jest/globals';
import { cleanup, fireEvent, render, waitFor } from '@testing-library/svelte';

import WishlistsScreen from '../WishlistsScreen.svelte';
import WishlistsScreenEventHarness from './WishlistsScreenEventHarness.svelte';
import { wishlistsStore } from '../../../../types/wishlists.ts';
import { wishesStore } from '../../../stores/data.js';

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

function getStoreValue(store) {
  let value;
  const unsubscribe = store.subscribe((v) => {
    value = v;
  });
  unsubscribe();
  return value;
}

function renderScreen(props = {}) {
  return render(WishlistsScreen, {
    token: 'token-123',
    isExternalUser: false,
    externalProfileId: null,
    externalUserWishlists: [],
    ...props
  });
}

describe('WishlistsScreen', () => {
  beforeEach(() => {
    wishlistsStore.set([]);
    wishesStore.set([]);

    global.fetch = jest.fn();
    global.alert = jest.fn();

    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
  });

  test('renders external wishlists and dispatches external navigation events', async () => {
    const externalUserWishlists = [
      {
        id: '1',
        title: 'Public External',
        typeprivacy: 'public',
        count: 1,
        ownerId: '501',
        ownerName: 'Owner One',
        photo: ''
      },
      {
        id: '2',
        title: 'Friends External',
        privacy: 'restricted',
        count: 2,
        ownerName: '',
        photo: ''
      },
      {
        id: null,
        title: 'Invalid'
      }
    ];

    const { container } = render(WishlistsScreenEventHarness, {
      token: '',
      isExternalUser: true,
      externalProfileId: '42',
      externalUserWishlists
    });

    expect(container.querySelectorAll('.wishlist-card')).toHaveLength(2);
    expect(container.querySelector('.edit-button')).toBeNull();
    expect(container.querySelector('.delete-button')).toBeNull();
    expect(container.querySelector('.ui-button.full')).toBeNull();

    const owners = container.querySelectorAll('.wishlist-owner');
    const arrows = container.querySelectorAll('.arrow-button');

    await fireEvent.click(owners[0]);
    await fireEvent.click(owners[1]);
    await fireEvent.click(arrows[0]);

    const eventNames = Array.from(container.querySelectorAll('[data-testid="events-log"] li')).map(
      (node) => node.textContent
    );

    expect(eventNames).toEqual([
      'openOwnerProfile:{"profileId":"501"}',
      'openOwnerProfile:{"profileId":"42"}',
      'openWishlistDetail:{"wishlistId":"1","isExternal":true}'
    ]);
  });

  test('loads own wishlists and dispatches create/edit/open events', async () => {
    global.fetch.mockImplementation(async (url, options = {}) => {
      const method = options.method || 'GET';

      if (url === '/api/v1/wishlists/' && method === 'GET') {
        return okJson([
          {
            id: 1,
            name: 'My Wishlist',
            description: 'Main',
            photo: '',
            typeprivacy: 'public',
            wishes_count: 2
          },
          {
            id: 2,
            name: 'Second Wishlist',
            description: 'Alt',
            photo: '',
            typeprivacy: 'protected',
            wishes_count: 4
          }
        ]);
      }

      throw new Error(`Unexpected fetch call: ${url} (${method})`);
    });

    const { container } = render(WishlistsScreenEventHarness, {
      token: 'token-123'
    });

    await waitFor(() => {
      expect(container.querySelectorAll('.wishlist-card')).toHaveLength(2);
    });

    await fireEvent.click(container.querySelector('.ui-button.full'));
    await fireEvent.click(container.querySelector('.edit-button'));
    await fireEvent.click(container.querySelector('.wishlist-owner'));
    await fireEvent.click(container.querySelector('.arrow-button'));

    const eventNames = Array.from(container.querySelectorAll('[data-testid="events-log"] li')).map(
      (node) => node.textContent
    );

    expect(eventNames).toEqual([
      'openCreateWishlists',
      'openEditWishlists:{"id":"1","token":"token-123"}',
      'openMainScreen',
      'openWishlistDetail:{"wishlistId":"1","isExternal":false}'
    ]);
  });

  test('opens delete modal, supports cancel, and confirms successful deletion', async () => {
    wishesStore.set([
      {
        id: 'wish-1',
        title: 'Wish A',
        wishlistIds: ['1', '2']
      }
    ]);

    global.fetch.mockImplementation(async (url, options = {}) => {
      const method = options.method || 'GET';

      if (url === '/api/v1/wishlists/' && method === 'GET') {
        return okJson([
          {
            id: 1,
            name: 'Delete Me',
            description: 'Will be removed',
            photo: 'https://selstorage.ru/files/wl-1.png',
            typeprivacy: 'public',
            wishes_count: 3
          }
        ]);
      }

      if (url.startsWith('/api/v1/s3/file/delete?file_url=') && method === 'DELETE') {
        return okJson({ message: 'deleted' });
      }

      if (url === '/api/v1/wishlists/1' && method === 'DELETE') {
        return okJson({ message: 'ok' });
      }

      throw new Error(`Unexpected fetch call: ${url} (${method})`);
    });

    const { container } = renderScreen();

    await waitFor(() => {
      expect(container.querySelector('.delete-button')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.delete-button'));

    await waitFor(() => {
      expect(container.querySelector('.confirm-modal')).toBeTruthy();
    });

    const modalButtons = container.querySelectorAll('.confirm-actions .ui-button');
    await fireEvent.click(modalButtons[0]);

    await waitFor(() => {
      expect(container.querySelector('.confirm-modal')).toBeNull();
    });

    await fireEvent.click(container.querySelector('.delete-button'));

    await waitFor(() => {
      expect(container.querySelector('.confirm-modal')).toBeTruthy();
    });

    await fireEvent.click(container.querySelectorAll('.confirm-actions .ui-button')[1]);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/wishlists/1',
        expect.objectContaining({ method: 'DELETE' })
      );
    });

    const s3DeleteCall = global.fetch.mock.calls.find(
      ([url, opts]) =>
        typeof url === 'string' &&
        url.startsWith('/api/v1/s3/file/delete?file_url=') &&
        opts.method === 'DELETE'
    );

    expect(s3DeleteCall).toBeTruthy();

    const wishesAfterDelete = getStoreValue(wishesStore);
    expect(wishesAfterDelete[0].wishlistIds).toEqual(['2']);
  });

  test('shows alert and resets modal state when wishlist deletion fails', async () => {
    global.fetch.mockImplementation(async (url, options = {}) => {
      const method = options.method || 'GET';

      if (url === '/api/v1/wishlists/' && method === 'GET') {
        return okJson([
          {
            id: 1,
            name: 'Broken Delete',
            description: '',
            photo: '',
            typeprivacy: 'private',
            wishes_count: 0
          }
        ]);
      }

      if (url === '/api/v1/wishlists/1' && method === 'DELETE') {
        return failJson(500, { detail: 'cannot delete' });
      }

      throw new Error(`Unexpected fetch call: ${url} (${method})`);
    });

    const { container } = renderScreen();

    await waitFor(() => {
      expect(container.querySelector('.delete-button')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.delete-button'));
    await fireEvent.click(container.querySelectorAll('.confirm-actions .ui-button')[1]);

    await waitFor(() => {
      expect(global.alert).toHaveBeenCalled();
    });

    expect(container.querySelector('.confirm-modal')).toBeNull();
  });

  test('shows own and external empty states', async () => {
    const own = renderScreen({ token: '' });
    expect(own.container.querySelector('.empty-note')).toBeTruthy();
    expect(own.container.querySelector('.ui-button.full')).toBeTruthy();
    cleanup();

    const external = renderScreen({
      token: '',
      isExternalUser: true,
      externalProfileId: '13',
      externalUserWishlists: []
    });

    expect(external.container.querySelector('.empty-note')).toBeTruthy();
    expect(external.container.querySelector('.ui-button.full')).toBeNull();
  });

  test('keeps empty state when own wishlists loading fails', async () => {
    global.fetch.mockRejectedValue(new Error('network down'));

    const { container } = renderScreen({ token: 'token-123' });

    await waitFor(() => {
      expect(console.error).toHaveBeenCalled();
    });

    expect(container.querySelector('.empty-note')).toBeTruthy();
    expect(container.querySelector('.ui-button.full')).toBeTruthy();
  });

  test('continues wishlist deletion when S3 photo deletion fails', async () => {
    global.fetch.mockImplementation(async (url, options = {}) => {
      const method = options.method || 'GET';

      if (url === '/api/v1/wishlists/' && method === 'GET') {
        return okJson([
          {
            id: 1,
            name: 'Delete With Broken S3',
            description: '',
            photo: 'https://selstorage.ru/files/wl-1.png',
            typeprivacy: 'public',
            wishes_count: 1
          }
        ]);
      }

      if (url.startsWith('/api/v1/s3/file/delete?file_url=') && method === 'DELETE') {
        return failJson(500, { detail: 's3 failed' });
      }

      if (url === '/api/v1/wishlists/1' && method === 'DELETE') {
        return okJson({ message: 'ok' });
      }

      throw new Error(`Unexpected fetch call: ${url} (${method})`);
    });

    const { container } = renderScreen();

    await waitFor(() => {
      expect(container.querySelector('.delete-button')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.delete-button'));
    await fireEvent.click(container.querySelectorAll('.confirm-actions .ui-button')[1]);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/wishlists/1',
        expect.objectContaining({ method: 'DELETE' })
      );
    });

    expect(console.warn).toHaveBeenCalled();
    expect(global.alert).not.toHaveBeenCalled();
  });
});
