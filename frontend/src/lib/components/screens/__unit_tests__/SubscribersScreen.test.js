import { jest } from '@jest/globals';
import { cleanup, fireEvent, render, waitFor } from '@testing-library/svelte';

import SubscribersScreen from '../SubscribersScreen.svelte';
import SubscribersScreenEventHarness from './SubscribersScreenEventHarness.svelte';
import { subscribersStore } from '../../../../types/subscribers.ts';

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

function renderScreen(props = {}) {
  return render(SubscribersScreen, {
    token: 'token-123',
    ...props
  });
}

describe('SubscribersScreen', () => {
  beforeEach(() => {
    subscribersStore.set([]);
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

  test('keeps empty state when token is missing', async () => {
    const { container } = renderScreen({ token: '' });

    await waitFor(() => {
      expect(container.querySelector('.empty-note')).toBeTruthy();
    });

    expect(global.fetch).not.toHaveBeenCalled();
  });

  test('loads subscribers and supports search filtering', async () => {
    global.fetch.mockResolvedValue(
      okJson({
        subscribers: [
          {
            sub_id: 1,
            user_id: 10,
            name: 'Alice Cooper',
            birth_date: '1999-02-01',
            photo: ''
          },
          {
            sub_id: 2,
            user_id: 20,
            name: 'Bob Marley',
            birth_date: '03.04.2001',
            photo: ''
          }
        ]
      })
    );

    const { container } = renderScreen();

    await waitFor(() => {
      expect(container.querySelectorAll('.subscriber-card')).toHaveLength(2);
    });

    expect(container.textContent).toContain('01.02.1999');

    const searchInput = container.querySelector('input[type="text"]');

    await fireEvent.input(searchInput, { target: { value: 'bob' } });
    await waitFor(() => {
      expect(container.querySelectorAll('.subscriber-card')).toHaveLength(1);
      expect(container.textContent).toContain('Bob Marley');
    });

    await fireEvent.input(searchInput, { target: { value: 'unknown' } });
    await waitFor(() => {
      expect(container.querySelector('.empty-note')).toBeTruthy();
    });
  });

  test('dispatches open-profile event from card click and arrow click', async () => {
    global.fetch.mockResolvedValue(
      okJson({
        subscribers: [
          {
            sub_id: 1,
            user_id: 55,
            name: 'Event Subscriber',
            birth_date: '1990-01-01',
            photo: ''
          }
        ]
      })
    );

    const { container } = render(SubscribersScreenEventHarness, {
      token: 'token-123'
    });

    await waitFor(() => {
      expect(container.querySelector('.subscriber-card')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.subscriber-card'));
    await fireEvent.click(container.querySelector('.arrow-button'));
    await fireEvent.keyDown(container.querySelector('.subscriber-card'), { key: 'Enter' });

    const eventNames = Array.from(container.querySelectorAll('[data-testid="events-log"] li')).map(
      (node) => node.textContent
    );

    expect(eventNames).toEqual([
      'open-profile:{"profileId":55}',
      'open-profile:{"profileId":55}',
      'open-profile:{"profileId":55}'
    ]);
  });

  test('shows placeholder subscription alert and handles action error branch', async () => {
    global.fetch.mockResolvedValue(
      okJson({
        subscribers: [
          {
            sub_id: 1,
            user_id: 101,
            name: 'Toggle Subscriber',
            birth_date: '1990-01-01',
            photo: ''
          }
        ]
      })
    );

    const { container } = renderScreen();

    await waitFor(() => {
      expect(container.querySelector('.subscribe-btn')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.subscribe-btn'));
    expect(global.alert).toHaveBeenCalled();

    global.alert.mockImplementationOnce(() => {
      throw new Error('alert failed');
    });

    await fireEvent.click(container.querySelector('.subscribe-btn'));

    await waitFor(() => {
      expect(global.alert.mock.calls.length).toBeGreaterThanOrEqual(3);
    });

    expect(console.error).toHaveBeenCalled();
  });

  test('logs error when subscribers loading request fails', async () => {
    global.fetch.mockResolvedValue(failJson(500));

    renderScreen();

    await waitFor(() => {
      expect(console.error).toHaveBeenCalled();
    });
  });

  test('shows auth alert on subscribe action when token is missing but list exists', async () => {
    subscribersStore.set([
      {
        sub_id: 9,
        user_id: 909,
        name: 'No Token Subscriber',
        birth_date: '1990-01-01',
        photo: ''
      }
    ]);

    const { container } = renderScreen({ token: '' });

    await waitFor(() => {
      expect(container.querySelector('.subscriber-card')).toBeTruthy();
    });

    await fireEvent.click(container.querySelector('.subscribe-btn'));

    expect(global.alert).toHaveBeenCalled();
    expect(global.fetch).not.toHaveBeenCalled();
  });

  test('opens profile only on Enter key and ignores other keys', async () => {
    global.fetch.mockResolvedValue(
      okJson({
        subscribers: [
          {
            sub_id: 1,
            user_id: 88,
            name: 'Keyboard Subscriber',
            birth_date: '1990-01-01',
            photo: ''
          }
        ]
      })
    );

    const { container } = render(SubscribersScreenEventHarness, {
      token: 'token-123'
    });

    await waitFor(() => {
      expect(container.querySelector('.subscriber-card')).toBeTruthy();
    });

    const card = container.querySelector('.subscriber-card');
    await fireEvent.keyDown(card, { key: 'Space' });
    await fireEvent.keyDown(card, { key: 'Enter' });

    const eventNames = Array.from(container.querySelectorAll('[data-testid="events-log"] li')).map(
      (node) => node.textContent
    );

    expect(eventNames).toEqual(['open-profile:{"profileId":88}']);
  });

  test('renders explicit empty state for authorized user with no subscribers', async () => {
    global.fetch.mockResolvedValue(okJson({ subscribers: [] }));

    const { container } = renderScreen({ token: 'token-123' });

    await waitFor(() => {
      expect(container.querySelector('.empty-note')).toBeTruthy();
    });
  });
});
