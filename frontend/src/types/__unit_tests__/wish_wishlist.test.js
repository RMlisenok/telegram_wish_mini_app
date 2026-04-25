import { jest } from '@jest/globals';
import {
  addMultipleWishesToWishlist,
  addWishToWishlist,
  getWishesFromWishlist,
  toggleWishPinInWishlist
} from '../wish_wishlist.ts';

const jsonResponse = (data, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => data,
  text: async () => JSON.stringify(data)
});

describe('types/wish_wishlist', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('getWishesFromWishlist maps wish and connection data', async () => {
    global.fetch.mockResolvedValue(
      jsonResponse([
        {
          id: 1,
          name: 'Camera',
          photo: '',
          url_gift: 'https://example.com/camera',
          price: 500,
          currency: 'USD',
          description: 'Mirrorless',
          is_booked: false,
          status_is_finished: false,
          created_at: '2026-01-01T00:00:00.000Z',
          updated_at: '2026-01-02T00:00:00.000Z',
          connection_id: 8,
          is_pinned: true,
          order_position: 1,
          added_at: '2026-01-03T00:00:00.000Z'
        }
      ])
    );

    const result = await getWishesFromWishlist('token-123', '77', 10);

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/wishlists/77/wishes?limit=10',
      expect.objectContaining({ method: 'GET' })
    );
    expect(result[0]).toEqual(
      expect.objectContaining({
        id: '1',
        connection_id: '8',
        is_pinned: true,
        order_position: 1
      })
    );
    expect(result[0].updated_at).toBeInstanceOf(Date);
  });

  test('addWishToWishlist posts numeric ids and default options', async () => {
    global.fetch.mockResolvedValue(
      jsonResponse({
        id: 5,
        wish_id: 10,
        wishlist_id: 77,
        is_pinned: false,
        order_position: 0,
        created_at: '2026-01-01T00:00:00.000Z',
        updated_at: '2026-01-01T00:00:00.000Z'
      })
    );

    const result = await addWishToWishlist('token-123', '77', '10');

    const call = global.fetch.mock.calls[0];
    expect(call[0]).toBe('/api/v1/wishlists/77/wishes');
    expect(JSON.parse(call[1].body)).toEqual({
      wish_id: 10,
      wishlist_id: 77,
      is_pinned: false,
      order_position: 0
    });
    expect(result.id).toBe('5');
  });

  test('toggleWishPinInWishlist updates connection pin status', async () => {
    global.fetch.mockResolvedValue(
      jsonResponse({
        id: 9,
        wish_id: 10,
        wishlist_id: 77,
        is_pinned: true,
        order_position: 3,
        created_at: '2026-01-01T00:00:00.000Z',
        updated_at: '2026-01-02T00:00:00.000Z'
      })
    );

    const result = await toggleWishPinInWishlist('token-123', '9', true, 3);

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/wishlists/connections/9',
      expect.objectContaining({ method: 'PUT' })
    );
    expect(JSON.parse(global.fetch.mock.calls[0][1].body)).toEqual({
      is_pinned: true,
      order_position: 3
    });
    expect(result.is_pinned).toBe(true);
  });

  test('addMultipleWishesToWishlist returns only successful additions', async () => {
    global.fetch.mockImplementation(async (url, options = {}) => {
      const payload = JSON.parse(options.body);
      if (payload.wish_id === 2) {
        return {
          ok: false,
          status: 400,
          text: async () => 'duplicate'
        };
      }

      return jsonResponse({
        id: payload.wish_id,
        wish_id: payload.wish_id,
        wishlist_id: payload.wishlist_id,
        is_pinned: false,
        order_position: 0,
        created_at: '2026-01-01T00:00:00.000Z',
        updated_at: '2026-01-01T00:00:00.000Z'
      });
    });

    const result = await addMultipleWishesToWishlist('token-123', '77', ['1', '2', '3']);

    expect(result.map((item) => item.wish_id)).toEqual(['1', '3']);
  });
});
