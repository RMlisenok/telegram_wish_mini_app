import { jest } from '@jest/globals';
import { getMySubscribers, subscribersStore } from '../subscribers.ts';

const jsonResponse = (data, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => data
});

describe('types/subscribers', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    subscribersStore.set([]);
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('getMySubscribers fetches and stores subscribers list', async () => {
    global.fetch.mockResolvedValue(
      jsonResponse({
        subscribers: [{ type: 'user', sub_id: 1, name: 'Alice', user_id: 10 }],
        total: 1
      })
    );

    const result = await getMySubscribers('token-123', false, 5);

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/subscriptions/my/subscribers?is_desc=false&limit=5',
      expect.objectContaining({ method: 'GET' })
    );
    expect(result.total).toBe(1);
  });

  test('getMySubscribers resets store and throws on failure', async () => {
    global.fetch.mockResolvedValue(jsonResponse({}, false, 500));

    await expect(getMySubscribers('token-123')).rejects.toThrow('Ошибка загрузки подписчиков');
  });
});
