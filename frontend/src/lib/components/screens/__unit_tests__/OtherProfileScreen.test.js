import { jest } from '@jest/globals';
import { cleanup, fireEvent, render, waitFor } from '@testing-library/svelte';

import OtherProfileScreen from '../OtherProfileScreen.svelte';
import OtherProfileScreenEventHarness from './OtherProfileScreenEventHarness.svelte';

const okJson = (data) => ({
  ok: true,
  status: 200,
  json: async () => data,
  text: async () => JSON.stringify(data)
});

const failJson = (status = 400, data = { detail: 'error' }) => ({
  ok: false,
  status,
  json: async () => data,
  text: async () => JSON.stringify(data)
});

const baseProfile = {
  id: 55,
  fullName: 'John Profile',
  birthDate: '10.10.1990',
  avatarUrl: '',
  isSubscribed: false,
  publicWishlists: [
    {
      id: 'wl-1',
      title: 'Main Wishlist',
      visibility: 'public',
      wishesCount: 3,
      iconUrl: ''
    }
  ],
  subscriptions: [
    {
      id: 77,
      fullName: 'Sub User',
      birthDate: '01.01.1995',
      wishlistTitle: 'Birthday',
      avatarUrl: ''
    }
  ],
  subscriptionsArePrivate: false,
  questionnaire: {
    interests: [{ tag: 'Books', details: 'Fantasy' }],
    noGifts: [{ tag: 'Socks', details: 'Any type' }]
  }
};

function renderScreen(props = {}) {
  return render(OtherProfileScreen, {
    token: 'token-123',
    profile: baseProfile,
    ...props
  });
}

describe('OtherProfileScreen', () => {
  beforeEach(() => {
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

  test('renders profile and dispatches navigation events', async () => {
    const { container } = render(OtherProfileScreenEventHarness, {
      token: 'token-123',
      profile: baseProfile
    });

    const linkButtons = container.querySelectorAll('.link-btn');
    expect(linkButtons).toHaveLength(2);

    await fireEvent.click(linkButtons[0]);
    await fireEvent.click(linkButtons[1]);

    await fireEvent.click(container.querySelector('.wishlist-row'));
    await fireEvent.click(container.querySelector('.sub-row'));

    const actionButtons = container.querySelectorAll('.profile-actions .ui-button');
    await fireEvent.click(actionButtons[1]);
    await fireEvent.click(container.querySelector('.footer-actions .ui-button'));

    const eventNames = Array.from(container.querySelectorAll('[data-testid="events-log"] li')).map(
      (node) => node.textContent
    );

    expect(eventNames).toEqual([
      'show-all-wishlists:{"profileId":55,"isExternalProfile":true}',
      'show-all-subscriptions:{"profileId":55}',
      'open-wishlist:{"wishlistId":"wl-1","profileId":55}',
      'open-profile:{"profileId":77}',
      'share-profile:{"profileId":55}',
      'back'
    ]);

    expect(container.textContent).toContain('Books');
    expect(container.textContent).toContain('Socks');
  });
});
