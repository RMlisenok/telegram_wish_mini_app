import { jest } from '@jest/globals';
import { createWishlist, deleteWishlist, loadWishlists, wishlistsStore } from '../wishlists.ts';

const jsonResponse = (data, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => data,
  text: async () => JSON.stringify(data)
});

describe('types/wishlists', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    wishlistsStore.set([]);
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('loadWishlists maps backend fields and privacy values', async () => {
    global.fetch.mockResolvedValue(
      jsonResponse([
        {
          id: 1,
          name: 'Public list',
          description: 'open',
          photo: '',
          typeprivacy: 'public',
          wishes_count: 2
        },
        {
          id: 2,
          name: 'Protected list',
          description: 'limited',
          photo: '',
          typeprivacy: 'protected',
          wishes_count: 5
        }
      ])
    );

    const result = await loadWishlists('token-123');

    expect(result).toEqual([
      expect.objectContaining({ id: '1', title: 'Public list', privacy: 'public', count: 2 }),
      expect.objectContaining({ id: '2', title: 'Protected list', privacy: 'restricted', count: 5 })
    ]);
  });

  test('loadWishlists resets store and throws on failure', async () => {
    global.fetch.mockResolvedValue(jsonResponse({}, false, 500));

    await expect(loadWishlists('token-123')).rejects.toThrow('Ошибка загрузки вишлистов');
  });

  test('createWishlist posts payload and returns response data', async () => {
    global.fetch.mockResolvedValue(
      jsonResponse({ id: '10', name: 'Travel', description: '', photo: '', typeprivacy: 'public' })
    );

    const result = await createWishlist('token-123', {
      name: 'Travel',
      description: '',
      photo: '',
      typeprivacy: 'public'
    });

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/wishlists/',
      expect.objectContaining({ method: 'POST' })
    );
    expect(result.id).toBe('10');
  });

  test('deleteWishlist removes deleted wishlist from store', async () => {
    wishlistsStore.set([
      { id: '1', name: 'One', description: '', photo: '', typeprivacy: 'public', count: 1 },
      { id: '2', name: 'Two', description: '', photo: '', typeprivacy: 'public', count: 1 }
    ]);
    global.fetch.mockResolvedValue(jsonResponse({}, true, 204));

    await deleteWishlist('token-123', '1');

    let currentValue;
    wishlistsStore.subscribe((value) => {
      currentValue = value;
    })();

    expect(currentValue).toHaveLength(1);
    expect(currentValue[0].id).toBe('2');
  });
});
