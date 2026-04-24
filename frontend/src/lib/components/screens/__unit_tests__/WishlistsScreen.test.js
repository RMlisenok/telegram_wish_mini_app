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
});
