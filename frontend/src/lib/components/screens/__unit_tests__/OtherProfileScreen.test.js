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

  test('does not dispatch subscriptions event when subscriptions are private', async () => {
    const profile = {
      ...baseProfile,
      subscriptionsArePrivate: true,
      subscriptions: [{ id: 1, fullName: 'Private User', birthDate: null, avatarUrl: '' }]
    };

    const { container } = render(OtherProfileScreenEventHarness, {
      token: 'token-123',
      profile
    });

    await fireEvent.click(container.querySelectorAll('.link-btn')[1]);

    const eventNames = Array.from(container.querySelectorAll('[data-testid="events-log"] li')).map(
      (node) => node.textContent
    );

    expect(eventNames).toEqual([]);
    expect(container.querySelectorAll('.empty-note').length).toBeGreaterThan(0);
  });

  test('subscribes to profile and dispatches toggle-subscribe=true', async () => {
    global.fetch.mockResolvedValue(okJson({ message: 'ok' }));

    const { container } = render(OtherProfileScreenEventHarness, {
      token: 'token-123',
      profile: {
        ...baseProfile,
        isSubscribed: false
      }
    });

    await fireEvent.click(container.querySelectorAll('.profile-actions .ui-button')[0]);

    await waitFor(() => {
      const eventNames = Array.from(
        container.querySelectorAll('[data-testid="events-log"] li')
      ).map((node) => node.textContent);

      expect(eventNames).toContain('toggle-subscribe:{"profileId":55,"value":true}');
    });

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/subscriptions/users',
      expect.objectContaining({ method: 'POST' })
    );
  });

  test('unsubscribes from profile and dispatches toggle-subscribe=false', async () => {
    global.fetch.mockResolvedValue(okJson({ message: 'ok' }));

    const { container } = render(OtherProfileScreenEventHarness, {
      token: 'token-123',
      profile: {
        ...baseProfile,
        isSubscribed: true
      }
    });

    await fireEvent.click(container.querySelectorAll('.profile-actions .ui-button')[0]);

    await waitFor(() => {
      const eventNames = Array.from(
        container.querySelectorAll('[data-testid="events-log"] li')
      ).map((node) => node.textContent);

      expect(eventNames).toContain('toggle-subscribe:{"profileId":55,"value":false}');
    });

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/subscriptions/users/55',
      expect.objectContaining({ method: 'DELETE' })
    );
  });

  test('shows alert when subscribe request fails', async () => {
    global.fetch.mockResolvedValue(failJson(400, { detail: 'Subscribe failed' }));

    const { container } = render(OtherProfileScreenEventHarness, {
      token: 'token-123',
      profile: {
        ...baseProfile,
        isSubscribed: false
      }
    });

    await fireEvent.click(container.querySelectorAll('.profile-actions .ui-button')[0]);

    await waitFor(() => {
      expect(global.alert).toHaveBeenCalledWith('Subscribe failed');
    });

    expect(container.querySelectorAll('[data-testid="events-log"] li')).toHaveLength(0);
  });

  test('does not call API when token or profile id is missing', async () => {
    const { container } = renderScreen({
      token: '',
      profile: {
        ...baseProfile,
        id: null,
        questionnaire: null,
        publicWishlists: [],
        subscriptions: []
      }
    });

    const subscribeButton = container.querySelectorAll('.profile-actions .ui-button')[0];

    expect(subscribeButton).toBeDisabled();

    await fireEvent.click(subscribeButton);

    expect(global.fetch).not.toHaveBeenCalled();
    expect(container.querySelector('.empty-note')).toBeTruthy();
  });

  test('shows loading state while subscribe request is pending', async () => {
    let resolveRequest;
    global.fetch.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveRequest = () => resolve(okJson({ message: 'ok' }));
        })
    );

    const { container } = render(OtherProfileScreenEventHarness, {
      token: 'token-123',
      profile: {
        ...baseProfile,
        isSubscribed: false
      }
    });

    await fireEvent.click(container.querySelectorAll('.profile-actions .ui-button')[0]);

    await waitFor(() => {
      expect(container.querySelectorAll('.profile-actions .ui-button')[0]).toBeDisabled();
    });

    resolveRequest();

    await waitFor(() => {
      const eventNames = Array.from(
        container.querySelectorAll('[data-testid="events-log"] li')
      ).map((node) => node.textContent);
      expect(eventNames).toContain('toggle-subscribe:{"profileId":55,"value":true}');
    });
  });

  test('shows fallback alert text when subscribe response has no json body', async () => {
    global.fetch.mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => {
        throw new Error('broken json');
      }
    });

    const { container } = render(OtherProfileScreenEventHarness, {
      token: 'token-123',
      profile: {
        ...baseProfile,
        isSubscribed: false
      }
    });

    await fireEvent.click(container.querySelectorAll('.profile-actions .ui-button')[0]);

    await waitFor(() => {
      expect(global.alert).toHaveBeenCalled();
    });
  });

  test('renders restricted wishlist visibility and questionnaire fallback', async () => {
    const { container } = renderScreen({
      profile: {
        ...baseProfile,
        publicWishlists: [
          {
            id: 'wl-2',
            title: 'Restricted Wishlist',
            visibility: 'restricted',
            wishesCount: undefined,
            iconUrl: '../../../../static/icons/gift-check.png'
          }
        ],
        subscriptions: [{ id: 101, fullName: 'Sub No Title', birthDate: '02.02.2000' }],
        questionnaire: {
          interests: [],
          noGifts: []
        }
      }
    });

    expect(container.querySelector('.wishlist-row')).toBeTruthy();
    expect(container.querySelector('.sub-row')).toBeTruthy();
    expect(container.querySelector('.empty-note')).toBeTruthy();
  });

  test('skips subscribe request when token is missing but profile id exists', async () => {
    const { container } = render(OtherProfileScreenEventHarness, {
      token: '',
      profile: {
        ...baseProfile,
        id: 55,
        isSubscribed: false
      }
    });

    await fireEvent.click(container.querySelectorAll('.profile-actions .ui-button')[0]);

    expect(global.fetch).not.toHaveBeenCalled();
    expect(console.error).toHaveBeenCalled();
  });
});
