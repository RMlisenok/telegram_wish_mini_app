import { jest } from '@jest/globals';
import {
  checkWishReservation,
  createReservation,
  getUserReservations,
  toggleReservation
} from '../wish_reservation.ts';

const jsonResponse = (data, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => data,
  text: async () => JSON.stringify(data)
});

describe('types/wish_reservation', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('getUserReservations maps backend reservation data', async () => {
    global.fetch.mockResolvedValue(
      jsonResponse([
        {
          wish_wishlist_id: 12,
          reserved_by_id: 44,
          created_at: '2026-01-01T00:00:00.000Z'
        }
      ])
    );

    const result = await getUserReservations('token-123', 10);

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/reservations/?limit=10',
      expect.objectContaining({ method: 'GET' })
    );
    expect(result[0]).toEqual(
      expect.objectContaining({ wish_wishlist_id: '12', reserved_by_id: '44' })
    );
    expect(result[0].created_at).toBeInstanceOf(Date);
  });

  test('createReservation posts numeric wish_wishlist_id', async () => {
    global.fetch.mockResolvedValue(
      jsonResponse({
        wish_wishlist_id: 12,
        reserved_by_id: 44,
        created_at: '2026-01-01T00:00:00.000Z'
      })
    );

    const result = await createReservation('token-123', '12');

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/reservations/',
      expect.objectContaining({ method: 'POST' })
    );
    expect(JSON.parse(global.fetch.mock.calls[0][1].body)).toEqual({ wish_wishlist_id: 12 });
    expect(result.reserved_by_id).toBe('44');
  });

  test('checkWishReservation detects reservation made by current user', async () => {
    global.fetch
      .mockResolvedValueOnce(
        jsonResponse([
          { wish_wishlist_id: 12, reserved_by_id: 44, created_at: '2026-01-01T00:00:00.000Z' }
        ])
      )
      .mockResolvedValueOnce(jsonResponse({ id: 44 }));

    const result = await checkWishReservation('token-123', '12');

    expect(result).toEqual({ isReserved: true, reservedByCurrentUser: true });
  });

  test('toggleReservation follows current implementation branch logic', async () => {
    global.fetch.mockResolvedValue(
      jsonResponse({
        wish_wishlist_id: 12,
        reserved_by_id: 44,
        created_at: '2026-01-01T00:00:00.000Z'
      })
    );

    const result = await toggleReservation('token-123', '12', true);

    expect(result).toBe(true);
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/reservations/',
      expect.objectContaining({ method: 'POST' })
    );
  });
});
