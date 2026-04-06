import { writable } from 'svelte/store';

export interface WishReservation {
    wish_wishlist_id: string; // ID связи wish_wishlist
    reserved_by_id: string;   // ID пользователя, который зарезервировал
    created_at: Date;         // Дата создания резервации
}

export interface CreateReservationData {
    wish_wishlist_id: number; // ID связи wish_wishlist для резервирования
}

export const reservationsStore = writable<WishReservation[]>([]);

// Получить резервации текущего пользователя
export async function getUserReservations(
    token: string,
    limit: number = 10
): Promise<WishReservation[]> {
    try {
        const response = await fetch(`/api/v1/reservations/?limit=${limit}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Резервации не найдены');
            }
            throw new Error('Ошибка загрузки резерваций');
        }
        
        const data = await response.json();
        console.log('Получены резервации:', data);
        
        const transformedReservations = data.map((reservation: any) => ({
            wish_wishlist_id: reservation.wish_wishlist_id.toString(),
            reserved_by_id: reservation.reserved_by_id.toString(),
            created_at: new Date(reservation.created_at)
        }));
        
        reservationsStore.set(transformedReservations);
        return transformedReservations;
    } catch (error) {
        console.error('Ошибка загрузки резерваций:', error);
        reservationsStore.set([]);
        throw error;
    }
}

// Создать резервацию желания
export async function createReservation(
    token: string,
    wish_wishlist_id: string
): Promise<WishReservation> {
    try {
        const response = await fetch('/api/v1/reservations/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                wish_wishlist_id: parseInt(wish_wishlist_id)
            })
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Ошибка сервера при создании резервации:', errorText);
            
            if (response.status === 400) {
                throw new Error('Не удалось создать резервацию. Возможно, желание уже зарезервировано.');
            }
            throw new Error(`Ошибка создания резервации: ${response.status}`);
        }
        
        const data = await response.json();
        
        const newReservation: WishReservation = {
            wish_wishlist_id: data.wish_wishlist_id.toString(),
            reserved_by_id: data.reserved_by_id.toString(),
            created_at: new Date(data.created_at)
        };
        
        // Добавляем в store
        reservationsStore.update(reservations => [...reservations, newReservation]);
        
        return newReservation;
    } catch (error) {
        console.error('Ошибка создания резервации:', error);
        throw error;
    }
}

// Удалить резервацию
export async function deleteReservation(
    token: string,
    wish_wishlist_id: string
): Promise<void> {
    try {
        const response = await fetch(`/api/v1/reservations/delete/?wish_wishlist_id=${wish_wishlist_id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Резервация не найдена');
            }
            throw new Error('Ошибка удаления резервации');
        }
        
        // Удаляем резервацию из store
        reservationsStore.update(reservations => 
            reservations.filter(res => res.wish_wishlist_id !== wish_wishlist_id)
        );
        
        console.log('Резервация успешно удалена');
    } catch (error) {
        console.error('Ошибка удаления резервации:', error);
        throw error;
    }
}

// Проверить, кто забронировал желание
export async function getReservationByWishWishlistId(
    token: string,
    wish_wishlist_id: string
): Promise<{isReserved: boolean; reservedByUserId: string | null}> {
    try {
        const reservations = await getUserReservations(token, 100);
        
        const reservation = reservations.find(
            res => res.wish_wishlist_id === wish_wishlist_id
        );
        
        if (reservation) {
            return {
                isReserved: true,
                reservedByUserId: reservation.reserved_by_id
            };
        }
        
        return {
            isReserved: false,
            reservedByUserId: null
        };
    } catch (error) {
        console.error('Ошибка проверки резервации:', error);
        return {
            isReserved: false,
            reservedByUserId: null
        };
    }
}

