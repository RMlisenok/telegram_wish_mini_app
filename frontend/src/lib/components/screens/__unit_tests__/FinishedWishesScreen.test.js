import { jest } from '@jest/globals';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/svelte';

import FinishedWishesScreen from '../FinishedWishesScreen.svelte';
import FinishedWishesScreenEventHarness from './FinishedWishesScreenEventHarness.svelte';
import { wishesStore } from '../../../../types/wishes.ts';

const jsonResponse = (data, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => data,
  text: async () => JSON.stringify(data)
});

const finishedWish = {
  id: 1,
  name: 'Kindle',
  photo: '',
  url_gift: 'https://example.com/kindle',
  price: 100,
  currency: 'RUB',
  is_booked: true,
  status_is_finished: true,
  description: 'E-reader',
  created_at: '2026-01-01T00:00:00.000Z',
  updated_at: '2026-02-01T00:00:00.000Z'
};

describe('FinishedWishesScreen', () => {
  beforeEach(() => {
    wishesStore.set([]);
    global.fetch = jest.fn();
    global.confirm = jest.fn(() => true);
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
  });

  test('loads finished wishes on mount and shows empty state', async () => {
    global.fetch.mockResolvedValue(jsonResponse([]));

    render(FinishedWishesScreen, { token: 'token-123' });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/wishes/finish?is_finish=true',
        expect.objectContaining({ method: 'GET' })
      );
      expect(screen.getByText('У вас пока нет исполненных желаний.')).toBeInTheDocument();
    });
  });

  test('renders wishes sorted by updated date descending', async () => {
    global.fetch.mockResolvedValue(
      jsonResponse([
        {
          ...finishedWish,
          id: 2,
          name: 'Older wish',
          updated_at: '2025-01-01T00:00:00.000Z'
        },
        {
          ...finishedWish,
          id: 3,
          name: 'Newest wish',
          updated_at: '2026-03-01T00:00:00.000Z'
        }
      ])
    );

    const { container } = render(FinishedWishesScreen, { token: 'token-123' });

    await waitFor(() => {
      const names = Array.from(container.querySelectorAll('.wish-title')).map((node) =>
        node.textContent?.trim()
      );
      expect(names).toEqual(['Newest wish', 'Older wish']);
    });
  });

  test('renders placeholder image and formatted price symbol', async () => {
    global.fetch.mockResolvedValue(jsonResponse([finishedWish]));

    const { container } = render(FinishedWishesScreen, { token: 'token-123' });

    await waitFor(() => {
      expect(screen.getByText('100 ₽')).toBeInTheDocument();
      expect(screen.getByText('Исполнено')).toBeInTheDocument();
      expect(container.querySelector('.wish-image.placeholder')).toBeTruthy();
    });
  });

  test('returns wish to active list and reloads finished wishes', async () => {
    global.fetch.mockImplementation(async (url, options = {}) => {
      if (url === '/api/v1/wishes/finish?is_finish=true' && (!options.method || options.method === 'GET')) {
        return jsonResponse([finishedWish]);
      }

      if (url === '/api/v1/wishes/1' && options.method === 'GET') {
        return jsonResponse(finishedWish);
      }

      if (url === '/api/v1/wishes/1' && options.method === 'PUT') {
        return jsonResponse({ ...finishedWish, status_is_finished: false, is_booked: false });
      }

      throw new Error(`Unexpected fetch call: ${url} (${options.method || 'GET'})`);
    });

    render(FinishedWishesScreen, { token: 'token-123' });

    await screen.findByText('Вернуть в активные');
    await fireEvent.click(screen.getByText('Вернуть в активные'));

    await waitFor(() => {
      const putCall = global.fetch.mock.calls.find(
        ([url, opts]) => url === '/api/v1/wishes/1' && opts.method === 'PUT'
      );
      expect(putCall).toBeTruthy();
      expect(JSON.parse(putCall[1].body)).toMatchObject({
        status_is_finished: false,
        is_booked: false,
        name: 'Kindle'
      });
    });
  });

  test('does not delete wish when deletion is cancelled', async () => {
    global.confirm = jest.fn(() => false);
    global.fetch.mockResolvedValue(jsonResponse([finishedWish]));

    render(FinishedWishesScreen, { token: 'token-123' });

    await screen.findByText('Удалить');
    await fireEvent.click(screen.getByText('Удалить'));

    expect(global.confirm).toHaveBeenCalled();
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  test('deletes wish permanently after confirmation and reloads list', async () => {
    let finishedCalls = 0;

    global.fetch.mockImplementation(async (url, options = {}) => {
      if (url === '/api/v1/wishes/finish?is_finish=true' && (!options.method || options.method === 'GET')) {
        finishedCalls += 1;
        return jsonResponse(finishedCalls === 1 ? [finishedWish] : []);
      }

      if (url === '/api/v1/wishes/1' && options.method === 'DELETE') {
        return jsonResponse({}, true, 204);
      }

      throw new Error(`Unexpected fetch call: ${url} (${options.method || 'GET'})`);
    });

    render(FinishedWishesScreen, { token: 'token-123' });

    await screen.findByText('Удалить');
    await fireEvent.click(screen.getByText('Удалить'));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/wishes/1',
        expect.objectContaining({ method: 'DELETE' })
      );
      expect(screen.getByText('У вас пока нет исполненных желаний.')).toBeInTheDocument();
    });
  });

  test('dispatches back event', async () => {
    global.fetch.mockResolvedValue(jsonResponse([]));

    render(FinishedWishesScreenEventHarness, { token: 'token-123' });

    await screen.findByText('Назад');
    await fireEvent.click(screen.getByText('Назад'));

    const events = Array.from(screen.getByTestId('events-log').querySelectorAll('li')).map(
      (node) => node.textContent
    );

    expect(events).toEqual(['back']);
  });
});
