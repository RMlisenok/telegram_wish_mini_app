import { writable } from 'svelte/store';

export interface WishWishlistConnection {
    id: string;
    wish_id: string;
    wishlist_id: string;
    is_pinned?: boolean;
    order_position?: number;
    created_at: Date;
    updated_at: Date;
}

export interface WishWishlistCreateData {
    wish_id: number;
    wishlist_id: number;
    is_pinned?: boolean;
    order_position?: number;
}

export interface WishWishlistUpdateData {
    is_pinned?: boolean;
    order_position?: number;
}

export interface WishInWishlist {
    id: string;
    name: string;
    photo?: string;
    url_gift?: string;
    price?: number;
    currency: 'RUB' | 'BYN' | 'USD' | 'EUR' | 'UAH' | 'KZT' | null;
    description?: string;
    is_booked: boolean;
    status_is_finished: boolean;
    created_at: Date;
    updated_at: Date;
    
    connection_id: string;
    is_pinned: boolean;
    order_position: number;
    added_at: Date;
}

export const wishWishlistsStore = writable<WishInWishlist[]>([]);

// Получение списка желаний из конкретного вишлиста
export async function getWishesFromWishlist(
    token: string, 
    wishlistId: string, 
    limit: number = 50
): Promise<WishInWishlist[]> {
    try {
        const response = await fetch(`/api/v1/wishlists/${wishlistId}/wishes?limit=${limit}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Вишлист не найден');
            }
            throw new Error('Ошибка загрузки желаний из вишлиста');
        }
        
        const data = await response.json();
        
        // Преобразование данных
        return data.map((item: any) => ({
            // Данные желания
            id: item.id.toString(),
            name: item.name,
            photo: item.photo,
            url_gift: item.url_gift,
            price: item.price,
            currency: item.currency,
            description: item.description,
            is_booked: item.is_booked,
            status_is_finished: item.status_is_finished,
            created_at: new Date(item.created_at),
            updated_at: new Date(item.updated_at),
            
            // Данные связи
            connection_id: item.connection_id.toString(),
            is_pinned: item.is_pinned,
            order_position: item.order_position,
            added_at: new Date(item.added_at)
        }));
    } catch (error) {
        console.error('Ошибка загрузки желаний из вишлиста:', error);
        throw error;
    }
}

// Добавление желания в вишлист
export async function addWishToWishlist(
    token: string, 
    wishlistId: string, 
    wishId: string,
    options?: {
        is_pinned?: boolean;
        order_position?: number;
    }
): Promise<WishWishlistConnection> {
    try {
        const connectData: WishWishlistCreateData = {
            wish_id: parseInt(wishId),
            wishlist_id: parseInt(wishlistId),
            ...(options?.is_pinned !== undefined && { is_pinned: options.is_pinned }),
            ...(options?.order_position !== undefined && { order_position: options.order_position })
        };
        
        const response = await fetch(`/api/v1/wishlists/${wishlistId}/wishes`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(connectData)
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Ошибка сервера:', errorText);
            
            if (response.status === 400) {
                throw new Error('Не удалось добавить желание в вишлист. Возможно, желание уже добавлено или не существует.');
            }
            throw new Error(`Ошибка добавления желания в вишлист: ${response.status}`);
        }
        
        const data = await response.json();
        return {
            id: data.id.toString(),
            wish_id: data.wish_id.toString(),
            wishlist_id: data.wishlist_id.toString(),
            is_pinned: data.is_pinned,
            order_position: data.order_position,
            created_at: new Date(data.created_at),
            updated_at: new Date(data.updated_at)
        };
    } catch (error) {
        console.error('Ошибка добавления желания в вишлист:', error);
        throw error;
    }
}

// Обновление связи желание-вишлист
export async function updateWishWishlistConnection(
    token: string,
    connectionId: string,
    updateData: WishWishlistUpdateData
): Promise<WishWishlistConnection> {
    try {
        const response = await fetch(`/api/v1/wishlists/connections/${connectionId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updateData)
        });
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Связь не найдена');
            }
            throw new Error('Ошибка обновления связи');
        }
        
        const data = await response.json();
        return {
            id: data.id.toString(),
            wish_id: data.wish_id.toString(),
            wishlist_id: data.wishlist_id.toString(),
            is_pinned: data.is_pinned,
            order_position: data.order_position,
            created_at: new Date(data.created_at),
            updated_at: new Date(data.updated_at)
        };
    } catch (error) {
        console.error('Ошибка обновления связи:', error);
        throw error;
    }
}

// Удаление желания из вишлиста
export async function removeWishFromWishlist(
    token: string,
    wishlistId: string,
    wishId: string
): Promise<void> {
    try {
        const response = await fetch(`/api/v1/wishlists/${wishlistId}/wishes/${wishId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Желание не найдено в вишлисте');
            }
            throw new Error('Ошибка удаления желания из вишлиста');
        }
        
    } catch (error) {
        console.error('Ошибка удаления желания из вишлиста:', error);
        throw error;
    }
}

// Закрепление/открепление желания в вишлисте
export async function toggleWishPinInWishlist(
    token: string,
    connectionId: string,
    pinned: boolean
): Promise<WishWishlistConnection> {
    return await updateWishWishlistConnection(token, connectionId, {
        is_pinned: pinned
    });
}

// Массовое добавление желаний в вишлист
export async function addMultipleWishesToWishlist(
    token: string,
    wishlistId: string,
    wishIds: string[],
    options?: {
        is_pinned?: boolean;
        order_position?: number;
    }
): Promise<WishWishlistConnection[]> {
    const results: WishWishlistConnection[] = [];
    
    // for (const wishId of wishIds) {
    //     try {
    //         const result = await addWishToWishlist(token, wishlistId, wishId, options);
    //         results.push(result);
    //     } catch (error) {
    //         console.error(`Ошибка добавления желания ${wishId}:`, error);
    //     }
    // }
    
    const promises = wishIds.map(async (wishId) => {
        try {
            const result = await addWishToWishlist(token, wishlistId, wishId, options);
            return result;
        } catch (error) {
            console.error(`Ошибка добавления желания ${wishId}:`, error);
            throw error;
        }
    });
    
    try {
        const settledResults = await Promise.allSettled(promises);
        
        settledResults.forEach((result, index) => {
            if (result.status === 'fulfilled') {
                results.push(result.value);
            } else {
                console.error(`Не удалось добавить желание ${wishIds[index]}:`, result.reason);
            }
        });
        
        return results;
    } catch (error) {
        console.error('Ошибка при массовом добавлении:', error);
        throw error;
    }

    return results;
}