// Проверить, зарезервировано ли желание
export async function checkWishReservation(
    token: string,
    wish_wishlist_id: string
): Promise<{ isReserved: boolean; reservedByCurrentUser: boolean }> {
    try {
        // Получаем все резервации
        const reservations = await getUserReservations(token, 100);
        
        // Проверяем, есть ли резервация для данного wish_wishlist_id
        const reservation = reservations.find(res => res.wish_wishlist_id === wish_wishlist_id);
        
        if (!reservation) {
            return { isReserved: false, reservedByCurrentUser: false };
        }
        
        // Получаем ID текущего пользователя
        const userResponse = await fetch('/api/v1/users/me', {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!userResponse.ok) {
            return { isReserved: true, reservedByCurrentUser: false };
        }
        
        const userData = await userResponse.json();
        const currentUserId = userData.id.toString();
        
        return {
            isReserved: true,
            reservedByCurrentUser: reservation.reserved_by_id === currentUserId
        };
    } catch (error) {
        console.error('Ошибка проверки резервации:', error);
        return { isReserved: false, reservedByCurrentUser: false };
    }
}

// Получить резервации для конкретного желания в вишлисте
export async function getReservationsForWishWishlist(
    token: string,
    wish_wishlist_id: string,
    limit: number = 10
): Promise<WishReservation[]> {
    try {
        // Загрузка всех резерваций пользователя        
        const allReservations = await getUserReservations(token, 100);
        // Поиск резерваций для данного wish_wishlist_id
        const filtered = allReservations.filter(
            reservation => reservation.wish_wishlist_id === wish_wishlist_id
        );
        
        return filtered.slice(0, limit);
    } catch (error) {
        console.error('Ошибка получения резерваций для wish_wishlist:', error);
        return [];
    }
}

// Тоггл резервации (создать или удалить)
export async function toggleReservation(
    token: string,
    wish_wishlist_id: string,
    isReserved: boolean
): Promise<boolean> {
    try {
        if (isReserved) {
            await createReservation(token, wish_wishlist_id);
            return true;
        } else {
            await deleteReservation(token, wish_wishlist_id);
            return false;
        }
    } catch (error) {
        console.error('Ошибка переключения резервации:', error);
        throw error;
    }
}

// Проверить, может ли пользователь отменить резервацию
export async function canCancelReservation(
    token: string,
    wish_wishlist_id: string
): Promise<boolean> {
    try {
        const checkResult = await checkWishReservation(token, wish_wishlist_id);
        return checkResult.reservedByCurrentUser;
    } catch (error) {
        console.error('Ошибка проверки возможности отмены:', error);
        return false;
    }
}

// Проверить статус резервации и обновить is_booked в wish
export async function checkReservationStatus(
    token: string,
    wish_id: string,
    wish_wishlist_id: string
): Promise<{ is_booked: boolean; reservation: WishReservation | null }> {
    try {
        // Проверяем резервацию
        const reservationCheck = await checkWishReservation(token, wish_wishlist_id);
        
        if (reservationCheck.isReserved) {
            // Если есть резервация, получаем ее данные
            const reservations = await getReservationsForWishWishlist(token, wish_wishlist_id, 1);
            return {
                is_booked: true,
                reservation: reservations[0] || null
            };
        } else {
            // Если нет резервации, возможно нужно обновить статус wish
            const wishResponse = await fetch(`/api/v1/wishes/${wish_id}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (wishResponse.ok) {
                const wishData = await wishResponse.json();
                return {
                    is_booked: wishData.is_booked || false,
                    reservation: null
                };
            }
        }
        
        return { is_booked: false, reservation: null };
    } catch (error) {
        console.error('Ошибка проверки статуса резервации:', error);
        return { is_booked: false, reservation: null };
    }
}

// Получить информацию о пользователе, который зарезервировал
export async function getReservationUserInfo(
    token: string,
    wish_wishlist_id: string
): Promise<{ id: string; name: string; photo: string | null } | null> {
    try {
        const reservationCheck = await checkWishReservation(token, wish_wishlist_id);
        
        if (!reservationCheck.isReserved) {
            return null;
        }
        
        // Получаем резервацию
        const reservations = await getReservationsForWishWishlist(token, wish_wishlist_id, 1);
        if (reservations.length === 0) {
            return null;
        }
        
        const reservedByUserId = reservations[0].reserved_by_id;
        
        // Получаем информацию о пользователе
        const userResponse = await fetch(`/api/v1/users/${reservedByUserId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!userResponse.ok) {
            return null;
        }
        
        const userData = await userResponse.json();
        
        return {
            id: reservedByUserId,
            name: userData.name || 'Пользователь',
            photo: userData.photo || null
        };
    } catch (error) {
        console.error('Ошибка получения информации о пользователе:', error);
        return null;
    }
}

// Получить резервации по wish_id (через wish_wishlist связь)
export async function getReservationsByWishId(
    token: string,
    wish_id: string
): Promise<WishReservation[]> {
    try {
        // Сначала получаем все wish_wishlist связи для этого wish
        const response = await fetch(`/api/v1/wish_wishlist/wish/${wish_id}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            return [];
        }
        
        const connections = await response.json();
        const wishWishlistIds = connections.map((conn: any) => conn.id.toString());
        
        // Получаем все резервации и фильтруем
        const allReservations = await getUserReservations(token, 100);
        const filtered = allReservations.filter(reservation => 
            wishWishlistIds.includes(reservation.wish_wishlist_id)
        );
        
        return filtered;
    } catch (error) {
        console.error('Ошибка получения резерваций по wish_id:', error);
        return [];
    }
}

// Проверить, есть ли резервации у пользователя
export async function hasActiveReservations(
    token: string
): Promise<boolean> {
    try {
        const reservations = await getUserReservations(token, 1);
        return reservations.length > 0;
    } catch (error) {
        console.error('Ошибка проверки активных резерваций:', error);
        return false;
    }
}