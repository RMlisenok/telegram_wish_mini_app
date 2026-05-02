import { jest } from '@jest/globals';
import { get } from 'svelte/store';
import {
  checkWishReservation,
  createReservation,
  getUserReservations,
  toggleReservation,
  canCancelReservation,
  checkReservationStatus,
  deleteReservation,
  getReservationByWishWishlistId,
  getReservationUserInfo,
  getReservationsByWishId,
  getReservationsForWishWishlist,
  hasActiveReservations,
  reservationsStore,
} from '../wish_reservation.ts';

const jsonResponse = (data, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => data,
  text: async () => JSON.stringify(data)
});

const reservationDto = {
  wish_wishlist_id: 12,
  reserved_by_id: 44,
  created_at: '2026-01-01T00:00:00.000Z'
};

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

  test('canCancelReservation returns reservation ownership and false on errors', async () => {
    global.fetch
        .mockResolvedValueOnce(jsonResponse([reservationDto]))
        .mockResolvedValueOnce(jsonResponse({ id: 44 }));
    await expect(canCancelReservation('token-123', '12')).resolves.toBe(true);

    global.fetch.mockRejectedValueOnce(new Error('network'));
    await expect(canCancelReservation('token-123', '12')).resolves.toBe(false);
  });

  test('checkReservationStatus returns reservation data, wish booked state or fallback values', async () => {
    global.fetch
        .mockResolvedValueOnce(jsonResponse([reservationDto]))
        .mockResolvedValueOnce(jsonResponse({ id: 44 }))
        .mockResolvedValueOnce(jsonResponse([reservationDto]));

    await expect(checkReservationStatus('token-123', '5', '12')).resolves.toMatchObject({
      is_booked: true,
      reservation: expect.objectContaining({ wish_wishlist_id: '12' })
    });

    global.fetch
        .mockResolvedValueOnce(jsonResponse([]))
        .mockResolvedValueOnce(jsonResponse({ is_booked: true }));
    await expect(checkReservationStatus('token-123', '5', '12')).resolves.toEqual({
      is_booked: true,
      reservation: null
    });

    global.fetch
        .mockResolvedValueOnce(jsonResponse([]))
        .mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(checkReservationStatus('token-123', '5', '12')).resolves.toEqual({
      is_booked: false,
      reservation: null
    });

    global.fetch.mockRejectedValueOnce(new Error('network'));
    await expect(checkReservationStatus('token-123', '5', '12')).resolves.toEqual({
      is_booked: false,
      reservation: null
    });
  });

  test('getReservationUserInfo returns null for empty states and maps user info when available', async () => {
    global.fetch.mockResolvedValueOnce(jsonResponse([]));
    await expect(getReservationUserInfo('token-123', '12')).resolves.toBeNull();

    global.fetch
        .mockResolvedValueOnce(jsonResponse([reservationDto]))
        .mockResolvedValueOnce(jsonResponse({ id: 44 }))
        .mockResolvedValueOnce(jsonResponse([]));
    await expect(getReservationUserInfo('token-123', '12')).resolves.toBeNull();

    global.fetch
        .mockResolvedValueOnce(jsonResponse([reservationDto]))
        .mockResolvedValueOnce(jsonResponse({ id: 44 }))
        .mockResolvedValueOnce(jsonResponse([reservationDto]))
        .mockResolvedValueOnce(jsonResponse({ name: 'Alice', photo: 'alice.png' }));
    await expect(getReservationUserInfo('token-123', '12')).resolves.toEqual({
      id: '44',
      name: 'Alice',
      photo: 'alice.png'
    });

    global.fetch
        .mockResolvedValueOnce(jsonResponse([reservationDto]))
        .mockResolvedValueOnce(jsonResponse({ id: 44 }))
        .mockResolvedValueOnce(jsonResponse([reservationDto]))
        .mockResolvedValueOnce(jsonResponse({}, false, 404));
    await expect(getReservationUserInfo('token-123', '12')).resolves.toBeNull();

    global.fetch.mockRejectedValueOnce(new Error('network'));
    await expect(getReservationUserInfo('token-123', '12')).resolves.toBeNull();
  });

  test('getReservationsByWishId filters all reservations by wish-wishlist connections', async () => {
    global.fetch
        .mockResolvedValueOnce(jsonResponse([{ id: 12 }, { id: 99 }]))
        .mockResolvedValueOnce(
            jsonResponse([
              reservationDto,
              { ...reservationDto, wish_wishlist_id: 100, reserved_by_id: 45 }
            ])
        );

    const result = await getReservationsByWishId('token-123', '5');

    expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/wish_wishlist/wish/5',
        expect.objectContaining({ headers: { Authorization: 'Bearer token-123' } })
    );
    expect(result).toHaveLength(1);
    expect(result[0].wish_wishlist_id).toBe('12');

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 404));
    await expect(getReservationsByWishId('token-123', '5')).resolves.toEqual([]);

    global.fetch.mockRejectedValueOnce(new Error('network'));
    await expect(getReservationsByWishId('token-123', '5')).resolves.toEqual([]);
  });

  test('hasActiveReservations returns true when at least one reservation exists and false on errors', async () => {
    global.fetch.mockResolvedValueOnce(jsonResponse([reservationDto]));
    await expect(hasActiveReservations('token-123')).resolves.toBe(true);

    global.fetch.mockResolvedValueOnce(jsonResponse([], true, 200));
    await expect(hasActiveReservations('token-123')).resolves.toBe(false);

    global.fetch.mockRejectedValueOnce(new Error('network'));
    await expect(hasActiveReservations('token-123')).resolves.toBe(false);
  });

  test('additional coverage for createReservation 400 error branch', async () => {
    global.fetch.mockResolvedValueOnce(jsonResponse({ detail: 'already booked' }, false, 400));

    await expect(createReservation('token-123', '12')).rejects.toThrow(
        'Не удалось создать резервацию. Возможно, желание уже зарезервировано.'
    );
  });

  test('additional coverage for deleteReservation success and error branches', async () => {
    reservationsStore.set([
      { wish_wishlist_id: '12', reserved_by_id: '44', created_at: new Date('2026-01-01T00:00:00.000Z') },
      { wish_wishlist_id: '99', reserved_by_id: '45', created_at: new Date('2026-01-02T00:00:00.000Z') }
    ]);

    global.fetch.mockResolvedValueOnce(jsonResponse({}, true, 204));

    await expect(deleteReservation('token-123', '12')).resolves.toBeUndefined();
    expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/reservations/delete/?wish_wishlist_id=12',
        expect.objectContaining({ method: 'DELETE' })
    );
    expect(get(reservationsStore)).toEqual([
      { wish_wishlist_id: '99', reserved_by_id: '45', created_at: new Date('2026-01-02T00:00:00.000Z') }
    ]);

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 404));
    await expect(deleteReservation('token-123', '12')).rejects.toThrow('Резервация не найдена');

    global.fetch.mockResolvedValueOnce(jsonResponse({}, false, 500));
    await expect(deleteReservation('token-123', '12')).rejects.toThrow('Ошибка удаления резервации');
  });

  test('additional coverage for getReservationByWishWishlistId branches', async () => {
    global.fetch.mockResolvedValueOnce(jsonResponse([reservationDto]));
    await expect(getReservationByWishWishlistId('token-123', '12')).resolves.toEqual({
      isReserved: true,
      reservedByUserId: '44'
    });

    global.fetch.mockResolvedValueOnce(jsonResponse([reservationDto]));
    await expect(getReservationByWishWishlistId('token-123', '404')).resolves.toEqual({
      isReserved: false,
      reservedByUserId: null
    });

    global.fetch.mockRejectedValueOnce(new Error('network'));
    await expect(getReservationByWishWishlistId('token-123', '12')).resolves.toEqual({
      isReserved: false,
      reservedByUserId: null
    });
  });

  test('additional coverage for reservation helper fallback branches', async () => {
    global.fetch
        .mockResolvedValueOnce(jsonResponse([reservationDto]))
        .mockResolvedValueOnce(jsonResponse({}, false, 401));
    await expect(checkWishReservation('token-123', '12')).resolves.toEqual({
      isReserved: true,
      reservedByCurrentUser: false
    });

    global.fetch.mockRejectedValueOnce(new Error('network'));
    await expect(getReservationsForWishWishlist('token-123', '12')).resolves.toEqual([]);

    global.fetch.mockResolvedValueOnce(jsonResponse({}, true, 204));
    await expect(toggleReservation('token-123', '12', false)).resolves.toBe(false);

    global.fetch.mockRejectedValueOnce(new Error('network'));
    await expect(toggleReservation('token-123', '12', false)).rejects.toThrow('network');

    global.fetch.mockRejectedValueOnce(new Error('network'));
    await expect(canCancelReservation('token-123', '12')).resolves.toBe(false);

    global.fetch.mockRejectedValueOnce(new Error('network'));
    await expect(getReservationUserInfo('token-123', '12')).resolves.toBeNull();
  });
});
