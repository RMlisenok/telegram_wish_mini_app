import { jest } from '@jest/globals';
import { get } from 'svelte/store';
import {
  createWish,
  deleteWish,
  loadFinishedWishes,
  loadWishes,
  removeWishFromAllWishlists,
  updateWish,
  updateWishStatus,
  wishesStore
} from '../wishes.ts';

const jsonResponse = (data, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => data,
  text: async () => JSON.stringify(data)
});

const activeWishDto = {
  id: 1,
  name: 'Kindle',
  photo: 'kindle.png',
  url_gift: 'https://example.com/kindle',
  price: 100,
  currency: 'RUB',
  is_booked: false,
  status_is_finished: false,
  description: 'E-reader',
  created_at: '2026-01-01T00:00:00.000Z',
  updated_at: '2026-01-02T00:00:00.000Z'
};

const baseWishPayload = {
  name: 'Kindle',
  photo: 'kindle.png',
  url_gift: 'https://example.com/kindle',
  price: 100,
  currency: 'RUB',
  description: 'E-reader',
  is_booked: false,
  status_is_finished: false
};

describe('types/wishes', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    wishesStore.set([]);
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('loadWishes fetches active wishes, normalizes ids and resets store on failure', async () => {
    global.fetch.mockResolvedValueOnce(jsonResponse([activeWishDto, { ...activeWishDto, id: 2, currency: null }]));

    const result = await loadWishes('token-123');

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/wishes/finish?is_finish=false',
      expect.objectContaining({ method: 'GET' })
    );
    expect(result).toHaveLength(2);
    expect(get(wishesStore)).toEqual([
      expect.objectContaining({ id: '1', currency: 'RUB', is_booked: false }),
      expect.objectContaining({ id: '2', currency: null })
    ]);

    wishesStore.set([{ id: 'old', name: 'Old wish' }]);
    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(loadWishes('token-123')).rejects.toThrow('Ошибка загрузки желаний');
    expect(get(wishesStore)).toEqual([]);
  });

  test('loadFinishedWishes maps finished wishes with description and dates', async () => {
    global.fetch.mockResolvedValueOnce(
      jsonResponse([
        activeWishDto,
        {
          ...activeWishDto,
          id: 2,
          currency: null,
          description: null,
          status_is_finished: true,
          updated_at: '2026-02-02T00:00:00.000Z'
        }
      ])
    );

    await loadFinishedWishes('token-123');

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/wishes/finish?is_finish=true',
      expect.objectContaining({ method: 'GET' })
    );
    expect(get(wishesStore)[0]).toEqual(
      expect.objectContaining({
        id: '1',
        description: 'E-reader',
        created_At: expect.any(Date),
        updated_At: expect.any(Date)
      })
    );
    expect(get(wishesStore)[1]).toEqual(expect.objectContaining({ id: '2', description: '', currency: null }));

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(loadFinishedWishes('token-123')).rejects.toThrow('Ошибка загрузки желаний');
    expect(get(wishesStore)).toEqual([]);
  });

  test('createWish posts payload, covers optional currency branch and propagates errors', async () => {
    global.fetch.mockResolvedValueOnce(jsonResponse({ ...activeWishDto, id: 10 }));

    const result = await createWish('token-123', baseWishPayload);

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/wishes/',
      expect.objectContaining({ method: 'POST' })
    );
    expect(JSON.parse(global.fetch.mock.calls[0][1].body)).toEqual(baseWishPayload);
    expect(result.id).toBe(10);

    global.fetch.mockResolvedValueOnce(jsonResponse({ ...activeWishDto, id: 11, currency: null }));
    await expect(createWish('token-123', { ...baseWishPayload, currency: null })).resolves.toEqual(
      expect.objectContaining({ id: 11 })
    );

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(createWish('token-123', baseWishPayload)).rejects.toThrow('Ошибка создания желания');
  });

  test('updateWish sends PUT request and throws on backend failure', async () => {
    global.fetch.mockResolvedValueOnce(jsonResponse({ ...activeWishDto, name: 'Updated' }));

    await expect(updateWish('token-123', '1', { ...baseWishPayload, name: 'Updated' })).resolves.toEqual(
      expect.objectContaining({ name: 'Updated' })
    );

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/wishes/1',
      expect.objectContaining({ method: 'PUT' })
    );

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(updateWish('token-123', '1', baseWishPayload)).rejects.toThrow('Ошибка обновления желания');
  });

  test('deleteWish returns true on success and throws specific delete errors', async () => {
    global.fetch.mockResolvedValueOnce(jsonResponse({}, true, 204));

    await expect(deleteWish('token-123', '1')).resolves.toBe(true);
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/wishes/1',
      expect.objectContaining({ method: 'DELETE' })
    );

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 404));
    await expect(deleteWish('token-123', '1')).rejects.toThrow('Желание не найдено');

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(deleteWish('token-123', '1')).rejects.toThrow('Ошибка удаления желания');
  });

  test('updateWishStatus loads current wish, sends normalized status body and returns updated wish', async () => {
    global.fetch
      .mockResolvedValueOnce(jsonResponse({ ...activeWishDto, name: '', description: null, photo: null, url_gift: null }))
      .mockResolvedValueOnce(jsonResponse({ ...activeWishDto, status_is_finished: true, is_booked: false }));

    const result = await updateWishStatus('token-123', '1', { status_is_finished: true });

    expect(result.status_is_finished).toBe(true);
    expect(global.fetch).toHaveBeenNthCalledWith(
      1,
      '/api/v1/wishes/1',
      expect.objectContaining({ method: 'GET' })
    );
    expect(global.fetch).toHaveBeenNthCalledWith(
      2,
      '/api/v1/wishes/1',
      expect.objectContaining({ method: 'PUT' })
    );
    expect(JSON.parse(global.fetch.mock.calls[1][1].body)).toEqual({
      name: '',
      description: '',
      photo: '',
      url_gift: '',
      price: 100,
      currency: 'RUB',
      status_is_finished: true,
      is_booked: false
    });
  });

  test('updateWishStatus respects explicit is_booked and reports GET/PUT errors', async () => {
    global.fetch
      .mockResolvedValueOnce(jsonResponse(activeWishDto))
      .mockResolvedValueOnce(jsonResponse({ ...activeWishDto, is_booked: true }));

    await updateWishStatus('token-123', '1', { status_is_finished: true, is_booked: true });

    expect(JSON.parse(global.fetch.mock.calls[1][1].body)).toEqual(
      expect.objectContaining({ status_is_finished: true, is_booked: true })
    );

    global.fetch.mockResolvedValueOnce(jsonResponse({ detail: 'not found' }, false, 404));
    await expect(updateWishStatus('token-123', '1', { status_is_finished: true })).rejects.toThrow(
      'Не удалось получить данные желания'
    );

    global.fetch
      .mockResolvedValueOnce(jsonResponse(activeWishDto))
      .mockResolvedValueOnce(jsonResponse({ detail: 'server' }, false, 500));
    await expect(updateWishStatus('token-123', '1', { status_is_finished: true })).rejects.toThrow(
      'Ошибка обновления статуса желания'
    );
  });

  test('removeWishFromAllWishlists returns true and handles delete errors', async () => {
    global.fetch.mockResolvedValueOnce(jsonResponse({}, true, 204));

    await expect(removeWishFromAllWishlists('token-123', '1')).resolves.toBe(true);
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/wishes/wishlists/1',
      expect.objectContaining({ method: 'DELETE' })
    );

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 404));
    await expect(removeWishFromAllWishlists('token-123', '1')).rejects.toThrow('Желание не найдено');

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(removeWishFromAllWishlists('token-123', '1')).rejects.toThrow(
      'Ошибка удаления желания из вишлистов'
    );
  });
});
