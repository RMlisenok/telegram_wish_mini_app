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
});
